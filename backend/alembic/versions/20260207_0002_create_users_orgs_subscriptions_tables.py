"""Criar tabelas users, organizations, organization_invites,
subscription_events e activity_logs.

Revision ID: 0002_create_core_tables
Revises: 0001_initial_setup
Create Date: 2026-02-07

Migra modelos MongoDB/Pydantic para SQLAlchemy ORM com PostgreSQL.
Usa JSONB para campos semi-estruturados (subscription, members, details).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision: str = "0002_create_core_tables"
down_revision: Union[str, None] = "0001_initial_setup"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Criar tabelas core: users, organizations, organization_invites,
    subscription_events, activity_logs."""

    # Enum types
    user_role_enum = sa.Enum(
        "admin", "coach", "player", "analyst", "viewer",
        name="user_role",
    )
    organization_plan_enum = sa.Enum(
        "rally", "match_point", "grand_slam",
        name="organization_plan",
    )
    invite_status_enum = sa.Enum(
        "pending", "accepted", "expired", "cancelled",
        name="invite_status",
    )

    # Criar enums no PostgreSQL
    user_role_enum.create(op.get_bind(), checkfirst=True)
    organization_plan_enum.create(op.get_bind(), checkfirst=True)
    invite_status_enum.create(op.get_bind(), checkfirst=True)

    # --- Tabela users ---
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("role", user_role_enum, nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        # Perfil
        sa.Column("profile_image", sa.String(500), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("language", sa.String(10), server_default="pt-BR"),
        sa.Column("preferences", JSONB, nullable=True),
        # Subscription (JSONB)
        sa.Column("subscription", JSONB, nullable=True),
        # Organization
        sa.Column("organization_id", UUID(as_uuid=True), nullable=True),
        sa.Column("organization_role", sa.String(50), nullable=True),
        # Email verification
        sa.Column("email_verified", sa.Boolean, server_default=sa.text("false")),
        sa.Column("email_verification_token", sa.String(500), nullable=True),
        # Password reset
        sa.Column("password_reset_token", sa.String(500), nullable=True),
        sa.Column("password_reset_expires", sa.DateTime(timezone=True), nullable=True),
        # Tokens
        sa.Column("refresh_token", sa.Text, nullable=True),
        # Auth
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Indices users
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email_active", "users", ["email", "is_active"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_organization_id", "users", ["organization_id"])

    # --- Tabela organizations ---
    op.create_table(
        "organizations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("owner_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "plan",
            organization_plan_enum,
            nullable=False,
            server_default="grand_slam",
        ),
        sa.Column("max_members", sa.Integer, server_default="10"),
        sa.Column("members", JSONB, nullable=True),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Indices organizations
    op.create_index("ix_organizations_slug", "organizations", ["slug"])
    op.create_index("ix_organizations_owner_id", "organizations", ["owner_id"])
    op.create_index("ix_organizations_name", "organizations", ["name"])

    # --- Tabela organization_invites ---
    op.create_table(
        "organization_invites",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("token", sa.String(500), unique=True, nullable=False),
        sa.Column("invited_by", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            invite_status_enum,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Indices organization_invites
    op.create_index(
        "ix_org_invites_organization_id",
        "organization_invites",
        ["organization_id"],
    )
    op.create_index("ix_org_invites_email", "organization_invites", ["email"])
    op.create_index("ix_org_invites_token", "organization_invites", ["token"])
    op.create_index(
        "ix_org_invites_org_status",
        "organization_invites",
        ["organization_id", "status"],
    )
    op.create_index(
        "ix_org_invites_email_status",
        "organization_invites",
        ["email", "status"],
    )

    # --- Tabela subscription_events ---
    op.create_table(
        "subscription_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("stripe_event_id", sa.String(255), unique=True, nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("data", JSONB, nullable=True),
        sa.Column("processed", sa.Boolean, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Indices subscription_events
    op.create_index(
        "ix_sub_events_user_id",
        "subscription_events",
        ["user_id"],
    )
    op.create_index(
        "ix_sub_events_stripe_event_id",
        "subscription_events",
        ["stripe_event_id"],
    )
    op.create_index(
        "ix_sub_events_event_type",
        "subscription_events",
        ["event_type"],
    )
    op.create_index(
        "ix_sub_events_user_type",
        "subscription_events",
        ["user_id", "event_type"],
    )
    op.create_index(
        "ix_sub_events_processed",
        "subscription_events",
        ["processed"],
    )

    # --- Tabela activity_logs ---
    op.create_table(
        "activity_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("details", JSONB, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Indices activity_logs
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"])
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"])
    op.create_index("ix_activity_logs_resource", "activity_logs", ["resource", "resource_id"])
    op.create_index(
        "ix_activity_logs_user_action",
        "activity_logs",
        ["user_id", "action"],
    )
    op.create_index(
        "ix_activity_logs_created_at",
        "activity_logs",
        ["created_at"],
    )


def downgrade() -> None:
    """Remover tabelas e enums na ordem inversa."""
    op.drop_table("activity_logs")
    op.drop_table("subscription_events")
    op.drop_table("organization_invites")
    op.drop_table("organizations")
    op.drop_table("users")

    # Remover enum types
    sa.Enum(name="invite_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="organization_plan").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
