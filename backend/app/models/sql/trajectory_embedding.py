"""
SQLAlchemy model para armazenar embeddings de trajetórias de bola.
Usa pgvector para busca por similaridade.
"""
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class TrajectoryEmbedding(Base):
    """
    Embeddings de trajetórias de bola para busca por similaridade.

    Cada embedding representa uma sequência de posições da bola (trajetória)
    convertida em vetor de dimensão fixa para busca eficiente.
    """
    __tablename__ = "trajectory_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Referências
    match_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    point_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    player_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Metadata da trajetória
    shot_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # forehand, backhand, serve, volley
    trajectory_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # cross_court, down_the_line, lob, drop_shot
    num_points: Mapped[int] = mapped_column(Integer, nullable=False)  # quantidade de pontos na trajetória
    duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)  # duração em ms

    # Embedding vector (128 dimensões - suficiente para trajetórias 2D normalizadas)
    embedding = mapped_column(Vector(128), nullable=False)

    # Dados originais da trajetória (para referência)
    raw_trajectory: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Formato: {"points": [[x1,y1,t1], [x2,y2,t2], ...], "court_normalized": true}

    # Metadados adicionais
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_trajectory_match_player", "match_id", "player_id"),
        Index("ix_trajectory_shot_type", "shot_type"),
    )

    def __repr__(self) -> str:
        return f"<TrajectoryEmbedding(id={self.id}, match={self.match_id}, shot={self.shot_type})>"
