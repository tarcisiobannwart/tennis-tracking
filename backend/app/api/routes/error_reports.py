"""
Rotas para error reporting automatico.

POST / - Endpoint publico (sem auth) para receber erros do frontend/backend
GET / - Endpoint admin para listar error reports
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_admin
from app.core.database import get_db
from app.services.error_report_service import error_report_service


router = APIRouter()


# --- Schemas ---

class ErrorReportCreate(BaseModel):
    """Schema para criacao de error report."""
    source: str = Field(..., description="Origem: 'frontend' ou 'backend'")
    error_type: str = Field(..., max_length=255, description="Tipo do erro (ex: TypeError)")
    message: str = Field(..., max_length=2000, description="Mensagem do erro")
    stack_trace: Optional[str] = Field(None, max_length=10000, description="Stack trace")
    context: Optional[dict] = Field(None, description="Contexto adicional (URL, method, etc.)")


class ErrorReportResponse(BaseModel):
    """Schema de resposta do error report."""
    id: str
    fingerprint: str
    source: str
    error_type: str
    message: str
    jira_issue_key: Optional[str] = None
    occurrence_count: int
    status: str
    created_at: str
    last_seen_at: str

    class Config:
        from_attributes = True


# --- Endpoints ---

@router.post(
    "",
    status_code=201,
    summary="Reportar erro",
    description="Endpoint publico para receber erros automaticos do frontend e backend.",
)
async def create_error_report(
    payload: ErrorReportCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Recebe erro e processa:
    1. Gera fingerprint SHA256
    2. Verifica duplicata
    3. Se novo: cria issue no Jira (respeitando rate limit)
    4. Se duplicata: incrementa count + comentario no Jira
    """
    report = await error_report_service.report_error(
        db=db,
        source=payload.source,
        error_type=payload.error_type,
        message=payload.message,
        stack_trace=payload.stack_trace,
        context=payload.context,
    )

    if report is None:
        return {"status": "skipped", "message": "Error reporting desabilitado ou falha interna"}

    return {
        "status": "ok",
        "fingerprint": report.fingerprint,
        "jira_issue_key": report.jira_issue_key,
        "occurrence_count": report.occurrence_count,
        "is_duplicate": report.occurrence_count > 1,
    }


@router.get(
    "",
    summary="Listar error reports (admin)",
    description="Lista error reports com filtros. Requer role admin.",
)
async def list_error_reports(
    source: Optional[str] = Query(None, description="Filtrar por source: frontend/backend"),
    status: Optional[str] = Query(None, description="Filtrar por status: open/reported/resolved/ignored"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_admin),
):
    """Lista error reports para painel admin."""
    reports = await error_report_service.get_reports(
        db=db,
        source=source,
        status=status,
        limit=limit,
        offset=offset,
    )
    total = await error_report_service.get_report_count(
        db=db,
        source=source,
        status=status,
    )

    return {
        "items": [
            {
                "id": str(r.id),
                "fingerprint": r.fingerprint,
                "source": r.source.value if r.source else r.source,
                "error_type": r.error_type,
                "message": r.message[:200],
                "jira_issue_key": r.jira_issue_key,
                "occurrence_count": r.occurrence_count,
                "status": r.status.value if r.status else r.status,
                "context": r.context,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "last_seen_at": r.last_seen_at.isoformat() if r.last_seen_at else None,
            }
            for r in reports
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
