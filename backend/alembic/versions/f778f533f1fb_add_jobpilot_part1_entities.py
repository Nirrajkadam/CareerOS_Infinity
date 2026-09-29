"""add_jobpilot_part1_entities

Revision ID: f778f533f1fb
Revises: 
Create Date: 2026-08-13 10:01:05.247724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = 'f778f533f1fb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    # Create foundational users table first
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False, server_default='MEMBER'),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # This baseline must create resumes before the Part 1 ALTER statements.
    op.create_table('resumes',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_url', sa.String(512), nullable=False),
        sa.Column('raw_text', sa.String(), nullable=False),
        sa.Column('resume_json', postgresql.JSONB(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(1536), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Uuid(), sa.ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    for column in ('id', 'user_id', 'parent_id'):
        op.create_index(f'ix_resumes_{column}', 'resumes', [column])

    op.create_table('job_postings',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('company', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('source', sa.String(length=100), nullable=False),
    sa.Column('source_url', sa.String(length=512), nullable=True),
    sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_postings_id'), 'job_postings', ['id'], unique=False)
    op.create_table('career_goals',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('target_roles', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('target_salary', sa.String(length=100), nullable=True),
    sa.Column('target_locations', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('preferred_companies', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('preferred_industries', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('work_mode', sa.String(length=50), nullable=False),
    sa.Column('career_level', sa.String(length=50), nullable=False),
    sa.Column('application_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_goals_id'), 'career_goals', ['id'], unique=False)
    op.create_index(op.f('ix_career_goals_user_id'), 'career_goals', ['user_id'], unique=True)
    op.create_table('evidence_registry',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('type', sa.String(length=100), nullable=False),
    sa.Column('source_url', sa.String(length=512), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evidence_registry_id'), 'evidence_registry', ['id'], unique=False)
    op.create_index(op.f('ix_evidence_registry_user_id'), 'evidence_registry', ['user_id'], unique=False)
    op.create_table('master_profiles',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('personal_info', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_master_profiles_id'), 'master_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_master_profiles_user_id'), 'master_profiles', ['user_id'], unique=True)
    op.create_table('user_skills',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('normalized_name', sa.String(length=100), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('proficiency', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('first_verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_skills_id'), 'user_skills', ['id'], unique=False)
    op.create_index(op.f('ix_user_skills_user_id'), 'user_skills', ['user_id'], unique=False)
    op.create_table('certifications',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('profile_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('issuing_organization', sa.String(length=255), nullable=False),
    sa.Column('issue_date', sa.String(length=50), nullable=True),
    sa.Column('expiration_date', sa.String(length=50), nullable=True),
    sa.Column('credential_id', sa.String(length=255), nullable=True),
    sa.Column('credential_url', sa.String(length=512), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['master_profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_certifications_id'), 'certifications', ['id'], unique=False)
    op.create_index(op.f('ix_certifications_profile_id'), 'certifications', ['profile_id'], unique=False)
    op.create_index(op.f('ix_certifications_user_id'), 'certifications', ['user_id'], unique=False)
    op.create_table('educations',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('profile_id', sa.Uuid(), nullable=False),
    sa.Column('school', sa.String(length=255), nullable=False),
    sa.Column('degree', sa.String(length=255), nullable=False),
    sa.Column('field_of_study', sa.String(length=255), nullable=False),
    sa.Column('start_date', sa.String(length=50), nullable=True),
    sa.Column('end_date', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['master_profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_educations_id'), 'educations', ['id'], unique=False)
    op.create_index(op.f('ix_educations_profile_id'), 'educations', ['profile_id'], unique=False)
    op.create_index(op.f('ix_educations_user_id'), 'educations', ['user_id'], unique=False)
    op.create_table('experiences',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('profile_id', sa.Uuid(), nullable=False),
    sa.Column('company', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=255), nullable=False),
    sa.Column('start_date', sa.String(length=50), nullable=True),
    sa.Column('end_date', sa.String(length=50), nullable=True),
    sa.Column('description', sa.String(length=2000), nullable=True),
    sa.Column('achievements', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['master_profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiences_id'), 'experiences', ['id'], unique=False)
    op.create_index(op.f('ix_experiences_profile_id'), 'experiences', ['profile_id'], unique=False)
    op.create_index(op.f('ix_experiences_user_id'), 'experiences', ['user_id'], unique=False)
    op.create_table('projects',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('profile_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=2000), nullable=True),
    sa.Column('url', sa.String(length=512), nullable=True),
    sa.Column('technologies', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['master_profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_profile_id'), 'projects', ['profile_id'], unique=False)
    op.create_index(op.f('ix_projects_user_id'), 'projects', ['user_id'], unique=False)
    op.add_column('resumes', sa.Column('is_master', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('resumes', sa.Column('resume_type', sa.String(length=100), nullable=False, server_default=sa.text("'TAILORED'")))
    op.add_column('resumes', sa.Column('lifecycle_status', sa.String(length=50), nullable=False, server_default=sa.text("'ACTIVE'")))
    op.add_column('resumes', sa.Column('checksum', sa.String(length=64), nullable=True))
    op.add_column('resumes', sa.Column('validation_status', sa.String(length=50), nullable=True))
    op.add_column('resumes', sa.Column('target_job_id', sa.Uuid(), nullable=True))
    op.add_column('resumes', sa.Column('target_company', sa.String(length=255), nullable=True))
    op.add_column('resumes', sa.Column('target_role', sa.String(length=255), nullable=True))
    op.add_column('resumes', sa.Column('ats_score_before', sa.Float(), nullable=True))
    op.add_column('resumes', sa.Column('ats_score_after', sa.Float(), nullable=True))
    op.add_column('resumes', sa.Column('matched_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('resumes', sa.Column('missing_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('resumes', sa.Column('changed_sections', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('resumes', sa.Column('truth_guard_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('resumes', sa.Column('evaluation_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('resumes', sa.Column('approval_status', sa.String(length=50), nullable=True))
    op.create_foreign_key('fk_resumes_target_job', 'resumes', 'job_postings', ['target_job_id'], ['id'], ondelete='SET NULL')
    
    # Enforce one active master resume per user at DB level
    op.create_index(
        'idx_resumes_one_active_master',
        'resumes',
        ['user_id'],
        unique=True,
        postgresql_where=sa.text("is_master = true AND lifecycle_status = 'ACTIVE'")
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_resumes_one_active_master', table_name='resumes')
    op.drop_constraint('fk_resumes_target_job', 'resumes', type_='foreignkey')
    op.drop_column('resumes', 'approval_status')
    op.drop_column('resumes', 'evaluation_metadata')
    op.drop_column('resumes', 'truth_guard_result')
    op.drop_column('resumes', 'changed_sections')
    op.drop_column('resumes', 'missing_skills')
    op.drop_column('resumes', 'matched_skills')
    op.drop_column('resumes', 'ats_score_after')
    op.drop_column('resumes', 'ats_score_before')
    op.drop_column('resumes', 'target_role')
    op.drop_column('resumes', 'target_company')
    op.drop_column('resumes', 'target_job_id')
    op.drop_column('resumes', 'validation_status')
    op.drop_column('resumes', 'checksum')
    op.drop_column('resumes', 'lifecycle_status')
    op.drop_column('resumes', 'resume_type')
    op.drop_column('resumes', 'is_master')
    op.drop_index(op.f('ix_projects_user_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_profile_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_experiences_user_id'), table_name='experiences')
    op.drop_index(op.f('ix_experiences_profile_id'), table_name='experiences')
    op.drop_index(op.f('ix_experiences_id'), table_name='experiences')
    op.drop_table('experiences')
    op.drop_index(op.f('ix_educations_user_id'), table_name='educations')
    op.drop_index(op.f('ix_educations_profile_id'), table_name='educations')
    op.drop_index(op.f('ix_educations_id'), table_name='educations')
    op.drop_table('educations')
    op.drop_index(op.f('ix_certifications_user_id'), table_name='certifications')
    op.drop_index(op.f('ix_certifications_profile_id'), table_name='certifications')
    op.drop_index(op.f('ix_certifications_id'), table_name='certifications')
    op.drop_table('certifications')
    op.drop_index(op.f('ix_user_skills_user_id'), table_name='user_skills')
    op.drop_index(op.f('ix_user_skills_id'), table_name='user_skills')
    op.drop_table('user_skills')
    op.drop_index(op.f('ix_master_profiles_user_id'), table_name='master_profiles')
    op.drop_index(op.f('ix_master_profiles_id'), table_name='master_profiles')
    op.drop_table('master_profiles')
    op.drop_index(op.f('ix_evidence_registry_user_id'), table_name='evidence_registry')
    op.drop_index(op.f('ix_evidence_registry_id'), table_name='evidence_registry')
    op.drop_table('evidence_registry')
    op.drop_index(op.f('ix_career_goals_user_id'), table_name='career_goals')
    op.drop_index(op.f('ix_career_goals_id'), table_name='career_goals')
    op.drop_table('career_goals')
    op.drop_index(op.f('ix_job_postings_id'), table_name='job_postings')
    op.drop_table('job_postings')
    op.drop_table('resumes')
    op.drop_table('users')
    # ### end Alembic commands ###
