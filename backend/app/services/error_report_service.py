"""
Service principal para captura e report de erros automaticos.

Responsabilidades:
- Gerar fingerprint SHA256 para deduplicacao
- Verificar duplicatas no PostgreSQL
- Aplicar rate limit de criacao de issues
- Criar bugs no Jira via JiraService
- Persistir error reports na tabela error_reports
"""

import hashlib
import re
import traceback
from datetime import datetime, timedelta, timezone
from typing import Optional

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.sql.error_report import ErrorReport, ErrorReportStatusEnum, ErrorSourceEnum
from app.services.jira_service import jira_service


logger = structlog.get_logger(__name__)


class ErrorReportService:
    """Service para captura automatica de erros e integracao com Jira."""

    @staticmethod
    def normalize_message(message: str) -> str:
        """
        Normaliza mensagem de erro removendo valores variaveis.

        Remove:
        - IDs hexadecimais (UUIDs, hashes)
        - Numeros puros
        - Timestamps
        """
        # Remove UUIDs
        normalized = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "<UUID>",
            message,
            flags=re.IGNORECASE,
        )
        # Remove hashes hex longos (>8 chars)
        normalized = re.sub(r"\b[0-9a-f]{8,}\b", "<HEX>", normalized, flags=re.IGNORECASE)
        # Remove numeros puros (IDs numericos, portas, etc.)
        normalized = re.sub(r"\b\d{4,}\b", "<NUM>", normalized)
        return normalized

    @staticmethod
    def extract_location_from_stack(stack_trace: Optional[str]) -> str:
        """Extrai arquivo:funcao do topo do stack trace."""
        if not stack_trace:
            return "unknown"

        # Padroes Python: File "xxx.py", line N, in func
        python_match = re.search(
            r'File "([^"]+)", line \d+, in (\w+)',
            stack_trace,
        )
        if python_match:
            filepath = python_match.group(1).split("/")[-1]
            func_name = python_match.group(2)
            return f"{filepath}:{func_name}"

        # Padroes JavaScript: at funcName (file.js:line:col)
        js_match = re.search(
            r"at (\S+) \(([^)]+)\)",
            stack_trace,
        )
        if js_match:
            func_name = js_match.group(1)
            file_info = js_match.group(2).split("/")[-1]
            return f"{file_info}:{func_name}"

        return "unknown"

    def generate_fingerprint(
        self,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None,
    ) -> str:
        """
        Gera fingerprint SHA256 para deduplicacao.

        Compoe: error_type + mensagem_normalizada + arquivo:funcao
        """
        normalized_msg = self.normalize_message(message)
        location = self.extract_location_from_stack(stack_trace)
        raw = f"{error_type}|{normalized_msg}|{location}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def check_duplicate(
        self,
        db: AsyncSession,
        fingerprint: str,
    ) -> Optional[ErrorReport]:
        """Verifica se ja existe um error report com este fingerprint."""
        result = await db.execute(
            select(ErrorReport).where(
                ErrorReport.fingerprint == fingerprint,
                ErrorReport.status.in_([
                    ErrorReportStatusEnum.open,
                    ErrorReportStatusEnum.reported,
                ]),
            )
        )
        return result.scalar_one_or_none()

    async def check_rate_limit(
        self,
        db: AsyncSession,
    ) -> bool:
        """
        Verifica se o rate limit de criacao de issues Jira foi atingido.

        Returns:
            True se ainda pode criar issues (dentro do limite).
        """
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        result = await db.execute(
            select(func.count(ErrorReport.id)).where(
                ErrorReport.created_at >= one_hour_ago,
                ErrorReport.jira_issue_key.isnot(None),
            )
        )
        count = result.scalar() or 0
        limit = settings.JIRA_ERROR_REPORT_RATE_LIMIT
        if count >= limit:
            logger.warning(
                "Rate limit de error reports atingido",
                count=count,
                limit=limit,
            )
            return False
        return True

    async def report_error(
        self,
        db: AsyncSession,
        source: str,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> Optional[ErrorReport]:
        """
        Processa um erro: dedup, rate limit, cria Jira issue e persiste.

        Returns:
            ErrorReport criado/atualizado ou None se desabilitado/erro.
        """
        if not settings.JIRA_ERROR_REPORT_ENABLED:
            return None

        try:
            fingerprint = self.generate_fingerprint(error_type, message, stack_trace)

            # Verificar duplicata
            existing = await self.check_duplicate(db, fingerprint)
            if existing:
                return await self._handle_duplicate(db, existing)

            # Verificar rate limit
            within_limit = await self.check_rate_limit(db)

            # Criar issue no Jira (se dentro do limite)
            jira_issue_key = None
            report_status = ErrorReportStatusEnum.open

            if within_limit:
                summary = self._build_summary(error_type, message)
                priority = "High" if source == "backend" else "Medium"

                jira_issue_key = await jira_service.create_bug(
                    summary=summary,
                    error_type=error_type,
                    message=message,
                    stack_trace=stack_trace,
                    context=context,
                    fingerprint=fingerprint,
                    source=source,
                    priority=priority,
                )
                if jira_issue_key:
                    report_status = ErrorReportStatusEnum.reported

            # Persistir error report
            error_source = (
                ErrorSourceEnum.frontend if source == "frontend"
                else ErrorSourceEnum.backend
            )
            error_report = ErrorReport(
                fingerprint=fingerprint,
                source=error_source,
                error_type=error_type,
                message=message[:2000],
                stack_trace=stack_trace[:10000] if stack_trace else None,
                jira_issue_key=jira_issue_key,
                occurrence_count=1,
                status=report_status,
                context=context,
            )
            db.add(error_report)
            await db.flush()

            logger.info(
                "Error report criado",
                fingerprint=fingerprint[:12],
                jira_issue_key=jira_issue_key,
                source=source,
                error_type=error_type,
            )
            return error_report

        except Exception as e:
            logger.error(
                "Falha ao processar error report",
                error=str(e),
                source=source,
                error_type=error_type,
            )
            return None

    async def report_exception(
        self,
        db: AsyncSession,
        exc: Exception,
        request_path: Optional[str] = None,
        request_method: Optional[str] = None,
    ) -> Optional[ErrorReport]:
        """
        Atalho para reportar exceptions Python do backend.

        Extrai tipo, mensagem e stack trace da exception.
        """
        error_type = type(exc).__name__
        message = str(exc)
        stack_trace = traceback.format_exc()

        context = {}
        if request_path:
            context["path"] = request_path
        if request_method:
            context["method"] = request_method

        return await self.report_error(
            db=db,
            source="backend",
            error_type=error_type,
            message=message,
            stack_trace=stack_trace,
            context=context if context else None,
        )

    async def _handle_duplicate(
        self,
        db: AsyncSession,
        existing: ErrorReport,
    ) -> ErrorReport:
        """Incrementa contagem e adiciona comentario no Jira para duplicata."""
        new_count = existing.occurrence_count + 1

        await db.execute(
            update(ErrorReport)
            .where(ErrorReport.id == existing.id)
            .values(
                occurrence_count=new_count,
                last_seen_at=func.now(),
            )
        )
        await db.flush()

        # Adicionar comentario no Jira (se tiver issue)
        if existing.jira_issue_key:
            await jira_service.add_comment(
                issue_key=existing.jira_issue_key,
                occurrence_count=new_count,
            )

        logger.info(
            "Error report duplicado atualizado",
            fingerprint=existing.fingerprint[:12],
            occurrence_count=new_count,
            jira_issue_key=existing.jira_issue_key,
        )

        # Refresh para retornar estado atualizado
        await db.refresh(existing)
        return existing

    @staticmethod
    def _build_summary(error_type: str, message: str) -> str:
        """Constroi summary para issue Jira (max 80 chars de mensagem)."""
        truncated_msg = message[:80] + ("..." if len(message) > 80 else "")
        return f"[AUTO] {error_type}: {truncated_msg}"

    async def get_reports(
        self,
        db: AsyncSession,
        source: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ErrorReport]:
        """Lista error reports com filtros opcionais."""
        query = select(ErrorReport).order_by(ErrorReport.last_seen_at.desc())

        if source:
            query = query.where(ErrorReport.source == source)
        if status:
            query = query.where(ErrorReport.status == status)

        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_report_count(
        self,
        db: AsyncSession,
        source: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """Conta error reports com filtros opcionais."""
        query = select(func.count(ErrorReport.id))

        if source:
            query = query.where(ErrorReport.source == source)
        if status:
            query = query.where(ErrorReport.status == status)

        result = await db.execute(query)
        return result.scalar() or 0


error_report_service = ErrorReportService()
