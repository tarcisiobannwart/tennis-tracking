"""
SQLAlchemy ORM models para social feed (feed social com resultados de partidas).

Implementado para TT-130: Feed tipo timeline com publicacoes texto+foto,
cards de resultado de partida, reacoes (like/torcer), comentarios e compartilhamento.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PostType(str, PyEnum):
    """Tipos de post no feed."""
    TEXT = "text"
    MATCH_RESULT = "match_result"
    PHOTO = "photo"
    TEXT_PHOTO = "text_photo"


class ReactionType(str, PyEnum):
    """Tipos de reacao a posts."""
    LIKE = "like"
    CHEER = "cheer"


class FeedPost(Base):
    """
    Modelo SQLAlchemy para tabela feed_posts.

    Representa uma publicacao no feed social, que pode ser:
    - Post de texto simples
    - Post com foto
    - Card de resultado de partida
    """

    __tablename__ = "feed_posts"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Usuario que criou o post
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo de post
    post_type: Mapped[str] = mapped_column(
        ENUM('text', 'match_result', 'photo', 'text_photo', name='post_type', create_type=False),
        nullable=False,
        default='text',
    )

    # Conteudo
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Referencia para partida (se for post de resultado)
    match_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    # Contadores (denormalizados para performance)
    likes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cheers_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shares_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Visibilidade
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    reactions = relationship(
        "FeedReaction",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    comments = relationship(
        "FeedComment",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Indices para performance
    __table_args__ = (
        Index("ix_feed_posts_user_created", "user_id", "created_at"),
        Index("ix_feed_posts_type_created", "post_type", "created_at"),
        Index("ix_feed_posts_public_created", "is_public", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<FeedPost(id={self.id}, user_id={self.user_id}, type={self.post_type})>"


class FeedReaction(Base):
    """
    Modelo SQLAlchemy para tabela feed_reactions.

    Representa uma reacao (like/torcer) a um post.
    """

    __tablename__ = "feed_reactions"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Post e usuario
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feed_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo de reacao
    reaction_type: Mapped[str] = mapped_column(
        ENUM('like', 'cheer', name='reaction_type', create_type=False),
        nullable=False,
        default='like',
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    post = relationship("FeedPost", back_populates="reactions")

    # Indices e constraints
    __table_args__ = (
        Index("ix_feed_reactions_post_user", "post_id", "user_id", unique=True),
        Index("ix_feed_reactions_user", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<FeedReaction(id={self.id}, post_id={self.post_id}, type={self.reaction_type})>"


class FeedComment(Base):
    """
    Modelo SQLAlchemy para tabela feed_comments.

    Representa um comentario em um post do feed.
    """

    __tablename__ = "feed_comments"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Post e usuario
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feed_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Conteudo do comentario
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    post = relationship("FeedPost", back_populates="comments")

    # Indices
    __table_args__ = (
        Index("ix_feed_comments_post_created", "post_id", "created_at"),
        Index("ix_feed_comments_user", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<FeedComment(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"
