"""add_tournaments

Revision ID: 20260207_0007
Revises: 20260207_0006
Create Date: 2026-02-07 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0007_add_tournaments'
down_revision = '0006_add_rankings'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar enums
    op.execute("CREATE TYPE tournament_status AS ENUM ('draft', 'open', 'closed', 'in_progress', 'completed', 'cancelled')")
    op.execute("CREATE TYPE tournament_type AS ENUM ('singles', 'doubles', 'mixed', 'team')")
    op.execute("CREATE TYPE registration_status AS ENUM ('pending', 'confirmed', 'cancelled', 'waitlist')")
    op.execute("CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'refunded', 'failed')")

    # Tabela tournaments
    op.create_table(
        'tournaments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sport', sa.String(length=50), nullable=False),
        sa.Column('tournament_type', postgresql.ENUM('singles', 'doubles', 'mixed', 'team', name='tournament_type', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'open', 'closed', 'in_progress', 'completed', 'cancelled', name='tournament_status', create_type=False), nullable=False),
        sa.Column('organizer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('venue_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('venue_name', sa.String(length=200), nullable=True),
        sa.Column('venue_address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('registration_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('registration_deadline', sa.DateTime(timezone=True), nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('current_participants', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('registration_fee', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('allow_waitlist', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('require_approval', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('rules', sa.Text(), nullable=True),
        sa.Column('prizes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('contact_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('additional_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('banner_image', sa.String(length=500), nullable=True),
        sa.Column('logo_image', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organizer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tournaments_status', 'tournaments', ['status'])
    op.create_index('ix_tournaments_sport', 'tournaments', ['sport'])
    op.create_index('ix_tournaments_organizer_id', 'tournaments', ['organizer_id'])
    op.create_index('ix_tournaments_organization_id', 'tournaments', ['organization_id'])
    op.create_index('ix_tournaments_start_date', 'tournaments', ['start_date'])
    op.create_index('ix_tournaments_state', 'tournaments', ['state'])
    op.create_index('ix_tournaments_city', 'tournaments', ['city'])

    # Tabela tournament_categories
    op.create_table(
        'tournament_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('min_age', sa.Integer(), nullable=True),
        sa.Column('max_age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('skill_level', sa.String(length=50), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('current_participants', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('registration_fee', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tournament_categories_tournament_id', 'tournament_categories', ['tournament_id'])
    op.create_index('ix_tournament_categories_gender', 'tournament_categories', ['gender'])
    op.create_index('ix_tournament_categories_skill_level', 'tournament_categories', ['skill_level'])

    # Tabela tournament_registrations
    op.create_table(
        'tournament_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('player_name', sa.String(length=200), nullable=False),
        sa.Column('player_email', sa.String(length=255), nullable=False),
        sa.Column('player_phone', sa.String(length=20), nullable=True),
        sa.Column('player_document', sa.String(length=50), nullable=True),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('partner_name', sa.String(length=200), nullable=True),
        sa.Column('team_name', sa.String(length=200), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'confirmed', 'cancelled', 'waitlist', name='registration_status', create_type=False), nullable=False),
        sa.Column('payment_status', postgresql.ENUM('pending', 'paid', 'refunded', 'failed', name='payment_status', create_type=False), nullable=False),
        sa.Column('amount_paid', sa.Float(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_id', sa.String(length=200), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('emergency_contact', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('medical_info', sa.Text(), nullable=True),
        sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['tournament_categories.id'], ),
        sa.ForeignKeyConstraint(['player_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['partner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tournament_registrations_tournament_id', 'tournament_registrations', ['tournament_id'])
    op.create_index('ix_tournament_registrations_category_id', 'tournament_registrations', ['category_id'])
    op.create_index('ix_tournament_registrations_player_id', 'tournament_registrations', ['player_id'])
    op.create_index('ix_tournament_registrations_status', 'tournament_registrations', ['status'])
    op.create_index('ix_tournament_registrations_payment_status', 'tournament_registrations', ['payment_status'])


def downgrade() -> None:
    # Dropar tabelas
    op.drop_index('ix_tournament_registrations_payment_status', table_name='tournament_registrations')
    op.drop_index('ix_tournament_registrations_status', table_name='tournament_registrations')
    op.drop_index('ix_tournament_registrations_player_id', table_name='tournament_registrations')
    op.drop_index('ix_tournament_registrations_category_id', table_name='tournament_registrations')
    op.drop_index('ix_tournament_registrations_tournament_id', table_name='tournament_registrations')
    op.drop_table('tournament_registrations')

    op.drop_index('ix_tournament_categories_skill_level', table_name='tournament_categories')
    op.drop_index('ix_tournament_categories_gender', table_name='tournament_categories')
    op.drop_index('ix_tournament_categories_tournament_id', table_name='tournament_categories')
    op.drop_table('tournament_categories')

    op.drop_index('ix_tournaments_city', table_name='tournaments')
    op.drop_index('ix_tournaments_state', table_name='tournaments')
    op.drop_index('ix_tournaments_start_date', table_name='tournaments')
    op.drop_index('ix_tournaments_organization_id', table_name='tournaments')
    op.drop_index('ix_tournaments_organizer_id', table_name='tournaments')
    op.drop_index('ix_tournaments_sport', table_name='tournaments')
    op.drop_index('ix_tournaments_status', table_name='tournaments')
    op.drop_table('tournaments')

    # Dropar enums
    op.execute("DROP TYPE IF EXISTS payment_status")
    op.execute("DROP TYPE IF EXISTS registration_status")
    op.execute("DROP TYPE IF EXISTS tournament_type")
    op.execute("DROP TYPE IF EXISTS tournament_status")
