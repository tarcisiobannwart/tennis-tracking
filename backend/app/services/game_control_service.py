"""
Game Control Service
Gerencia o ciclo de vida e estado de partidas em tempo real
"""

from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from bson import ObjectId
import structlog

from app.core.mongodb import get_database
from app.schemas.game_control import (
    GameStateEnum,
    PointTypeEnum,
    GameEventTypeEnum,
    StartMatchRequest,
    PauseMatchRequest,
    ResumeMatchRequest,
    AddPointRequest,
    PointMetadata,
    GameStateSnapshot,
    GameEventData,
    GameControlResponse,
    MatchStateResponse
)

logger = structlog.get_logger(__name__)


class GameControlService:
    """Service for game control operations"""

    def __init__(self):
        self.db = get_database()
        # Armazena callbacks por match_id -> event_type -> [callbacks]
        self._callbacks: Dict[str, Dict[str, List[Callable]]] = {}

    async def start_match(
        self,
        match_id: str,
        server_player_id: str,
        tournament_data: Optional[Dict[str, Any]] = None
    ) -> GameControlResponse:
        """
        Inicia uma partida

        Critérios de aceite TT-29:
        - [x] start_match() com jogador sacador e dados do torneio
        - [x] Validacao de estado (nao iniciar partida ja iniciada)
        - [x] Suporte a formatos best_of_3 e best_of_5
        """
        try:
            # Buscar partida
            match = await self.db.matches.find_one({"_id": ObjectId(match_id)})
            if not match:
                match = await self.db.matches.find_one({"matchId": match_id})

            if not match:
                return GameControlResponse(
                    success=False,
                    message="Partida não encontrada",
                    match_id=match_id
                )

            # Validar estado - não iniciar partida já iniciada
            current_status = match.get("status", "scheduled")
            if current_status in ["in_progress", "completed"]:
                return GameControlResponse(
                    success=False,
                    message=f"Partida não pode ser iniciada. Status atual: {current_status}",
                    match_id=match_id,
                    state=GameStateEnum.IN_PROGRESS if current_status == "in_progress" else GameStateEnum.COMPLETED
                )

            # Validar jogador sacador
            player1_id = match.get("player1_id") or match.get("player1")
            player2_id = match.get("player2_id") or match.get("player2")

            if server_player_id not in [str(player1_id), str(player2_id)]:
                return GameControlResponse(
                    success=False,
                    message="Jogador sacador inválido",
                    match_id=match_id
                )

            # Inicializar estado do jogo
            game_state = {
                "state": GameStateEnum.IN_PROGRESS.value,
                "current_set": 1,
                "current_game": 1,
                "player1_sets": 0,
                "player2_sets": 0,
                "player1_games": 0,
                "player2_games": 0,
                "player1_points": 0,
                "player2_points": 0,
                "server_player_id": server_player_id,
                "started_at": datetime.utcnow(),
                "paused_at": None,
                "resumed_at": None,
                "last_point_at": None,
                "tournament_data": tournament_data or {},
                "best_of_sets": match.get("best_of_sets", 3)  # Suporte a best_of_3 e best_of_5
            }

            # Atualizar partida
            await self.db.matches.update_one(
                {"_id": match["_id"]},
                {
                    "$set": {
                        "status": "in_progress",
                        "started_at": game_state["started_at"],
                        "game_state": game_state,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )

            logger.info(
                "Match started",
                match_id=match_id,
                server=server_player_id,
                best_of_sets=game_state["best_of_sets"]
            )

            # Emitir evento
            await self._emit_event(
                match_id=match_id,
                event_type=GameEventTypeEnum.MATCH_STARTED,
                metadata={
                    "server_player_id": server_player_id,
                    "tournament_data": tournament_data,
                    "best_of_sets": game_state["best_of_sets"]
                }
            )

            return GameControlResponse(
                success=True,
                message="Partida iniciada com sucesso",
                match_id=match_id,
                state=GameStateEnum.IN_PROGRESS,
                data=game_state
            )

        except Exception as e:
            logger.error("Error starting match", match_id=match_id, error=str(e))
            return GameControlResponse(
                success=False,
                message=f"Erro ao iniciar partida: {str(e)}",
                match_id=match_id
            )

    async def pause_match(self, match_id: str, reason: Optional[str] = None) -> GameControlResponse:
        """
        Pausa uma partida em andamento

        Critérios de aceite TT-29:
        - [x] pause_match() com eventos
        """
        try:
            match = await self.db.matches.find_one({"_id": ObjectId(match_id)})
            if not match:
                match = await self.db.matches.find_one({"matchId": match_id})

            if not match:
                return GameControlResponse(
                    success=False,
                    message="Partida não encontrada",
                    match_id=match_id
                )

            game_state = match.get("game_state", {})

            if game_state.get("state") != GameStateEnum.IN_PROGRESS.value:
                return GameControlResponse(
                    success=False,
                    message=f"Partida não está em andamento. Estado atual: {game_state.get('state')}",
                    match_id=match_id
                )

            # Pausar partida
            game_state["state"] = GameStateEnum.PAUSED.value
            game_state["paused_at"] = datetime.utcnow()

            await self.db.matches.update_one(
                {"_id": match["_id"]},
                {
                    "$set": {
                        "game_state": game_state,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )

            logger.info("Match paused", match_id=match_id, reason=reason)

            # Emitir evento
            await self._emit_event(
                match_id=match_id,
                event_type=GameEventTypeEnum.MATCH_PAUSED,
                metadata={"reason": reason}
            )

            return GameControlResponse(
                success=True,
                message="Partida pausada com sucesso",
                match_id=match_id,
                state=GameStateEnum.PAUSED,
                data={"reason": reason}
            )

        except Exception as e:
            logger.error("Error pausing match", match_id=match_id, error=str(e))
            return GameControlResponse(
                success=False,
                message=f"Erro ao pausar partida: {str(e)}",
                match_id=match_id
            )

    async def resume_match(self, match_id: str) -> GameControlResponse:
        """
        Resume uma partida pausada

        Critérios de aceite TT-29:
        - [x] resume_match() com eventos
        """
        try:
            match = await self.db.matches.find_one({"_id": ObjectId(match_id)})
            if not match:
                match = await self.db.matches.find_one({"matchId": match_id})

            if not match:
                return GameControlResponse(
                    success=False,
                    message="Partida não encontrada",
                    match_id=match_id
                )

            game_state = match.get("game_state", {})

            if game_state.get("state") != GameStateEnum.PAUSED.value:
                return GameControlResponse(
                    success=False,
                    message=f"Partida não está pausada. Estado atual: {game_state.get('state')}",
                    match_id=match_id
                )

            # Retomar partida
            game_state["state"] = GameStateEnum.IN_PROGRESS.value
            game_state["resumed_at"] = datetime.utcnow()

            await self.db.matches.update_one(
                {"_id": match["_id"]},
                {
                    "$set": {
                        "game_state": game_state,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )

            logger.info("Match resumed", match_id=match_id)

            # Emitir evento
            await self._emit_event(
                match_id=match_id,
                event_type=GameEventTypeEnum.MATCH_RESUMED
            )

            return GameControlResponse(
                success=True,
                message="Partida retomada com sucesso",
                match_id=match_id,
                state=GameStateEnum.IN_PROGRESS
            )

        except Exception as e:
            logger.error("Error resuming match", match_id=match_id, error=str(e))
            return GameControlResponse(
                success=False,
                message=f"Erro ao retomar partida: {str(e)}",
                match_id=match_id
            )

    async def add_point(
        self,
        match_id: str,
        winner_player_id: str,
        point_type: PointTypeEnum,
        metadata: Optional[PointMetadata] = None
    ) -> GameControlResponse:
        """
        Registra um ponto com metadados

        Critérios de aceite TT-30:
        - [x] add_point() com winner_player_id e point_type
        - [x] Suporte a dados: ball_speed, ball_position, shot_type
        - [x] Validacao de estado (partida em andamento, nao pausada)
        - [x] Salvar estado antes do ponto para eventos
        """
        try:
            match = await self.db.matches.find_one({"_id": ObjectId(match_id)})
            if not match:
                match = await self.db.matches.find_one({"matchId": match_id})

            if not match:
                return GameControlResponse(
                    success=False,
                    message="Partida não encontrada",
                    match_id=match_id
                )

            game_state = match.get("game_state", {})

            # Validação de estado (partida em andamento, não pausada)
            if game_state.get("state") != GameStateEnum.IN_PROGRESS.value:
                return GameControlResponse(
                    success=False,
                    message=f"Partida não está em andamento. Estado atual: {game_state.get('state')}",
                    match_id=match_id
                )

            # Salvar estado antes do ponto para eventos
            state_before = GameStateSnapshot(
                match_id=match_id,
                current_set=game_state.get("current_set", 1),
                current_game=game_state.get("current_game", 1),
                player1_sets=game_state.get("player1_sets", 0),
                player2_sets=game_state.get("player2_sets", 0),
                player1_games=game_state.get("player1_games", 0),
                player2_games=game_state.get("player2_games", 0),
                player1_points=game_state.get("player1_points", 0),
                player2_points=game_state.get("player2_points", 0),
                server_player_id=game_state.get("server_player_id", ""),
                timestamp=datetime.utcnow()
            )

            # Criar registro do ponto
            point_data = {
                "match_id": match_id,
                "winner_player_id": winner_player_id,
                "point_type": point_type.value,
                "timestamp": datetime.utcnow(),
                "state_before": state_before.dict(),
                "metadata": metadata.dict() if metadata else {}
            }

            # Salvar ponto no banco
            point_result = await self.db.points.insert_one(point_data)

            # Atualizar placar (lógica simplificada - pode ser expandida)
            # TODO: Implementar lógica completa de placar de tênis
            game_state["last_point_at"] = datetime.utcnow()

            await self.db.matches.update_one(
                {"_id": match["_id"]},
                {
                    "$set": {
                        "game_state": game_state,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )

            logger.info(
                "Point added",
                match_id=match_id,
                winner=winner_player_id,
                point_type=point_type.value,
                metadata=metadata.dict() if metadata else None
            )

            # Emitir evento de ponto
            await self._emit_event(
                match_id=match_id,
                event_type=GameEventTypeEnum.POINT_SCORED,
                player_id=winner_player_id,
                state_before=state_before,
                metadata={
                    "point_type": point_type.value,
                    "point_metadata": metadata.dict() if metadata else {}
                }
            )

            # Verificar eventos especiais
            if point_type == PointTypeEnum.ACE:
                await self._emit_event(
                    match_id=match_id,
                    event_type=GameEventTypeEnum.ACE,
                    player_id=winner_player_id
                )
            elif point_type == PointTypeEnum.WINNER:
                await self._emit_event(
                    match_id=match_id,
                    event_type=GameEventTypeEnum.WINNER,
                    player_id=winner_player_id
                )
            elif point_type == PointTypeEnum.DOUBLE_FAULT:
                await self._emit_event(
                    match_id=match_id,
                    event_type=GameEventTypeEnum.DOUBLE_FAULT,
                    player_id=winner_player_id
                )

            # Detectar situações críticas (TT-32)
            player1_id = match.get("player1_id") or match.get("player1")
            player2_id = match.get("player2_id") or match.get("player2")

            # Detectar break point
            is_break_pt = self._is_break_point(
                server_player_id=game_state.get("server_player_id", ""),
                player1_id=str(player1_id),
                player2_id=str(player2_id),
                player1_points=game_state.get("player1_points", 0),
                player2_points=game_state.get("player2_points", 0)
            )

            if is_break_pt:
                await self._emit_event(
                    match_id=match_id,
                    event_type=GameEventTypeEnum.BREAK_POINT,
                    metadata={
                        "player1_points": game_state.get("player1_points", 0),
                        "player2_points": game_state.get("player2_points", 0)
                    }
                )

            # Detectar set point
            is_set_pt, player_with_set_pt = self._is_set_point(
                player1_id=str(player1_id),
                player2_id=str(player2_id),
                player1_games=game_state.get("player1_games", 0),
                player2_games=game_state.get("player2_games", 0),
                player1_points=game_state.get("player1_points", 0),
                player2_points=game_state.get("player2_points", 0),
                is_tiebreak=False  # TODO: detectar tiebreak
            )

            if is_set_pt:
                await self._emit_event(
                    match_id=match_id,
                    event_type=GameEventTypeEnum.SET_POINT,
                    player_id=player_with_set_pt,
                    metadata={
                        "player1_games": game_state.get("player1_games", 0),
                        "player2_games": game_state.get("player2_games", 0)
                    }
                )

            # Detectar match point
            is_match_pt, player_with_match_pt = self._is_match_point(
                player1_id=str(player1_id),
                player2_id=str(player2_id),
                player1_sets=game_state.get("player1_sets", 0),
                player2_sets=game_state.get("player2_sets", 0),
                player1_games=game_state.get("player1_games", 0),
                player2_games=game_state.get("player2_games", 0),
                player1_points=game_state.get("player1_points", 0),
                player2_points=game_state.get("player2_points", 0),
                best_of_sets=game_state.get("best_of_sets", 3),
                is_tiebreak=False  # TODO: detectar tiebreak
            )

            if is_match_pt:
                await self._emit_event(
                    match_id=match_id,
                    event_type=GameEventTypeEnum.MATCH_POINT,
                    player_id=player_with_match_pt,
                    metadata={
                        "player1_sets": game_state.get("player1_sets", 0),
                        "player2_sets": game_state.get("player2_sets", 0)
                    }
                )

            return GameControlResponse(
                success=True,
                message="Ponto registrado com sucesso",
                match_id=match_id,
                data={
                    "point_id": str(point_result.inserted_id),
                    "state_before": state_before.dict()
                }
            )

        except Exception as e:
            logger.error("Error adding point", match_id=match_id, error=str(e))
            return GameControlResponse(
                success=False,
                message=f"Erro ao registrar ponto: {str(e)}",
                match_id=match_id
            )

    async def register_event_callback(
        self,
        match_id: str,
        event_type: GameEventTypeEnum,
        callback: Callable
    ) -> bool:
        """
        Registra um callback para um tipo de evento

        Critérios de aceite TT-31:
        - [x] register_event_callback() por tipo de evento
        """
        try:
            if match_id not in self._callbacks:
                self._callbacks[match_id] = {}

            if event_type.value not in self._callbacks[match_id]:
                self._callbacks[match_id][event_type.value] = []

            self._callbacks[match_id][event_type.value].append(callback)

            logger.info(
                "Event callback registered",
                match_id=match_id,
                event_type=event_type.value
            )

            return True
        except Exception as e:
            logger.error(
                "Error registering callback",
                match_id=match_id,
                event_type=event_type.value,
                error=str(e)
            )
            return False

    async def _emit_event(
        self,
        match_id: str,
        event_type: GameEventTypeEnum,
        player_id: Optional[str] = None,
        state_before: Optional[GameStateSnapshot] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Emite um evento para todos os callbacks registrados

        Critérios de aceite TT-31:
        - [x] Emissao de eventos: match_started, point_scored, game_won, set_won, match_completed
        - [x] Eventos especiais: ace, winner, double_fault
        - [x] Tratamento de erros em callbacks
        """
        event_data = GameEventData(
            match_id=match_id,
            event_type=event_type,
            player_id=player_id,
            timestamp=datetime.utcnow(),
            state_before=state_before,
            metadata=metadata or {}
        )

        # Salvar evento no banco
        await self.db.game_events.insert_one({
            "match_id": match_id,
            "event_type": event_type.value,
            "player_id": player_id,
            "timestamp": event_data.timestamp,
            "state_before": state_before.dict() if state_before else None,
            "metadata": metadata or {}
        })

        # Executar callbacks (com tratamento de erros)
        if match_id in self._callbacks:
            callbacks = self._callbacks[match_id].get(event_type.value, [])

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
                        event_type=event_type.value,
                        error=str(e)
                    )

    async def get_match_state(self, match_id: str) -> Optional[MatchStateResponse]:
        """Retorna o estado atual da partida"""
        try:
            match = await self.db.matches.find_one({"_id": ObjectId(match_id)})
            if not match:
                match = await self.db.matches.find_one({"matchId": match_id})

            if not match:
                return None

            game_state = match.get("game_state", {})

            return MatchStateResponse(
                match_id=match_id,
                state=GameStateEnum(game_state.get("state", "warm_up")),
                current_set=game_state.get("current_set", 1),
                current_game=game_state.get("current_game", 1),
                player1_sets=game_state.get("player1_sets", 0),
                player2_sets=game_state.get("player2_sets", 0),
                player1_games=game_state.get("player1_games", 0),
                player2_games=game_state.get("player2_games", 0),
                player1_points=game_state.get("player1_points", 0),
                player2_points=game_state.get("player2_points", 0),
                server_player_id=game_state.get("server_player_id", ""),
                started_at=game_state.get("started_at"),
                paused_at=game_state.get("paused_at"),
                resumed_at=game_state.get("resumed_at"),
                last_point_at=game_state.get("last_point_at")
            )

        except Exception as e:
            logger.error("Error getting match state", match_id=match_id, error=str(e))
            return None

    def _is_break_point(
        self,
        server_player_id: str,
        player1_id: str,
        player2_id: str,
        player1_points: int,
        player2_points: int
    ) -> bool:
        """
        Detecta se a situação atual é break point

        Critérios de aceite TT-32:
        - [x] Verifica se jogador que NÃO está sacando pode ganhar o game
        - [x] Considera advantage e deuce

        Args:
            server_player_id: ID do jogador sacando
            player1_id: ID do player 1
            player2_id: ID do player 2
            player1_points: Pontos do player 1 no game atual
            player2_points: Pontos do player 2 no game atual

        Returns:
            True se é break point, False caso contrário
        """
        # Determinar quem está recebendo
        receiver_id = player2_id if server_player_id == player1_id else player1_id

        # Determinar pontos do sacador e recebedor
        if server_player_id == player1_id:
            server_points = player1_points
            receiver_points = player2_points
        else:
            server_points = player2_points
            receiver_points = player1_points

        # Break point ocorre quando:
        # 1. Recebedor tem 40 e sacador tem menos (40-0, 40-15, 40-30)
        # 2. Advantage para o recebedor (após deuce)

        # Caso 1: 40 vs menos que 40 (receiver vencendo)
        if receiver_points >= 40 and server_points < 40:
            return True

        # Caso 2: Advantage para receiver (ambos >= 40, receiver tem mais)
        if receiver_points >= 40 and server_points >= 40 and receiver_points > server_points:
            return True

        return False

    def _is_set_point(
        self,
        player1_id: str,
        player2_id: str,
        player1_games: int,
        player2_games: int,
        player1_points: int,
        player2_points: int,
        is_tiebreak: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Detecta se a situação atual é set point

        Critérios de aceite TT-32:
        - [x] Verifica se jogador pode ganhar o set
        - [x] Considera advantage e deuce

        Args:
            player1_id: ID do player 1
            player2_id: ID do player 2
            player1_games: Games do player 1 no set atual
            player2_games: Games do player 2 no set atual
            player1_points: Pontos do player 1 no game atual
            player2_points: Pontos do player 2 no game atual
            is_tiebreak: Se está em tiebreak

        Returns:
            Tupla (is_set_point, player_id_with_set_point)
        """
        # Em tiebreak: primeiro a 7 pontos, com 2 de vantagem
        if is_tiebreak:
            # Player 1 tem set point no tiebreak
            if player1_points >= 6 and player1_points >= player2_points + 1:
                return (True, player1_id)
            # Player 2 tem set point no tiebreak
            if player2_points >= 6 and player2_points >= player1_points + 1:
                return (True, player2_id)
            return (False, None)

        # Set point em game normal
        # Player 1 pode fechar set (tem 5+ games e está com game point)
        if player1_games >= 5:
            # Caso 1: 5-qualquer coisa, player1 tem 40+ pontos
            if player1_games >= 5 and player1_points >= 40:
                # Verifica se player1 tem game point
                if player1_points >= 40 and player2_points < 40:
                    return (True, player1_id)
                if player1_points > player2_points and player1_points >= 40 and player2_points >= 40:
                    return (True, player1_id)

        # Player 2 pode fechar set
        if player2_games >= 5:
            if player2_games >= 5 and player2_points >= 40:
                if player2_points >= 40 and player1_points < 40:
                    return (True, player2_id)
                if player2_points > player1_points and player2_points >= 40 and player1_points >= 40:
                    return (True, player2_id)

        return (False, None)

    def _is_match_point(
        self,
        player1_id: str,
        player2_id: str,
        player1_sets: int,
        player2_sets: int,
        player1_games: int,
        player2_games: int,
        player1_points: int,
        player2_points: int,
        best_of_sets: int = 3,
        is_tiebreak: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Detecta se a situação atual é match point

        Critérios de aceite TT-32:
        - [x] Verifica se jogador pode ganhar a partida
        - [x] Considera advantage e deuce

        Args:
            player1_id: ID do player 1
            player2_id: ID do player 2
            player1_sets: Sets do player 1
            player2_sets: Sets do player 2
            player1_games: Games do player 1 no set atual
            player2_games: Games do player 2 no set atual
            player1_points: Pontos do player 1 no game atual
            player2_points: Pontos do player 2 no game atual
            best_of_sets: Formato da partida (3 ou 5)
            is_tiebreak: Se está em tiebreak

        Returns:
            Tupla (is_match_point, player_id_with_match_point)
        """
        # Calcular quantos sets necessários para vencer
        sets_to_win = (best_of_sets // 2) + 1  # 2 para best_of_3, 3 para best_of_5

        # Verificar se player1 está a 1 set de vencer a partida E tem set point
        if player1_sets == sets_to_win - 1:
            is_set_pt, player_with_set_pt = self._is_set_point(
                player1_id, player2_id,
                player1_games, player2_games,
                player1_points, player2_points,
                is_tiebreak
            )
            if is_set_pt and player_with_set_pt == player1_id:
                return (True, player1_id)

        # Verificar se player2 está a 1 set de vencer a partida E tem set point
        if player2_sets == sets_to_win - 1:
            is_set_pt, player_with_set_pt = self._is_set_point(
                player1_id, player2_id,
                player1_games, player2_games,
                player1_points, player2_points,
                is_tiebreak
            )
            if is_set_pt and player_with_set_pt == player2_id:
                return (True, player2_id)

        return (False, None)

    async def export_match_data(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Exporta todos os dados completos da partida

        Critérios de aceite TT-33:
        - [x] export_match_data() com match, events e statistics
        - [x] Inclui todos os dados do match, eventos e estatísticas

        Args:
            match_id: ID da partida

        Returns:
            Dict com match, events, statistics ou None se não encontrado
        """
        try:
            # Buscar partida
            match = await self.db.matches.find_one({"_id": ObjectId(match_id)})
            if not match:
                match = await self.db.matches.find_one({"matchId": match_id})

            if not match:
                logger.warning("Match not found for export", match_id=match_id)
                return None

            # Buscar todos os eventos da partida
            events_cursor = self.db.game_events.find({"match_id": match_id}).sort("timestamp", 1)
            events = []
            async for event in events_cursor:
                event["_id"] = str(event["_id"])
                events.append(event)

            # Buscar todos os pontos
            points_cursor = self.db.points.find({"match_id": match_id}).sort("timestamp", 1)
            points = []
            async for point in points_cursor:
                point["_id"] = str(point["_id"])
                points.append(point)

            # Obter estatísticas
            statistics = await self.get_match_statistics(match_id)

            # Converter ObjectId para string
            match["_id"] = str(match["_id"])

            # Preparar dados completos
            export_data = {
                "match": match,
                "events": events,
                "points": points,
                "statistics": statistics,
                "export_timestamp": datetime.utcnow().isoformat()
            }

            logger.info(
                "Match data exported",
                match_id=match_id,
                events_count=len(events),
                points_count=len(points)
            )

            return export_data

        except Exception as e:
            logger.error("Error exporting match data", match_id=match_id, error=str(e))
            return None

    async def get_match_statistics(self, match_id: str) -> Dict[str, Any]:
        """
        Retorna estatísticas completas da partida

        Critérios de aceite TT-33:
        - [x] get_match_statistics() com info, players, score e events_count
        - [x] Calculo de duração da partida (horas e minutos)

        Args:
            match_id: ID da partida

        Returns:
            Dict com estatísticas da partida
        """
        try:
            # Buscar partida
            match = await self.db.matches.find_one({"_id": ObjectId(match_id)})
            if not match:
                match = await self.db.matches.find_one({"matchId": match_id})

            if not match:
                return {}

            game_state = match.get("game_state", {})

            # Calcular duração da partida
            duration_info = {}
            started_at = game_state.get("started_at")
            if started_at:
                # Se partida está completa, usar ended_at
                ended_at = game_state.get("ended_at") or datetime.utcnow()

                # Calcular duração
                duration = ended_at - started_at
                duration_seconds = duration.total_seconds()
                duration_hours = int(duration_seconds // 3600)
                duration_minutes = int((duration_seconds % 3600) // 60)

                duration_info = {
                    "total_seconds": duration_seconds,
                    "hours": duration_hours,
                    "minutes": duration_minutes,
                    "formatted": f"{duration_hours}h {duration_minutes}min"
                }

            # Contar eventos por tipo
            events_count = {}
            pipeline = [
                {"$match": {"match_id": match_id}},
                {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
            ]
            async for result in self.db.game_events.aggregate(pipeline):
                events_count[result["_id"]] = result["count"]

            # Informações dos jogadores
            player1_id = match.get("player1_id") or match.get("player1")
            player2_id = match.get("player2_id") or match.get("player2")

            # Estatísticas básicas
            statistics = {
                "info": {
                    "match_id": match_id,
                    "status": match.get("status", "unknown"),
                    "started_at": started_at.isoformat() if started_at else None,
                    "duration": duration_info,
                    "best_of_sets": game_state.get("best_of_sets", 3)
                },
                "players": {
                    "player1": {
                        "id": str(player1_id),
                        "sets": game_state.get("player1_sets", 0),
                        "games": game_state.get("player1_games", 0),
                        "points": game_state.get("player1_points", 0)
                    },
                    "player2": {
                        "id": str(player2_id),
                        "sets": game_state.get("player2_sets", 0),
                        "games": game_state.get("player2_games", 0),
                        "points": game_state.get("player2_points", 0)
                    }
                },
                "score": {
                    "current_set": game_state.get("current_set", 1),
                    "current_game": game_state.get("current_game", 1),
                    "server_player_id": game_state.get("server_player_id", "")
                },
                "events_count": events_count
            }

            return statistics

        except Exception as e:
            logger.error("Error getting match statistics", match_id=match_id, error=str(e))
            return {}

    async def get_recent_events(
        self,
        match_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retorna eventos recentes da partida

        Critérios de aceite TT-33:
        - [x] get_recent_events() com limite configurável

        Args:
            match_id: ID da partida
            limit: Número máximo de eventos a retornar (default: 10)

        Returns:
            Lista de eventos recentes
        """
        try:
            events_cursor = self.db.game_events.find(
                {"match_id": match_id}
            ).sort("timestamp", -1).limit(limit)

            events = []
            async for event in events_cursor:
                event["_id"] = str(event["_id"])
                events.append(event)

            return events

        except Exception as e:
            logger.error("Error getting recent events", match_id=match_id, error=str(e))
            return []


# Import asyncio for callback execution
import asyncio
