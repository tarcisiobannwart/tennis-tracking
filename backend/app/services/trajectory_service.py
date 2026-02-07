"""
Serviço para gerenciamento de embeddings de trajetórias de bola.

Implementa busca por similaridade usando pgvector e análise de padrões de golpes.
"""

import logging
from typing import Any
import uuid
import numpy as np
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sql.trajectory_embedding import TrajectoryEmbedding

logger = logging.getLogger(__name__)


def encode_trajectory(points: list[list[float]], target_dim: int = 128) -> list[float]:
    """
    Converte trajetória raw (lista de [x,y] ou [x,y,t]) para embedding de dimensão fixa.

    Usa técnica determinística:
    1. Normaliza coordenadas para [0,1]
    2. Amostra/interpola para tamanho fixo (64 pontos)
    3. Flatten [x1,y1,x2,y2,...] = 128 dimensões
    4. Normaliza L2 para cosine similarity

    Args:
        points: Lista de pontos [[x1,y1], [x2,y2], ...] ou [[x1,y1,t1], [x2,y2,t2], ...]
        target_dim: Dimensão final do embedding (default 128)

    Returns:
        Embedding normalizado de dimensão target_dim
    """
    if not points:
        return [0.0] * target_dim

    # Converter para numpy array e pegar apenas x,y (ignorar t se presente)
    arr = np.array(points, dtype=np.float32)
    if arr.shape[1] >= 2:
        arr = arr[:, :2]  # Pega apenas x,y

    # Normalizar coordenadas para [0,1]
    min_vals = arr.min(axis=0)
    max_vals = arr.max(axis=0)
    range_vals = max_vals - min_vals
    # Evitar divisão por zero
    range_vals = np.where(range_vals == 0, 1.0, range_vals)
    arr_normalized = (arr - min_vals) / range_vals

    # Tamanho alvo de pontos (target_dim / 2 porque temos x,y)
    target_points = target_dim // 2

    # Resample para tamanho fixo usando interpolação linear
    if len(arr_normalized) > target_points:
        # Downsample
        indices = np.linspace(0, len(arr_normalized) - 1, target_points, dtype=int)
        arr_resampled = arr_normalized[indices]
    elif len(arr_normalized) < target_points:
        # Upsample via interpolação linear
        old_indices = np.arange(len(arr_normalized))
        new_indices = np.linspace(0, len(arr_normalized) - 1, target_points)
        arr_resampled = np.zeros((target_points, 2))
        arr_resampled[:, 0] = np.interp(new_indices, old_indices, arr_normalized[:, 0])
        arr_resampled[:, 1] = np.interp(new_indices, old_indices, arr_normalized[:, 1])
    else:
        arr_resampled = arr_normalized

    # Flatten para vetor 1D
    embedding = arr_resampled.flatten()

    # Normalização L2 para cosine similarity
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm

    return embedding.tolist()


async def store_trajectory(
    db: AsyncSession,
    match_id: str,
    embedding: list[float],
    raw_trajectory: dict | None = None,
    point_id: str | None = None,
    player_id: str | None = None,
    shot_type: str | None = None,
    trajectory_type: str | None = None,
    duration_ms: float | None = None,
    metadata: dict | None = None,
) -> TrajectoryEmbedding:
    """
    Salvar embedding de trajetória no banco de dados.

    Args:
        db: Sessão do banco de dados
        match_id: ID da partida
        embedding: Vetor de embedding (128 dimensões)
        raw_trajectory: Dados originais da trajetória
        point_id: ID do ponto (opcional)
        player_id: ID do jogador (opcional)
        shot_type: Tipo de golpe (forehand, backhand, serve, volley)
        trajectory_type: Tipo de trajetória (cross_court, down_the_line, lob, drop_shot)
        duration_ms: Duração em milissegundos
        metadata: Metadados adicionais

    Returns:
        TrajectoryEmbedding criado
    """
    num_points = 0
    if raw_trajectory and "points" in raw_trajectory:
        num_points = len(raw_trajectory["points"])

    trajectory_embedding = TrajectoryEmbedding(
        match_id=match_id,
        point_id=point_id,
        player_id=player_id,
        shot_type=shot_type,
        trajectory_type=trajectory_type,
        num_points=num_points,
        duration_ms=duration_ms,
        embedding=embedding,
        raw_trajectory=raw_trajectory,
        metadata_=metadata,
    )

    db.add(trajectory_embedding)
    await db.commit()
    await db.refresh(trajectory_embedding)

    logger.info(f"Trajetória armazenada: {trajectory_embedding.id} (match={match_id}, player={player_id})")
    return trajectory_embedding


async def find_similar(
    db: AsyncSession,
    embedding: list[float],
    limit: int = 10,
    threshold: float = 0.8,
    shot_type: str | None = None,
    exclude_match_id: str | None = None,
) -> list[tuple[TrajectoryEmbedding, float]]:
    """
    Buscar trajetórias similares usando cosine distance.

    Args:
        db: Sessão do banco de dados
        embedding: Vetor de embedding de query
        limit: Número máximo de resultados
        threshold: Limite de similaridade (0-1, onde 1 é idêntico)
        shot_type: Filtrar por tipo de golpe (opcional)
        exclude_match_id: Excluir trajetórias de uma partida específica

    Returns:
        Lista de tuplas (TrajectoryEmbedding, similarity_score)
    """
    # Cosine distance: 0 = idêntico, 2 = opostos
    # Convertemos para similarity: (2 - distance) / 2 => [0,1]
    distance_threshold = 2 * (1 - threshold)

    query = select(
        TrajectoryEmbedding,
        TrajectoryEmbedding.embedding.cosine_distance(embedding).label("distance")
    )

    # Aplicar filtros
    if shot_type:
        query = query.where(TrajectoryEmbedding.shot_type == shot_type)
    if exclude_match_id:
        query = query.where(TrajectoryEmbedding.match_id != exclude_match_id)

    # Filtrar por threshold e ordenar por distância
    query = query.where(
        TrajectoryEmbedding.embedding.cosine_distance(embedding) < distance_threshold
    ).order_by("distance").limit(limit)

    result = await db.execute(query)
    rows = result.all()

    # Converter distância para similaridade
    results = []
    for traj, distance in rows:
        similarity = (2 - distance) / 2  # Converter para [0,1]
        results.append((traj, similarity))

    logger.info(f"Encontradas {len(results)} trajetórias similares (threshold={threshold})")
    return results


async def find_similar_by_match(
    db: AsyncSession,
    match_id: str,
    limit: int = 10,
    point_id: str | None = None,
) -> list[tuple[TrajectoryEmbedding, TrajectoryEmbedding, float]]:
    """
    Encontrar trajetórias de outras partidas similares às trajetórias de uma partida.

    Args:
        db: Sessão do banco de dados
        match_id: ID da partida de referência
        limit: Número máximo de resultados por trajetória
        point_id: Filtrar por ponto específico (opcional)

    Returns:
        Lista de tuplas (trajetória_origem, trajetória_similar, similarity_score)
    """
    # Buscar trajetórias da partida de referência
    query = select(TrajectoryEmbedding).where(TrajectoryEmbedding.match_id == match_id)
    if point_id:
        query = query.where(TrajectoryEmbedding.point_id == point_id)

    result = await db.execute(query)
    source_trajectories = result.scalars().all()

    if not source_trajectories:
        logger.warning(f"Nenhuma trajetória encontrada para match_id={match_id}")
        return []

    # Para cada trajetória, buscar similares
    all_results = []
    for source_traj in source_trajectories:
        similar = await find_similar(
            db,
            source_traj.embedding,
            limit=limit,
            exclude_match_id=match_id,
            shot_type=source_traj.shot_type,
        )
        for sim_traj, similarity in similar:
            all_results.append((source_traj, sim_traj, similarity))

    # Ordenar por similaridade
    all_results.sort(key=lambda x: x[2], reverse=True)

    logger.info(f"Encontradas {len(all_results)} trajetórias similares para match={match_id}")
    return all_results[:limit]


async def find_similar_by_player(
    db: AsyncSession,
    player_id: str,
    shot_type: str | None = None,
    limit: int = 10,
) -> list[tuple[TrajectoryEmbedding, TrajectoryEmbedding, float]]:
    """
    Buscar padrões de golpe de um jogador comparando com outros jogadores.

    Args:
        db: Sessão do banco de dados
        player_id: ID do jogador
        shot_type: Tipo de golpe (forehand, backhand, serve, volley)
        limit: Número máximo de resultados

    Returns:
        Lista de tuplas (trajetória_jogador, trajetória_similar_outros, similarity_score)
    """
    # Buscar trajetórias do jogador
    query = select(TrajectoryEmbedding).where(TrajectoryEmbedding.player_id == player_id)
    if shot_type:
        query = query.where(TrajectoryEmbedding.shot_type == shot_type)

    result = await db.execute(query)
    player_trajectories = result.scalars().all()

    if not player_trajectories:
        logger.warning(f"Nenhuma trajetória encontrada para player_id={player_id}")
        return []

    # Para cada trajetória do jogador, buscar similares de outros jogadores
    all_results = []
    for player_traj in player_trajectories:
        # Buscar similares excluindo o próprio jogador
        similar_query = select(
            TrajectoryEmbedding,
            TrajectoryEmbedding.embedding.cosine_distance(player_traj.embedding).label("distance")
        ).where(
            TrajectoryEmbedding.player_id != player_id
        )

        if shot_type:
            similar_query = similar_query.where(TrajectoryEmbedding.shot_type == shot_type)

        similar_query = similar_query.order_by("distance").limit(5)

        similar_result = await db.execute(similar_query)
        similar_rows = similar_result.all()

        for sim_traj, distance in similar_rows:
            similarity = (2 - distance) / 2
            all_results.append((player_traj, sim_traj, similarity))

    # Ordenar por similaridade
    all_results.sort(key=lambda x: x[2], reverse=True)

    logger.info(f"Encontrados {len(all_results)} padrões similares para player={player_id}")
    return all_results[:limit]


async def get_player_shot_patterns(
    db: AsyncSession,
    player_id: str,
) -> dict[str, Any]:
    """
    Análise de padrões de golpe do jogador.

    Agrupa trajetórias por shot_type e calcula estatísticas.

    Args:
        db: Sessão do banco de dados
        player_id: ID do jogador

    Returns:
        Dicionário com padrões de golpe:
        {
            "player_id": str,
            "total_trajectories": int,
            "shot_types": {
                "forehand": {"count": int, "avg_duration_ms": float, "avg_points": float},
                "backhand": {...},
                ...
            },
            "trajectory_types": {
                "cross_court": {"count": int},
                ...
            }
        }
    """
    # Buscar todas as trajetórias do jogador
    query = select(TrajectoryEmbedding).where(TrajectoryEmbedding.player_id == player_id)
    result = await db.execute(query)
    trajectories = result.scalars().all()

    if not trajectories:
        return {
            "player_id": player_id,
            "total_trajectories": 0,
            "shot_types": {},
            "trajectory_types": {},
        }

    # Agrupar por shot_type
    shot_patterns = {}
    trajectory_patterns = {}

    for traj in trajectories:
        # Shot type stats
        if traj.shot_type:
            if traj.shot_type not in shot_patterns:
                shot_patterns[traj.shot_type] = {
                    "count": 0,
                    "total_duration": 0,
                    "total_points": 0,
                }
            shot_patterns[traj.shot_type]["count"] += 1
            if traj.duration_ms:
                shot_patterns[traj.shot_type]["total_duration"] += traj.duration_ms
            shot_patterns[traj.shot_type]["total_points"] += traj.num_points

        # Trajectory type stats
        if traj.trajectory_type:
            if traj.trajectory_type not in trajectory_patterns:
                trajectory_patterns[traj.trajectory_type] = {"count": 0}
            trajectory_patterns[traj.trajectory_type]["count"] += 1

    # Calcular médias
    for shot_type, stats in shot_patterns.items():
        count = stats["count"]
        shot_patterns[shot_type]["avg_duration_ms"] = stats["total_duration"] / count if count > 0 else 0
        shot_patterns[shot_type]["avg_points"] = stats["total_points"] / count if count > 0 else 0
        # Remover totais temporários
        del shot_patterns[shot_type]["total_duration"]
        del shot_patterns[shot_type]["total_points"]

    result_dict = {
        "player_id": player_id,
        "total_trajectories": len(trajectories),
        "shot_types": shot_patterns,
        "trajectory_types": trajectory_patterns,
    }

    logger.info(f"Análise de padrões para player={player_id}: {len(trajectories)} trajetórias")
    return result_dict
