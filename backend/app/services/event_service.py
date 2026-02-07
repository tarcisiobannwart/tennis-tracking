"""
Event Service
Detecta e classifica eventos automáticos da partida
"""

from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from enum import Enum
import asyncio
import uuid
import structlog

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import GameEvent, EventType as ModelEventType
from app.schemas.game_control import (
    PointTypeEnum,
    GameStateSnapshot
)

logger = structlog.get_logger(__name__)


class EventPriority(str, Enum):
    """
    Prioridade de eventos

    Critérios de aceite TT-45:
    - [x] EventPriority: LOW, NORMAL, HIGH, CRITICAL
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventType:
    """
    Tipos de eventos detectáveis

    Critérios de aceite TT-44:
    - [x] 17 EventType definidos
    """
    # Eventos de ponto
    ACE = "ace"
    DOUBLE_FAULT = "double_fault"
    WINNER = "winner"
    UNFORCED_ERROR = "unforced_error"
    FORCED_ERROR = "forced_error"

    # Situações críticas
    BREAK_POINT = "break_point"
    SET_POINT = "set_point"
    MATCH_POINT = "match_point"
    DEUCE = "deuce"
    ADVANTAGE = "advantage"

    # Tiebreak
    TIEBREAK_START = "tiebreak_start"

    # Conclusões
    GAME_WON = "game_won"
    SET_WON = "set_won"
    MATCH_WON = "match_won"

    # Interrupções
    CHALLENGE = "challenge"
    MEDICAL_TIMEOUT = "medical_timeout"
    COACHING_TIMEOUT = "coaching_timeout"


class EventService:
    """
    Service para detecção e classificação de eventos

    Critérios de aceite TT-44:
    - [x] analyze_point() classifica ponto em evento automaticamente
    - [x] _detect_situational_events() para break point, deuce, advantage

    Critérios de aceite TT-45:
    - [x] Sistema de prioridades (critical, high, medium, low)
    - [x] register_event_callback() por EventType
    - [x] Tratamento de erros em callbacks
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        # Callbacks por match_id -> event_type -> priority -> [callbacks]
        self._callbacks: Dict[str, Dict[str, Dict[str, List[Callable]]]] = {}

    async def analyze_point(
        self,
        match_id: str,
        point_type: PointTypeEnum,
        winner_player_id: str,
        state_before: GameStateSnapshot,
        state_after: Optional[GameStateSnapshot] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Analisa um ponto e classifica em eventos

        Critérios de aceite TT-44:
        - [x] analyze_point() classifica ponto em evento automaticamente

        Args:
            match_id: ID da partida
            point_type: Tipo do ponto
            winner_player_id: ID do jogador que ganhou o ponto
            state_before: Estado antes do ponto
            state_after: Estado depois do ponto (opcional)
            metadata: Metadados adicionais

        Returns:
            Lista de tipos de eventos detectados
        """
        events_detected = []

        try:
            # Eventos diretos do tipo de ponto
            if point_type == PointTypeEnum.ACE:
                events_detected.append(EventType.ACE)
            elif point_type == PointTypeEnum.DOUBLE_FAULT:
                events_detected.append(EventType.DOUBLE_FAULT)
            elif point_type == PointTypeEnum.WINNER:
                events_detected.append(EventType.WINNER)
            elif point_type == PointTypeEnum.UNFORCED_ERROR:
                events_detected.append(EventType.UNFORCED_ERROR)
            elif point_type == PointTypeEnum.FORCED_ERROR:
                events_detected.append(EventType.FORCED_ERROR)

            # Detectar eventos situacionais
            situational_events = await self._detect_situational_events(
                match_id=match_id,
                state_before=state_before,
                state_after=state_after
            )
            events_detected.extend(situational_events)

            # Salvar eventos detectados
            for event_type in events_detected:
                await self._save_event(
                    match_id=match_id,
                    event_type=event_type,
                    player_id=winner_player_id,
                    state_before=state_before,
                    metadata=metadata or {}
                )

            logger.info(
                "Point analyzed",
                match_id=match_id,
                point_type=point_type.value,
                events_detected=events_detected
            )

            return events_detected

        except Exception as e:
            logger.error("Error analyzing point", match_id=match_id, error=str(e))
            return []

    async def _detect_situational_events(
        self,
        match_id: str,
        state_before: GameStateSnapshot,
        state_after: Optional[GameStateSnapshot] = None
    ) -> List[str]:
        """
        Detecta eventos situacionais (break point, deuce, advantage, etc)

        Critérios de aceite TT-44:
        - [x] _detect_situational_events() para break point, deuce, advantage

        Args:
            match_id: ID da partida
            state_before: Estado antes do ponto
            state_after: Estado depois do ponto (opcional)

        Returns:
            Lista de eventos situacionais detectados
        """
        events = []

        try:
            # Detectar deuce (40-40)
            if state_before.player1_points >= 40 and state_before.player2_points >= 40:
                if state_before.player1_points == state_before.player2_points:
                    events.append(EventType.DEUCE)

            # Detectar advantage (mais de 40 e diferença de 1)
            if state_before.player1_points > 40 or state_before.player2_points > 40:
                if abs(state_before.player1_points - state_before.player2_points) == 1:
                    events.append(EventType.ADVANTAGE)

            # Detectar break point (usando lógica do game_control_service)
            # Buscar match para verificar servidor
            from app.models.match import Match
            stmt = select(Match).where(Match.id == match_id)
            result = await self.db.execute(stmt)
            match = result.scalar_one_or_none()

            if match:
                game_state = match.game_state or {}
                server_player_id = game_state.get("server_player_id", "")
                player1_id = str(match.player1_id)
                player2_id = str(match.player2_id)

                # Verificar se é break point
                is_break_pt = self._is_break_point(
                    server_player_id=server_player_id,
                    player1_points=state_before.player1_points,
                    player2_points=state_before.player2_points,
                    player1_id=player1_id,
                    player2_id=player2_id
                )

                if is_break_pt:
                    events.append(EventType.BREAK_POINT)

            # Detectar set point
            is_set_pt, _ = self._is_set_point(
                player1_games=state_before.player1_games,
                player2_games=state_before.player2_games,
                player1_points=state_before.player1_points,
                player2_points=state_before.player2_points
            )

            if is_set_pt:
                events.append(EventType.SET_POINT)

            # Detectar match point (se state_after disponível)
            if state_after:
                # Detectar game won
                if state_after.current_game > state_before.current_game:
                    events.append(EventType.GAME_WON)

                # Detectar set won
                if state_after.current_set > state_before.current_set:
                    events.append(EventType.SET_WON)

                # Detectar match won (status completo)
                stmt = select(Match).where(Match.id == match_id)
                result = await self.db.execute(stmt)
                match = result.scalar_one_or_none()

                if match and match.status == "completed":
                    events.append(EventType.MATCH_WON)

            return events

        except Exception as e:
            logger.error("Error detecting situational events", match_id=match_id, error=str(e))
            return []

    def _is_break_point(
        self,
        server_player_id: str,
        player1_points: int,
        player2_points: int,
        player1_id: str,
        player2_id: str
    ) -> bool:
        """
        Verifica se é break point
        (Lógica copiada do game_control_service para consistência)
        """
        receiver_id = player2_id if server_player_id == player1_id else player1_id

        if server_player_id == player1_id:
            server_points = player1_points
            receiver_points = player2_points
        else:
            server_points = player2_points
            receiver_points = player1_points

        # Break point: receiver pode ganhar o game
        if receiver_points >= 40 and server_points < 40:
            return True

        if receiver_points >= 40 and server_points >= 40 and receiver_points > server_points:
            return True

        return False

    def _is_set_point(
        self,
        player1_games: int,
        player2_games: int,
        player1_points: int,
        player2_points: int,
        is_tiebreak: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Verifica se é set point
        """
        if is_tiebreak:
            if player1_points >= 6 and player1_points >= player2_points + 1:
                return (True, "player1")
            if player2_points >= 6 and player2_points >= player1_points + 1:
                return (True, "player2")
            return (False, None)

        # Player 1 pode fechar set
        if player1_games >= 5 and player1_points >= 40:
            if player1_points >= 40 and player2_points < 40:
                return (True, "player1")
            if player1_points > player2_points and player1_points >= 40 and player2_points >= 40:
                return (True, "player1")

        # Player 2 pode fechar set
        if player2_games >= 5 and player2_points >= 40:
            if player2_points >= 40 and player1_points < 40:
                return (True, "player2")
            if player2_points > player1_points and player2_points >= 40 and player1_points >= 40:
                return (True, "player2")

        return (False, None)

    async def _save_event(
        self,
        match_id: str,
        event_type: str,
        player_id: str,
        state_before: GameStateSnapshot,
        metadata: Dict[str, Any]
    ):
        """Salva um evento no banco de dados"""
        try:
            # Mapear event_type para ModelEventType compatível
            # Se o event_type não estiver no enum, usar POINT_SCORED como fallback
            try:
                model_event_type = ModelEventType[event_type.upper()]
            except (KeyError, AttributeError):
                model_event_type = ModelEventType.POINT_SCORED

            event = GameEvent(
                id=uuid.uuid4(),
                match_id=match_id,
                event_type=model_event_type.value,
                player_id=player_id,
                event_data={
                    "state_before": state_before.dict() if state_before else None,
                    **metadata
                },
                timestamp=datetime.utcnow(),
            )

            self.db.add(event)
            await self.db.flush()

        except Exception as e:
            logger.error("Error saving event", match_id=match_id, event_type=event_type, error=str(e))

    async def register_challenge(
        self,
        match_id: str,
        player_id: str,
        call_challenged: str,
        outcome: str
    ) -> bool:
        """
        Registra um challenge (pedido de revisão)

        Args:
            match_id: ID da partida
            player_id: ID do jogador que pediu challenge
            call_challenged: Chamada questionada (in/out)
            outcome: Resultado (successful/unsuccessful)

        Returns:
            True se registrado com sucesso
        """
        try:
            event = GameEvent(
                id=uuid.uuid4(),
                match_id=match_id,
                event_type=ModelEventType.CHALLENGE.value,
                player_id=player_id,
                event_data={
                    "call_challenged": call_challenged,
                    "outcome": outcome
                },
                timestamp=datetime.utcnow(),
            )

            self.db.add(event)
            await self.db.flush()

            logger.info("Challenge registered", match_id=match_id, player_id=player_id)
            return True

        except Exception as e:
            logger.error("Error registering challenge", match_id=match_id, error=str(e))
            return False

    async def register_timeout(
        self,
        match_id: str,
        timeout_type: str,
        player_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Registra um timeout (médico ou coaching)

        Args:
            match_id: ID da partida
            timeout_type: Tipo (medical_timeout/coaching_timeout)
            player_id: ID do jogador (opcional)
            reason: Razão do timeout (opcional)

        Returns:
            True se registrado com sucesso
        """
        try:
            if timeout_type not in [EventType.MEDICAL_TIMEOUT, EventType.COACHING_TIMEOUT]:
                logger.warning("Invalid timeout type", timeout_type=timeout_type)
                return False

            event = GameEvent(
                id=uuid.uuid4(),
                match_id=match_id,
                event_type=ModelEventType.ERROR.value,  # Using ERROR as fallback
                player_id=player_id or "",
                event_data={"timeout_type": timeout_type, "reason": reason},
                timestamp=datetime.utcnow(),
            )

            self.db.add(event)
            await self.db.flush()

            logger.info("Timeout registered", match_id=match_id, timeout_type=timeout_type)
            return True

        except Exception as e:
            logger.error("Error registering timeout", match_id=match_id, error=str(e))
            return False

    async def get_events_by_type(
        self,
        match_id: str,
        event_type: str
    ) -> List[Dict[str, Any]]:
        """
        Busca eventos por tipo

        Args:
            match_id: ID da partida
            event_type: Tipo de evento

        Returns:
            Lista de eventos
        """
        try:
            stmt = select(GameEvent).where(
                and_(
                    GameEvent.match_id == match_id,
                    GameEvent.event_type == event_type
                )
            ).order_by(GameEvent.timestamp)

            result = await self.db.execute(stmt)
            events = result.scalars().all()

            return [
                {
                    "_id": str(event.id),
                    "match_id": event.match_id,
                    "event_type": event.event_type,
                    "player_id": event.player_id,
                    "timestamp": event.timestamp,
                    "event_data": event.event_data,
                }
                for event in events
            ]

        except Exception as e:
            logger.error("Error getting events by type", match_id=match_id, error=str(e))
            return []

    def register_event_callback(
        self,
        match_id: str,
        event_type: str,
        callback: Callable,
        priority: EventPriority = EventPriority.NORMAL
    ) -> bool:
        """
        Registra um callback para um tipo de evento com prioridade

        Critérios de aceite TT-45:
        - [x] register_event_callback() por EventType
        - [x] Permitir filtrar por prioridade

        Args:
            match_id: ID da partida
            event_type: Tipo de evento
            callback: Função callback
            priority: Prioridade do evento (default: NORMAL)

        Returns:
            True se registrado com sucesso
        """
        try:
            if match_id not in self._callbacks:
                self._callbacks[match_id] = {}

            if event_type not in self._callbacks[match_id]:
                self._callbacks[match_id][event_type] = {}

            if priority.value not in self._callbacks[match_id][event_type]:
                self._callbacks[match_id][event_type][priority.value] = []

            self._callbacks[match_id][event_type][priority.value].append(callback)

            logger.info(
                "Event callback registered",
                match_id=match_id,
                event_type=event_type,
                priority=priority.value
            )

            return True

        except Exception as e:
            logger.error(
                "Error registering callback",
                match_id=match_id,
                event_type=event_type,
                error=str(e)
            )
            return False

    def _get_event_priority(self, event_type: str) -> EventPriority:
        """
        Determina a prioridade automática de um evento

        Critérios de aceite TT-45:
        - [x] _get_event_priority() automática por tipo

        Args:
            event_type: Tipo de evento

        Returns:
            EventPriority correspondente
        """
        # CRITICAL: eventos que finalizam match ou set
        if event_type in [EventType.MATCH_WON, EventType.SET_WON]:
            return EventPriority.CRITICAL

        # HIGH: situações críticas
        if event_type in [
            EventType.MATCH_POINT,
            EventType.SET_POINT,
            EventType.BREAK_POINT,
            EventType.MEDICAL_TIMEOUT
        ]:
            return EventPriority.HIGH

        # NORMAL: eventos de jogo
        if event_type in [
            EventType.ACE,
            EventType.WINNER,
            EventType.DOUBLE_FAULT,
            EventType.GAME_WON,
            EventType.DEUCE,
            EventType.ADVANTAGE,
            EventType.CHALLENGE
        ]:
            return EventPriority.NORMAL

        # LOW: outros eventos
        return EventPriority.LOW

    async def _emit_event(
        self,
        match_id: str,
        event_type: str,
        player_id: Optional[str] = None,
        state_before: Optional[GameStateSnapshot] = None,
        metadata: Optional[Dict[str, Any]] = None,
        min_priority: Optional[EventPriority] = None
    ):
        """
        Emite um evento para callbacks registrados

        Critérios de aceite TT-45:
        - [x] Executar callbacks filtrados por prioridade
        - [x] Tratamento de erros em callbacks

        Args:
            match_id: ID da partida
            event_type: Tipo de evento
            player_id: ID do jogador (opcional)
            state_before: Estado antes do evento (opcional)
            metadata: Metadados (opcional)
            min_priority: Prioridade mínima para executar callbacks (opcional)
        """
        event_data = {
            "match_id": match_id,
            "event_type": event_type,
            "player_id": player_id,
            "timestamp": datetime.utcnow(),
            "state_before": state_before.dict() if state_before else None,
            "metadata": metadata or {}
        }

        # Determinar prioridade do evento
        event_priority = self._get_event_priority(event_type)

        # Executar callbacks (com tratamento de erros)
        if match_id in self._callbacks:
            if event_type in self._callbacks[match_id]:
                # Ordem de execução: CRITICAL -> HIGH -> NORMAL -> LOW
                priority_order = [
                    EventPriority.CRITICAL,
                    EventPriority.HIGH,
                    EventPriority.NORMAL,
                    EventPriority.LOW
                ]

                for priority in priority_order:
                    # Se min_priority definido, pular prioridades menores
                    if min_priority and self._priority_value(priority) < self._priority_value(min_priority):
                        continue

                    callbacks = self._callbacks[match_id][event_type].get(priority.value, [])

                    for callback in callbacks:
                        try:
                            # Tentar executar callback
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event_data)
                            else:
                                callback(event_data)

                        except Exception as e:
                            # Tratamento de erros em callbacks (não interrompe execução)
                            logger.error(
                                "Error executing callback",
                                match_id=match_id,
                                event_type=event_type,
                                priority=priority.value,
                                error=str(e)
                            )

    def _priority_value(self, priority: EventPriority) -> int:
        """Retorna valor numérico da prioridade para comparação"""
        priority_values = {
            EventPriority.LOW: 1,
            EventPriority.NORMAL: 2,
            EventPriority.HIGH: 3,
            EventPriority.CRITICAL: 4
        }
        return priority_values.get(priority, 0)

    def unregister_callback(
        self,
        match_id: str,
        event_type: str,
        callback: Callable,
        priority: Optional[EventPriority] = None
    ) -> bool:
        """
        Remove um callback registrado

        Args:
            match_id: ID da partida
            event_type: Tipo de evento
            callback: Função callback
            priority: Prioridade (opcional, remove de todas se None)

        Returns:
            True se removido com sucesso
        """
        try:
            if match_id not in self._callbacks:
                return False

            if event_type not in self._callbacks[match_id]:
                return False

            # Se prioridade específica
            if priority:
                if priority.value in self._callbacks[match_id][event_type]:
                    if callback in self._callbacks[match_id][event_type][priority.value]:
                        self._callbacks[match_id][event_type][priority.value].remove(callback)
                        return True
            else:
                # Remover de todas as prioridades
                removed = False
                for priority_key in self._callbacks[match_id][event_type]:
                    if callback in self._callbacks[match_id][event_type][priority_key]:
                        self._callbacks[match_id][event_type][priority_key].remove(callback)
                        removed = True
                return removed

            return False

        except Exception as e:
            logger.error(
                "Error unregistering callback",
                match_id=match_id,
                event_type=event_type,
                error=str(e)
            )
            return False

    async def get_event_description(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> str:
        """
        Gera descrição legível em português para um evento

        Critérios de aceite TT-46:
        - [x] Descrições em português para todos os tipos
        - [x] Inclusão de dados específicos (velocidade da bola)
        - [x] Nome do jogador na descrição

        Args:
            event_type: Tipo do evento
            event_data: Dados do evento (player_id, metadata, etc)

        Returns:
            Descrição em português do evento
        """
        try:
            player_id = event_data.get("player_id", "")
            metadata = event_data.get("metadata", {})

            # Buscar nome do jogador
            player_name = "Jogador"
            if player_id:
                try:
                    from app.models.player import Player
                    stmt = select(Player).where(Player.id == player_id)
                    result = await self.db.execute(stmt)
                    player = result.scalar_one_or_none()
                    if player:
                        player_name = player.name
                except:
                    pass

            # Gerar descrição baseada no tipo de evento
            if event_type == EventType.ACE:
                speed = metadata.get("ball_speed", None)
                if speed:
                    return f"Ace de {player_name} no primeiro saque ({speed} km/h)"
                return f"Ace de {player_name}"

            elif event_type == EventType.DOUBLE_FAULT:
                return f"Dupla falta de {player_name}"

            elif event_type == EventType.WINNER:
                shot_type = metadata.get("shot_type", "")
                if shot_type:
                    return f"Winner de {player_name} ({shot_type})"
                return f"Winner de {player_name}"

            elif event_type == EventType.UNFORCED_ERROR:
                return f"Erro não forçado de {player_name}"

            elif event_type == EventType.FORCED_ERROR:
                return f"Erro forçado de {player_name}"

            elif event_type == EventType.BREAK_POINT:
                return f"Break point contra {player_name}"

            elif event_type == EventType.SET_POINT:
                return f"Set point para {player_name}"

            elif event_type == EventType.MATCH_POINT:
                return f"Match point para {player_name}"

            elif event_type == EventType.DEUCE:
                return "Deuce no game"

            elif event_type == EventType.ADVANTAGE:
                return f"Vantagem para {player_name}"

            elif event_type == EventType.TIEBREAK_START:
                return "Início do tiebreak"

            elif event_type == EventType.GAME_WON:
                return f"Game conquistado por {player_name}"

            elif event_type == EventType.SET_WON:
                set_score = metadata.get("set_score", "")
                if set_score:
                    return f"Set vencido por {player_name} ({set_score})"
                return f"Set vencido por {player_name}"

            elif event_type == EventType.MATCH_WON:
                final_score = metadata.get("final_score", "")
                if final_score:
                    return f"Partida vencida por {player_name} ({final_score})"
                return f"Partida vencida por {player_name}"

            elif event_type == EventType.CHALLENGE:
                outcome = metadata.get("outcome", "")
                if outcome == "successful":
                    return f"Challenge bem-sucedido de {player_name}"
                elif outcome == "unsuccessful":
                    return f"Challenge sem sucesso de {player_name}"
                return f"Challenge de {player_name}"

            elif event_type == EventType.MEDICAL_TIMEOUT:
                reason = metadata.get("reason", "")
                if reason:
                    return f"Timeout médico de {player_name} ({reason})"
                return f"Timeout médico de {player_name}"

            elif event_type == EventType.COACHING_TIMEOUT:
                return f"Timeout de coaching de {player_name}"

            else:
                return f"Evento: {event_type}"

        except Exception as e:
            logger.error("Error generating event description", event_type=event_type, error=str(e))
            return f"Evento: {event_type}"
