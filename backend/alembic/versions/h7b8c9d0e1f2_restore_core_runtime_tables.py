"""Restore core authentication and graph tables omitted from the legacy history.

Revision ID: h7b8c9d0e1f2
Revises: g6a7b8c9d0e1
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = 'h7b8c9d0e1f2'
down_revision = 'g6a7b8c9d0e1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column('users', 'full_name', existing_type=sa.String(255), nullable=True)
    role = postgresql.ENUM('ADMIN', 'MEMBER', name='userrole')
    role.create(op.get_bind(), checkfirst=True)
    op.alter_column('users', 'role', server_default=None)
    op.alter_column('users', 'role', type_=role, postgresql_using='role::userrole')
    op.alter_column('users', 'role', server_default=sa.text("'MEMBER'::userrole"))
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table('refresh_tokens',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(512), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_refresh_tokens_id', 'refresh_tokens', ['id'])
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)

    op.create_table('audit_logs',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('details', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    for column in ('id', 'user_id', 'action'):
        op.create_index(f'ix_audit_logs_{column}', 'audit_logs', [column])

    op.create_table('graph_nodes',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('properties', postgresql.JSONB(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    for column in ('id', 'entity_type'):
        op.create_index(f'ix_graph_nodes_{column}', 'graph_nodes', [column])

    op.create_table('graph_relationships',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('source_id', sa.String(255), nullable=False),
        sa.Column('target_id', sa.String(255), nullable=False),
        sa.Column('relation_type', sa.String(100), nullable=False),
        sa.Column('properties', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    for column in ('id', 'source_id', 'target_id', 'relation_type'):
        op.create_index(f'ix_graph_relationships_{column}', 'graph_relationships', [column])


def downgrade():
    for table in ('graph_relationships', 'graph_nodes', 'audit_logs', 'refresh_tokens'):
        op.drop_table(table)
    op.drop_index('ix_users_email', table_name='users')
    op.alter_column('users', 'role', server_default=None)
    op.alter_column('users', 'role', type_=sa.String(50), postgresql_using='role::text')
    op.alter_column('users', 'role', server_default='MEMBER')
    postgresql.ENUM(name='userrole').drop(op.get_bind(), checkfirst=True)
    op.alter_column('users', 'full_name', existing_type=sa.String(255), nullable=False)
    op.drop_column('users', 'is_deleted')
