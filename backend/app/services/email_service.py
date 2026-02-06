"""
Email service - sends transactional emails via Resend
"""
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails"""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None and settings.RESEND_API_KEY:
            try:
                import resend
                resend.api_key = settings.RESEND_API_KEY
                self._client = resend
            except ImportError:
                logger.warning("resend package not installed")
        return self._client

    async def send_email(self, to: str, subject: str, html: str) -> bool:
        if not self.client:
            logger.info(f"Email service not configured. Would send to {to}: {subject}")
            return True  # graceful fallback in dev

        try:
            self.client.Emails.send({
                "from": settings.EMAIL_FROM,
                "to": [to],
                "subject": subject,
                "html": html,
            })
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False

    async def send_password_reset(self, to: str, token: str) -> bool:
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1e293b;">Redefinir senha</h2>
            <p>Voce solicitou a redefinicao de sua senha no Tennis Tracking.</p>
            <p>Clique no botao abaixo para criar uma nova senha:</p>
            <a href="{reset_url}"
               style="display: inline-block; background: #3b82f6; color: white;
                      padding: 12px 24px; border-radius: 8px; text-decoration: none;
                      margin: 16px 0;">
                Redefinir Senha
            </a>
            <p style="color: #64748b; font-size: 14px;">
                Este link expira em 1 hora. Se voce nao solicitou esta redefinicao, ignore este email.
            </p>
        </div>
        """
        return await self.send_email(to, "Redefinir senha - Tennis Tracking", html)

    async def send_email_verification(self, to: str, token: str) -> bool:
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1e293b;">Verificar e-mail</h2>
            <p>Bem-vindo ao Tennis Tracking!</p>
            <p>Clique no botao abaixo para verificar seu e-mail:</p>
            <a href="{verify_url}"
               style="display: inline-block; background: #3b82f6; color: white;
                      padding: 12px 24px; border-radius: 8px; text-decoration: none;
                      margin: 16px 0;">
                Verificar E-mail
            </a>
        </div>
        """
        return await self.send_email(to, "Verificar e-mail - Tennis Tracking", html)

    async def send_organization_invite(self, to: str, org_name: str, inviter_name: str, token: str) -> bool:
        invite_url = f"{settings.FRONTEND_URL}/app/accept-invite?token={token}"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1e293b;">Convite para {org_name}</h2>
            <p>{inviter_name} convidou voce para participar de <strong>{org_name}</strong> no Tennis Tracking.</p>
            <a href="{invite_url}"
               style="display: inline-block; background: #3b82f6; color: white;
                      padding: 12px 24px; border-radius: 8px; text-decoration: none;
                      margin: 16px 0;">
                Aceitar Convite
            </a>
            <p style="color: #64748b; font-size: 14px;">
                Este convite expira em 7 dias.
            </p>
        </div>
        """
        return await self.send_email(to, f"Convite para {org_name} - Tennis Tracking", html)


email_service = EmailService()
