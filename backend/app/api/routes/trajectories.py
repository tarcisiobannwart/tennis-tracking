"""
API endpoints para busca por similaridade de trajetórias usando pgvector.

Fornece endpoints para salvar embeddings de trajetórias e buscar padrões similares.
"""

import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.sql.user import User
from app.services import trajectory_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────


class TrajectoryCreate(BaseModel):
    """Request para criar embedding de trajetória."""
    match_id: str = Field(..., description="ID da partida")
    points: list[list[float]] = Field(..., description="Lista de pontos [[x1,y1], [x2,y2], ...] ou [[x1,y1,t1], ...]")
    point_id: str | None = Field(None, description="ID do ponto")
    player_id: str | None = Field(None, description="ID do jogador")
    shot_type: str | None = Field(None, description="Tipo de golpe: forehand, backhand, serve, volley")
    trajectory_type: str | None = Field(None, description="Tipo de trajetória: cross_court, down_the_line, lob, drop_shot")
    duration_ms: float | None = Field(None, description="Duração em milissegundos")
    metadata: dict | None = Field(None, description="Metadados adicionais")


class TrajectorySearchRequest(BaseModel):
    """Request para buscar trajetórias similares."""
    points: list[list[float]] = Field(..., description="Lista de pontos da trajetória de query")
    limit: int = Field(10, ge=1, le=100, description="Número máximo de resultados")
    threshold: float = Field(0.8, ge=0.0, le=1.0, description="Limite de similaridade (0-1)")
    shot_type: str | None = Field(None, description="Filtrar por tipo de golpe")
    exclude_match_id: str | None = Field(None, description="Excluir trajetórias de uma partida")


class TrajectoryResponse(BaseModel):
    """Response com dados da trajetória."""
    id: str
    match_id: str
    point_id: str | None
    player_id: str | None
    shot_type: str | None
    trajectory_type: str | None
    num_points: int
    duration_ms: float | None
    raw_trajectory: dict | None
    metadata: dict | None
    created_at: str


class SimilarTrajectoryResponse(BaseModel):
    """Response com trajetória similar e score de similaridade."""
    trajectory: TrajectoryResponse
    similarity_score: float


class TrajectoryMatchResponse(BaseModel):
    """Response com trajetórias similares entre partidas."""
    source_trajectory: TrajectoryResponse
    similar_trajectory: TrajectoryResponse
    similarity_score: float


class PlayerPatternsResponse(BaseModel):
    """Response com padrões de golpe do jogador."""
    player_id: str
    total_trajectories: int
    shot_types: dict[str, dict[str, Any]]
    trajectory_types: dict[str, dict[str, Any]]


# ── Endpoints ────────────────────────────────────────────────


@router.post("", response_model=TrajectoryResponse, status_code=status.HTTP_201_CREATED)
async def create_trajectory(
    trajectory: TrajectoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Salvar trajetória com embedding para busca por similaridade.

    Converte a lista de pontos em embedding de 128 dimensões e armazena no banco.
    O embedding é gerado de forma determinística (sem ML) para permitir busca eficiente.
    """
    try:
        # Gerar embedding
        embedding = trajectory_service.encode_trajectory(trajectory.points)

        # Preparar raw_trajectory
        raw_trajectory = {
            "points": trajectory.points,
            "court_normalized": False,  # Assumir que não está normalizado
        }

        # Salvar no banco
        traj_embedding = await trajectory_service.store_trajectory(
            db=db,
            match_id=trajectory.match_id,
            embedding=embedding,
            raw_trajectory=raw_trajectory,
            point_id=trajectory.point_id,
            player_id=trajectory.player_id,
            shot_type=trajectory.shot_type,
            trajectory_type=trajectory.trajectory_type,
            duration_ms=trajectory.duration_ms,
            metadata=trajectory.metadata,
        )

        return TrajectoryResponse(
            id=str(traj_embedding.id),
            match_id=traj_embedding.match_id,
            point_id=traj_embedding.point_id,
            player_id=traj_embedding.player_id,
            shot_type=traj_embedding.shot_type,
            trajectory_type=traj_embedding.trajectory_type,
            num_points=traj_embedding.num_points,
            duration_ms=traj_embedding.duration_ms,
            raw_trajectory=traj_embedding.raw_trajectory,
            metadata=traj_embedding.metadata_,
            created_at=traj_embedding.created_at.isoformat(),
        )

    except Exception as e:
        logger.error(f"Erro ao criar trajetória: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar trajetória: {str(e)}"
        )


@router.post("/search", response_model=list[SimilarTrajectoryResponse])
async def search_trajectories(
    search: TrajectorySearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Buscar trajetórias similares usando cosine similarity.

    Converte a trajetória de query em embedding e busca no banco usando pgvector.
    Retorna trajetórias ordenadas por similaridade (1.0 = idêntico, 0.0 = diferente).
    """
    try:
        # Gerar embedding da query
        query_embedding = trajectory_service.encode_trajectory(search.points)

        # Buscar similares
        similar = await trajectory_service.find_similar(
            db=db,
            embedding=query_embedding,
            limit=search.limit,
            threshold=search.threshold,
            shot_type=search.shot_type,
            exclude_match_id=search.exclude_match_id,
        )

        # Converter para response
        results = []
        for traj, similarity in similar:
            results.append(
                SimilarTrajectoryResponse(
                    trajectory=TrajectoryResponse(
                        id=str(traj.id),
                        match_id=traj.match_id,
                        point_id=traj.point_id,
                        player_id=traj.player_id,
                        shot_type=traj.shot_type,
                        trajectory_type=traj.trajectory_type,
                        num_points=traj.num_points,
                        duration_ms=traj.duration_ms,
                        raw_trajectory=traj.raw_trajectory,
                        metadata=traj.metadata_,
                        created_at=traj.created_at.isoformat(),
                    ),
                    similarity_score=similarity,
                )
            )

        return results

    except Exception as e:
        logger.error(f"Erro ao buscar trajetórias similares: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar trajetórias: {str(e)}"
        )


@router.get("/player/{player_id}/patterns", response_model=PlayerPatternsResponse)
async def get_player_patterns(
    player_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obter padrões de golpe de um jogador.

    Analisa todas as trajetórias do jogador e agrupa por tipo de golpe (forehand, backhand, etc.)
    e tipo de trajetória (cross_court, down_the_line, etc.).
    """
    try:
        patterns = await trajectory_service.get_player_shot_patterns(db=db, player_id=player_id)

        return PlayerPatternsResponse(
            player_id=patterns["player_id"],
            total_trajectories=patterns["total_trajectories"],
            shot_types=patterns["shot_types"],
            trajectory_types=patterns["trajectory_types"],
        )

    except Exception as e:
        logger.error(f"Erro ao obter padrões do jogador: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter padrões: {str(e)}"
        )


@router.get("/match/{match_id}", response_model=list[TrajectoryMatchResponse])
async def get_match_similar_trajectories(
    match_id: str,
    limit: int = 10,
    point_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Encontrar trajetórias de outras partidas similares às trajetórias de uma partida.

    Útil para comparar padrões de jogo entre diferentes partidas.
    """
    try:
        similar = await trajectory_service.find_similar_by_match(
            db=db,
            match_id=match_id,
            limit=limit,
            point_id=point_id,
        )

        # Converter para response
        results = []
        for source_traj, sim_traj, similarity in similar:
            results.append(
                TrajectoryMatchResponse(
                    source_trajectory=TrajectoryResponse(
                        id=str(source_traj.id),
                        match_id=source_traj.match_id,
                        point_id=source_traj.point_id,
                        player_id=source_traj.player_id,
                        shot_type=source_traj.shot_type,
                        trajectory_type=source_traj.trajectory_type,
                        num_points=source_traj.num_points,
                        duration_ms=source_traj.duration_ms,
                        raw_trajectory=source_traj.raw_trajectory,
                        metadata=source_traj.metadata_,
                        created_at=source_traj.created_at.isoformat(),
                    ),
                    similar_trajectory=TrajectoryResponse(
                        id=str(sim_traj.id),
                        match_id=sim_traj.match_id,
                        point_id=sim_traj.point_id,
                        player_id=sim_traj.player_id,
                        shot_type=sim_traj.shot_type,
                        trajectory_type=sim_traj.trajectory_type,
                        num_points=sim_traj.num_points,
                        duration_ms=sim_traj.duration_ms,
                        raw_trajectory=sim_traj.raw_trajectory,
                        metadata=sim_traj.metadata_,
                        created_at=sim_traj.created_at.isoformat(),
                    ),
                    similarity_score=similarity,
                )
            )

        return results

    except Exception as e:
        logger.error(f"Erro ao buscar trajetórias similares da partida: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar trajetórias: {str(e)}"
        )
