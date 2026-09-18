"""Initial database schema

Revision ID: 0001
Revises:
Create Date: 2026-07-09 12:00:00.000000

Creates all tables:
  - admins
  - users
  - subscriptions
  - notices
  - bookmarks
  - notification_history
  - system_logs
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── admins ────────────────────────────────────────────────────────────────
    op.create_table(
        'admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_superadmin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_admins_id'), 'admins', ['id'], unique=False)
    op.create_index(op.f('ix_admins_email'), 'admins', ['email'], unique=True)

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('telegram_notifications', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('telegram_chat_id', sa.String(length=64), nullable=True),
        sa.Column('reset_token', sa.String(length=255), nullable=True),
        sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # ── subscriptions ─────────────────────────────────────────────────────────
    category_enum = sa.Enum(
        'NEET', 'JEE', 'CUET', 'GATE', 'CAT', 'UPSC', 'SSC', 'BANKING', 'SCHOLARSHIPS', 'GENERAL',
        name='categoryenum',
    )
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', category_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'category', name='uq_user_category'),
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)

    # ── notices ───────────────────────────────────────────────────────────────
    op.create_table(
        'notices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('source', sa.String(length=64), nullable=False, server_default='NTA'),
        sa.Column('category', sa.String(length=64), nullable=False, server_default='GENERAL'),
        sa.Column('raw_content', sa.Text(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('ai_explanation', sa.Text(), nullable=True),
        sa.Column('ai_important_dates', sa.Text(), nullable=True),
        sa.Column('ai_action_required', sa.Text(), nullable=True),
        sa.Column('ai_eligibility', sa.Text(), nullable=True),
        sa.Column('ai_deadline', sa.String(length=256), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('is_processed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_notified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('scraped_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_hash', name='uq_notice_content_hash'),
    )
    op.create_index(op.f('ix_notices_id'), 'notices', ['id'], unique=False)
    op.create_index(op.f('ix_notices_category'), 'notices', ['category'], unique=False)
    op.create_index(op.f('ix_notices_content_hash'), 'notices', ['content_hash'], unique=True)
    op.create_index(op.f('ix_notices_scraped_at'), 'notices', ['scraped_at'], unique=False)

    # ── bookmarks ─────────────────────────────────────────────────────────────
    op.create_table(
        'bookmarks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notice_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['notice_id'], ['notices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'notice_id', name='uq_user_notice_bookmark'),
    )
    op.create_index(op.f('ix_bookmarks_id'), 'bookmarks', ['id'], unique=False)
    op.create_index(op.f('ix_bookmarks_user_id'), 'bookmarks', ['user_id'], unique=False)
    op.create_index(op.f('ix_bookmarks_notice_id'), 'bookmarks', ['notice_id'], unique=False)

    # ── notification_history ──────────────────────────────────────────────────
    channel_enum = sa.Enum('telegram', 'email', 'push', name='notificationchannel')
    status_enum = sa.Enum('sent', 'failed', 'pending', name='notificationstatus')
    op.create_table(
        'notification_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notice_id', sa.Integer(), nullable=False),
        sa.Column('channel', channel_enum, nullable=False),
        sa.Column('status', status_enum, nullable=False, server_default='pending'),
        sa.Column('error_message', sa.String(length=512), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['notice_id'], ['notices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notification_history_id'), 'notification_history', ['id'], unique=False)
    op.create_index(op.f('ix_notification_history_user_id'), 'notification_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_notification_history_sent_at'), 'notification_history', ['sent_at'], unique=False)

    # ── system_logs ───────────────────────────────────────────────────────────
    loglevel_enum = sa.Enum('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', name='loglevel')
    op.create_table(
        'system_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('level', loglevel_enum, nullable=False),
        sa.Column('module', sa.String(length=128), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('extra', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_system_logs_id'), 'system_logs', ['id'], unique=False)
    op.create_index(op.f('ix_system_logs_level'), 'system_logs', ['level'], unique=False)
    op.create_index(op.f('ix_system_logs_module'), 'system_logs', ['module'], unique=False)
    op.create_index(op.f('ix_system_logs_created_at'), 'system_logs', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table('system_logs')
    op.drop_table('notification_history')
    op.drop_table('bookmarks')
    op.drop_table('notices')
    op.drop_table('subscriptions')
    op.drop_table('users')
    op.drop_table('admins')

    # Drop custom enum types
    sa.Enum(name='loglevel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='notificationstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='notificationchannel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='categoryenum').drop(op.get_bind(), checkfirst=True)
