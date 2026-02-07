"""
Service async para integracao com Jira REST API.

Usa httpx para criar bugs, adicionar comentarios e buscar issues.
Formato de descricao: Atlassian Document Format (ADF).
"""

import httpx
import structlog
from typing import Optional

from app.core.config import settings


logger = structlog.get_logger(__name__)


class JiraService:
    """Service para operacoes async na Jira REST API v3."""

    def __init__(self):
        self._base_url = ""
        self._auth = ("", "")
        self._project_key = ""

    def _get_client(self) -> httpx.AsyncClient:
        """Cria httpx client com autenticacao basica."""
        return httpx.AsyncClient(
            base_url=f"{settings.JIRA_BASE_URL}/rest/api/3",
            auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

    def _build_adf_description(
        self,
        error_type: str,
        message: str,
        stack_trace: Optional[str],
        context: Optional[dict],
        fingerprint: str,
    ) -> dict:
        """Constroi descricao em Atlassian Document Format (ADF)."""
        content = []

        # Secao: Error Details
        content.append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": [{"type": "text", "text": "Error Details"}],
        })
        content.append({
            "type": "table",
            "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
            "content": [
                self._adf_table_row("Type", error_type),
                self._adf_table_row("Message", message[:500]),
                self._adf_table_row("Fingerprint", fingerprint),
            ],
        })

        # Secao: Stack Trace
        if stack_trace:
            content.append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Stack Trace"}],
            })
            content.append({
                "type": "codeBlock",
                "attrs": {"language": "python"},
                "content": [{"type": "text", "text": stack_trace[:5000]}],
            })

        # Secao: Context
        if context:
            content.append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Context"}],
            })
            rows = []
            for key, value in context.items():
                rows.append(self._adf_table_row(key, str(value)[:200]))
            if rows:
                content.append({
                    "type": "table",
                    "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
                    "content": rows,
                })

        return {
            "version": 1,
            "type": "doc",
            "content": content,
        }

    @staticmethod
    def _adf_table_row(label: str, value: str) -> dict:
        """Cria uma linha de tabela ADF."""
        return {
            "type": "tableRow",
            "content": [
                {
                    "type": "tableCell",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": label, "marks": [{"type": "strong"}]},
                            ],
                        }
                    ],
                },
                {
                    "type": "tableCell",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": value}],
                        }
                    ],
                },
            ],
        }

    async def create_bug(
        self,
        summary: str,
        error_type: str,
        message: str,
        stack_trace: Optional[str],
        context: Optional[dict],
        fingerprint: str,
        source: str,
        priority: str = "High",
    ) -> Optional[str]:
        """
        Cria issue do tipo Bug no Jira.

        Returns:
            Issue key (ex: TT-150) ou None em caso de erro.
        """
        labels = ["auto-reported", "error-tracking", source]

        description = self._build_adf_description(
            error_type=error_type,
            message=message,
            stack_trace=stack_trace,
            context=context,
            fingerprint=fingerprint,
        )

        payload = {
            "fields": {
                "project": {"key": settings.JIRA_PROJECT_KEY},
                "summary": summary,
                "issuetype": {"name": "Bug"},
                "priority": {"name": priority},
                "labels": labels,
                "description": description,
            }
        }

        try:
            async with self._get_client() as client:
                response = await client.post("/issue", json=payload)
                response.raise_for_status()
                data = response.json()
                issue_key = data.get("key")
                logger.info(
                    "Jira bug criado com sucesso",
                    issue_key=issue_key,
                    summary=summary,
                )
                return issue_key
        except httpx.HTTPStatusError as e:
            logger.error(
                "Erro HTTP ao criar bug no Jira",
                status_code=e.response.status_code,
                response_body=e.response.text[:500],
                summary=summary,
            )
            return None
        except Exception as e:
            logger.error(
                "Erro inesperado ao criar bug no Jira",
                error=str(e),
                summary=summary,
            )
            return None

    async def add_comment(
        self,
        issue_key: str,
        occurrence_count: int,
    ) -> bool:
        """
        Adiciona comentario de nova ocorrencia em issue existente.

        Returns:
            True se comentario foi adicionado com sucesso.
        """
        comment_body = {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Nova ocorrencia detectada (total: {occurrence_count}). "
                            "Erro duplicado reportado automaticamente.",
                            "marks": [{"type": "em"}],
                        },
                    ],
                },
            ],
        }

        payload = {"body": comment_body}

        try:
            async with self._get_client() as client:
                response = await client.post(
                    f"/issue/{issue_key}/comment",
                    json=payload,
                )
                response.raise_for_status()
                logger.info(
                    "Comentario adicionado no Jira",
                    issue_key=issue_key,
                    occurrence_count=occurrence_count,
                )
                return True
        except Exception as e:
            logger.error(
                "Erro ao adicionar comentario no Jira",
                issue_key=issue_key,
                error=str(e),
            )
            return False

    async def search_issues(
        self,
        jql: str,
        max_results: int = 10,
    ) -> list[dict]:
        """
        Busca issues no Jira usando JQL.

        Returns:
            Lista de issues encontradas.
        """
        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ["key", "summary", "status", "labels"],
        }

        try:
            async with self._get_client() as client:
                response = await client.post("/search", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("issues", [])
        except Exception as e:
            logger.error(
                "Erro ao buscar issues no Jira",
                jql=jql,
                error=str(e),
            )
            return []


jira_service = JiraService()
