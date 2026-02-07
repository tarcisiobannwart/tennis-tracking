"""
Social Feed service para operacoes de logica de negocio do feed social.

Implementado para TT-130: Feed tipo timeline com publicacoes texto+foto,
cards de resultado de partida, reacoes (like/torcer), comentarios e compartilhamento.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime
import structlog
import uuid

from app.models.sql.social_feed import FeedPost, FeedReaction, FeedComment, PostType, ReactionType

logger = structlog.get_logger(__name__)


class SocialFeedService:
    """Service para operacoes relacionadas ao feed social."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_feed(
        self,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[uuid.UUID] = None,
        post_type: Optional[str] = None,
    ) -> Tuple[List[FeedPost], int]:
        """
        Obtem posts do feed com paginacao.

        Args:
            skip: Numero de registros a pular
            limit: Limite de registros
            user_id: Filtrar por usuario especifico (opcional)
            post_type: Filtrar por tipo de post (opcional)

        Returns:
            Tupla com lista de posts e total de registros
        """
        query = select(FeedPost).where(FeedPost.is_public == True).order_by(desc(FeedPost.created_at))

        # Aplicar filtros opcionais
        conditions = []
        if user_id:
            conditions.append(FeedPost.user_id == user_id)
        if post_type:
            conditions.append(FeedPost.post_type == post_type)

        if conditions:
            query = query.where(and_(*conditions))

        # Contar total
        count_query = select(func.count()).select_from(FeedPost).where(FeedPost.is_public == True)
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Aplicar paginacao
        query = query.offset(skip).limit(limit)

        # Carregar com relacionamentos
        query = query.options(
            selectinload(FeedPost.reactions),
            selectinload(FeedPost.comments)
        )

        result = await self.db.execute(query)
        posts = list(result.scalars().all())

        logger.info(
            "Feed obtido",
            total=total,
            returned=len(posts),
            skip=skip,
            limit=limit
        )

        return posts, total

    async def get_post(self, post_id: uuid.UUID) -> Optional[FeedPost]:
        """
        Obtem um post especifico por ID.

        Args:
            post_id: ID do post

        Returns:
            Post ou None se nao encontrado
        """
        query = (
            select(FeedPost)
            .where(FeedPost.id == post_id)
            .options(
                selectinload(FeedPost.reactions),
                selectinload(FeedPost.comments)
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_post(
        self,
        user_id: uuid.UUID,
        post_type: PostType,
        content: Optional[str] = None,
        image_url: Optional[str] = None,
        match_id: Optional[uuid.UUID] = None,
        is_public: bool = True,
    ) -> FeedPost:
        """
        Cria um novo post no feed.

        Args:
            user_id: ID do usuario que esta criando o post
            post_type: Tipo do post (text/photo/match_result)
            content: Conteudo textual (opcional)
            image_url: URL da imagem (opcional)
            match_id: ID da partida (para posts de resultado)
            is_public: Se o post e publico

        Returns:
            Post criado
        """
        post = FeedPost(
            user_id=user_id,
            post_type=post_type,
            content=content,
            image_url=image_url,
            match_id=match_id,
            is_public=is_public,
        )

        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)

        logger.info(
            "Post criado",
            post_id=post.id,
            user_id=user_id,
            post_type=post_type
        )

        return post

    async def delete_post(self, post_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Deleta um post do feed (apenas o proprio usuario pode deletar).

        Args:
            post_id: ID do post
            user_id: ID do usuario solicitante

        Returns:
            True se deletado, False se nao encontrado ou nao autorizado
        """
        post = await self.get_post(post_id)

        if not post or post.user_id != user_id:
            logger.warning(
                "Tentativa de deletar post nao autorizada",
                post_id=post_id,
                user_id=user_id
            )
            return False

        await self.db.delete(post)
        await self.db.commit()

        logger.info("Post deletado", post_id=post_id, user_id=user_id)
        return True

    async def react_to_post(
        self,
        post_id: uuid.UUID,
        user_id: uuid.UUID,
        reaction_type: ReactionType,
    ) -> FeedReaction:
        """
        Adiciona ou atualiza uma reacao a um post.

        Se o usuario ja reagiu ao post, atualiza o tipo de reacao.
        Se nao, cria uma nova reacao.

        Args:
            post_id: ID do post
            user_id: ID do usuario
            reaction_type: Tipo de reacao (like/cheer)

        Returns:
            Reacao criada ou atualizada
        """
        # Verificar se ja existe reacao
        query = select(FeedReaction).where(
            and_(
                FeedReaction.post_id == post_id,
                FeedReaction.user_id == user_id,
            )
        )
        result = await self.db.execute(query)
        existing_reaction = result.scalar_one_or_none()

        if existing_reaction:
            # Atualizar tipo de reacao se mudou
            old_type = existing_reaction.reaction_type
            if old_type != reaction_type:
                existing_reaction.reaction_type = reaction_type

                # Atualizar contadores do post
                post = await self.get_post(post_id)
                if post:
                    if old_type == ReactionType.LIKE:
                        post.likes_count = max(0, post.likes_count - 1)
                        post.cheers_count += 1
                    else:
                        post.cheers_count = max(0, post.cheers_count - 1)
                        post.likes_count += 1

                await self.db.commit()
                await self.db.refresh(existing_reaction)

                logger.info(
                    "Reacao atualizada",
                    post_id=post_id,
                    user_id=user_id,
                    old_type=old_type,
                    new_type=reaction_type
                )

            return existing_reaction

        # Criar nova reacao
        reaction = FeedReaction(
            post_id=post_id,
            user_id=user_id,
            reaction_type=reaction_type,
        )

        self.db.add(reaction)

        # Atualizar contador no post
        post = await self.get_post(post_id)
        if post:
            if reaction_type == ReactionType.LIKE:
                post.likes_count += 1
            else:
                post.cheers_count += 1

        await self.db.commit()
        await self.db.refresh(reaction)

        logger.info(
            "Reacao criada",
            post_id=post_id,
            user_id=user_id,
            reaction_type=reaction_type
        )

        return reaction

    async def remove_reaction(self, post_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Remove a reacao de um usuario a um post.

        Args:
            post_id: ID do post
            user_id: ID do usuario

        Returns:
            True se removido, False se nao havia reacao
        """
        # Buscar reacao existente
        query = select(FeedReaction).where(
            and_(
                FeedReaction.post_id == post_id,
                FeedReaction.user_id == user_id,
            )
        )
        result = await self.db.execute(query)
        reaction = result.scalar_one_or_none()

        if not reaction:
            return False

        # Atualizar contador no post
        post = await self.get_post(post_id)
        if post:
            if reaction.reaction_type == ReactionType.LIKE:
                post.likes_count = max(0, post.likes_count - 1)
            else:
                post.cheers_count = max(0, post.cheers_count - 1)

        await self.db.delete(reaction)
        await self.db.commit()

        logger.info(
            "Reacao removida",
            post_id=post_id,
            user_id=user_id,
            reaction_type=reaction.reaction_type
        )

        return True

    async def add_comment(
        self,
        post_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> FeedComment:
        """
        Adiciona um comentario a um post.

        Args:
            post_id: ID do post
            user_id: ID do usuario
            content: Conteudo do comentario

        Returns:
            Comentario criado
        """
        comment = FeedComment(
            post_id=post_id,
            user_id=user_id,
            content=content,
        )

        self.db.add(comment)

        # Atualizar contador no post
        post = await self.get_post(post_id)
        if post:
            post.comments_count += 1

        await self.db.commit()
        await self.db.refresh(comment)

        logger.info(
            "Comentario criado",
            comment_id=comment.id,
            post_id=post_id,
            user_id=user_id
        )

        return comment

    async def get_post_comments(
        self,
        post_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FeedComment]:
        """
        Obtem comentarios de um post com paginacao.

        Args:
            post_id: ID do post
            skip: Numero de registros a pular
            limit: Limite de registros

        Returns:
            Lista de comentarios
        """
        query = (
            select(FeedComment)
            .where(FeedComment.post_id == post_id)
            .order_by(FeedComment.created_at)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        comments = list(result.scalars().all())

        logger.info(
            "Comentarios obtidos",
            post_id=post_id,
            count=len(comments)
        )

        return comments

    async def delete_comment(
        self,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """
        Deleta um comentario (apenas o proprio usuario pode deletar).

        Args:
            comment_id: ID do comentario
            user_id: ID do usuario solicitante

        Returns:
            True se deletado, False se nao encontrado ou nao autorizado
        """
        query = select(FeedComment).where(FeedComment.id == comment_id)
        result = await self.db.execute(query)
        comment = result.scalar_one_or_none()

        if not comment or comment.user_id != user_id:
            logger.warning(
                "Tentativa de deletar comentario nao autorizada",
                comment_id=comment_id,
                user_id=user_id
            )
            return False

        post_id = comment.post_id

        # Atualizar contador no post
        post = await self.get_post(post_id)
        if post:
            post.comments_count = max(0, post.comments_count - 1)

        await self.db.delete(comment)
        await self.db.commit()

        logger.info("Comentario deletado", comment_id=comment_id, user_id=user_id)
        return True

    async def increment_share_count(self, post_id: uuid.UUID) -> bool:
        """
        Incrementa o contador de compartilhamentos de um post.

        Args:
            post_id: ID do post

        Returns:
            True se incrementado, False se post nao encontrado
        """
        post = await self.get_post(post_id)
        if not post:
            return False

        post.shares_count += 1
        await self.db.commit()

        logger.info("Contador de compartilhamentos incrementado", post_id=post_id)
        return True
