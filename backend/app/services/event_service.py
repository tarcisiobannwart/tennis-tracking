"""
Event Service
Detecta e classifica eventos automáticos da partida
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
import structlog

from app.core.mongodb import get_database
from app.schemas.game_control import (
    PointTypeEnum,
    GameStateSnapshot
)

logger = structlog.get_logger(__name__)


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
    """

    def __init__(self):
        self.db = get_database()

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
            match = await self.db.matches.find_one({"_id": ObjectId(match_id)})
            if not match:
                match = await self.db.matches.find_one({"matchId": match_id})

            if match:
                game_state = match.get("game_state", {})
                server_player_id = game_state.get("server_player_id", "")

                # Verificar se é break point
                is_break_pt = self._is_break_point(
                    server_player_id=server_player_id,
                    player1_points=state_before.player1_points,
                    player2_points=state_before.player2_points,
                    player1_id=str(match.get("player1_id") or match.get("player1")),
                    player2_id=str(match.get("player2_id") or match.get("player2"))
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
                match = await self.db.matches.find_one({"_id": ObjectId(match_id)})
                if not match:
                    match = await self.db.matches.find_one({"matchId": match_id})

                if match and match.get("status") == "completed":
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
            event_data = {
                "match_id": match_id,
                "event_type": event_type,
                "player_id": player_id,
                "timestamp": datetime.utcnow(),
                "state_before": state_before.dict() if state_before else None,
                "metadata": metadata
            }

            await self.db.game_events.insert_one(event_data)

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
            await self._save_event(
                match_id=match_id,
                event_type=EventType.CHALLENGE,
                player_id=player_id,
                state_before=None,
                metadata={
                    "call_challenged": call_challenged,
                    "outcome": outcome
                }
            )

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

            await self._save_event(
                match_id=match_id,
                event_type=timeout_type,
                player_id=player_id or "",
                state_before=None,
                metadata={"reason": reason}
            )

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
            events_cursor = self.db.game_events.find({
                "match_id": match_id,
                "event_type": event_type
            }).sort("timestamp", 1)

            events = []
            async for event in events_cursor:
                event["_id"] = str(event["_id"])
                events.append(event)

            return events

        except Exception as e:
            logger.error("Error getting events by type", match_id=match_id, error=str(e))
            return []
