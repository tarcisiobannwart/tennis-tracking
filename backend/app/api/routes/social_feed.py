"""
Social Feed API routes.

Implementado para TT-130: Feed tipo timeline com publicacoes texto+foto,
cards de resultado de partida, reacoes (like/torcer), comentarios e compartilhamento.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.social_feed_service import SocialFeedService
from app.models.sql.social_feed import PostType, ReactionType

router = APIRouter()


# Schemas de requisicao/resposta
class CreatePostRequest(BaseModel):
    """Requisicao para criar um novo post."""
    post_type: PostType
    content: Optional[str] = None
    image_url: Optional[str] = None
    match_id: Optional[uuid.UUID] = None
    is_public: bool = True


class ReactToPostRequest(BaseModel):
    """Requisicao para reagir a um post."""
    reaction_type: ReactionType


class AddCommentRequest(BaseModel):
    """Requisicao para adicionar um comentario."""
    content: str = Field(..., min_length=1, max_length=2000)


class ReactionResponse(BaseModel):
    """Resposta de reacao."""
    id: uuid.UUID
    post_id: uuid.UUID
    user_id: uuid.UUID
    reaction_type: str
    created_at: str


class CommentResponse(BaseModel):
    """Resposta de comentario."""
    id: uuid.UUID
    post_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: str
    updated_at: str


class PostResponse(BaseModel):
    """Resposta de post."""
    id: uuid.UUID
    user_id: uuid.UUID
    post_type: str
    content: Optional[str]
    image_url: Optional[str]
    match_id: Optional[uuid.UUID]
    likes_count: int
    cheers_count: int
    comments_count: int
    shares_count: int
    is_public: bool
    created_at: str
    updated_at: str


class FeedResponse(BaseModel):
    """Resposta do feed com paginacao."""
    data: List[PostResponse]
    total: int
    page: int
    limit: int
    total_pages: int


@router.get("/", response_model=FeedResponse)
async def get_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[uuid.UUID] = Query(None),
    post_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtem timeline do feed social com paginacao.

    Args:
        page: Numero da pagina (inicia em 1)
        limit: Itens por pagina (1-100)
        user_id: Filtrar por usuario especifico (opcional)
        post_type: Filtrar por tipo de post (opcional)
        db: Sessao do banco de dados

    Returns:
        FeedResponse com posts paginados
    """
    service = SocialFeedService(db)

    skip = (page - 1) * limit
    posts, total = await service.get_feed(
        skip=skip,
        limit=limit,
        user_id=user_id,
        post_type=post_type,
    )

    # Formatar resposta
    posts_data = [
        PostResponse(
            id=post.id,
            user_id=post.user_id,
            post_type=post.post_type,
            content=post.content,
            image_url=post.image_url,
            match_id=post.match_id,
            likes_count=post.likes_count,
            cheers_count=post.cheers_count,
            comments_count=post.comments_count,
            shares_count=post.shares_count,
            is_public=post.is_public,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
        )
        for post in posts
    ]

    total_pages = (total + limit - 1) // limit

    return FeedResponse(
        data=posts_data,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.post("/", status_code=201)
async def create_post(
    post_data: CreatePostRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cria um novo post no feed.

    Args:
        post_data: Dados do post
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Post criado
    """
    service = SocialFeedService(db)

    # Validacoes
    if post_data.post_type == PostType.MATCH_RESULT and not post_data.match_id:
        raise HTTPException(
            status_code=400,
            detail="match_id e obrigatorio para posts de resultado de partida"
        )

    user_id = uuid.UUID(str(current_user.id))

    post = await service.create_post(
        user_id=user_id,
        post_type=post_data.post_type,
        content=post_data.content,
        image_url=post_data.image_url,
        match_id=post_data.match_id,
        is_public=post_data.is_public,
    )

    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        post_type=post.post_type,
        content=post.content,
        image_url=post.image_url,
        match_id=post.match_id,
        likes_count=post.likes_count,
        cheers_count=post.cheers_count,
        comments_count=post.comments_count,
        shares_count=post.shares_count,
        is_public=post.is_public,
        created_at=post.created_at.isoformat(),
        updated_at=post.updated_at.isoformat(),
    )


@router.get("/{post_id}")
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtem um post especifico por ID.

    Args:
        post_id: ID do post
        db: Sessao do banco de dados

    Returns:
        Post encontrado
    """
    service = SocialFeedService(db)

    post = await service.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post nao encontrado")

    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        post_type=post.post_type,
        content=post.content,
        image_url=post.image_url,
        match_id=post.match_id,
        likes_count=post.likes_count,
        cheers_count=post.cheers_count,
        comments_count=post.comments_count,
        shares_count=post.shares_count,
        is_public=post.is_public,
        created_at=post.created_at.isoformat(),
        updated_at=post.updated_at.isoformat(),
    )


@router.delete("/{post_id}")
async def delete_post(
    post_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deleta um post (apenas o proprio usuario pode deletar).

    Args:
        post_id: ID do post
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Mensagem de sucesso
    """
    service = SocialFeedService(db)

    user_id = uuid.UUID(str(current_user.id))

    success = await service.delete_post(post_id, user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Post nao encontrado ou nao autorizado"
        )

    return {"message": "Post deletado com sucesso"}


@router.post("/{post_id}/react")
async def react_to_post(
    post_id: uuid.UUID,
    reaction_data: ReactToPostRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Adiciona ou atualiza uma reacao (like/torcer) a um post.

    Args:
        post_id: ID do post
        reaction_data: Tipo de reacao
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Reacao criada ou atualizada
    """
    service = SocialFeedService(db)

    # Verificar se post existe
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post nao encontrado")

    user_id = uuid.UUID(str(current_user.id))

    reaction = await service.react_to_post(
        post_id=post_id,
        user_id=user_id,
        reaction_type=reaction_data.reaction_type,
    )

    return ReactionResponse(
        id=reaction.id,
        post_id=reaction.post_id,
        user_id=reaction.user_id,
        reaction_type=reaction.reaction_type,
        created_at=reaction.created_at.isoformat(),
    )


@router.delete("/{post_id}/react")
async def remove_reaction(
    post_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a reacao do usuario a um post.

    Args:
        post_id: ID do post
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Mensagem de sucesso
    """
    service = SocialFeedService(db)

    user_id = uuid.UUID(str(current_user.id))

    success = await service.remove_reaction(post_id, user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Reacao nao encontrada"
        )

    return {"message": "Reacao removida com sucesso"}


@router.post("/{post_id}/comment")
async def add_comment(
    post_id: uuid.UUID,
    comment_data: AddCommentRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Adiciona um comentario a um post.

    Args:
        post_id: ID do post
        comment_data: Conteudo do comentario
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Comentario criado
    """
    service = SocialFeedService(db)

    # Verificar se post existe
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post nao encontrado")

    user_id = uuid.UUID(str(current_user.id))

    comment = await service.add_comment(
        post_id=post_id,
        user_id=user_id,
        content=comment_data.content,
    )

    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        content=comment.content,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat(),
    )


@router.get("/{post_id}/comments")
async def get_post_comments(
    post_id: uuid.UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtem comentarios de um post com paginacao.

    Args:
        post_id: ID do post
        page: Numero da pagina
        limit: Itens por pagina
        db: Sessao do banco de dados

    Returns:
        Lista de comentarios
    """
    service = SocialFeedService(db)

    skip = (page - 1) * limit
    comments = await service.get_post_comments(
        post_id=post_id,
        skip=skip,
        limit=limit,
    )

    comments_data = [
        CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            user_id=comment.user_id,
            content=comment.content,
            created_at=comment.created_at.isoformat(),
            updated_at=comment.updated_at.isoformat(),
        )
        for comment in comments
    ]

    return {"data": comments_data}


@router.delete("/{post_id}/comment/{comment_id}")
async def delete_comment(
    post_id: uuid.UUID,
    comment_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deleta um comentario (apenas o proprio usuario pode deletar).

    Args:
        post_id: ID do post
        comment_id: ID do comentario
        current_user: Usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Mensagem de sucesso
    """
    service = SocialFeedService(db)

    user_id = uuid.UUID(str(current_user.id))

    success = await service.delete_comment(comment_id, user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Comentario nao encontrado ou nao autorizado"
        )

    return {"message": "Comentario deletado com sucesso"}


@router.post("/{post_id}/share")
async def share_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Incrementa o contador de compartilhamentos de um post.

    Args:
        post_id: ID do post
        db: Sessao do banco de dados

    Returns:
        Mensagem de sucesso
    """
    service = SocialFeedService(db)

    success = await service.increment_share_count(post_id)

    if not success:
        raise HTTPException(status_code=404, detail="Post nao encontrado")

    return {"message": "Post compartilhado com sucesso"}
