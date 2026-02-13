"""initial schema — 全テーブルの初期作成

Revision ID: 001
Revises: None
Create Date: 2026-02-13

既存の手動マイグレーション (migration_add_mode.py, migration_add_beginner_fields.py)
を統合した初期スキーマ。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- projects ---
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('mode', sa.Enum('BEGINNER', 'EXPERT', name='projectmode'), nullable=False, server_default='EXPERT'),
        sa.Column('country', sa.String(50)),
        sa.Column('currency', sa.String(10)),
        sa.Column('industry', sa.String(100)),
        sa.Column('company_count', sa.Integer()),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_projects_id', 'projects', ['id'])

    # --- config_items ---
    op.create_table(
        'config_items',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('priority', sa.String(10)),
        sa.Column('inputs', sa.JSON()),
        sa.Column('depends_on', sa.JSON()),
        sa.Column('produces', sa.JSON()),
        sa.Column('notes', sa.JSON()),
        sa.Column('beginner_mode', sa.Boolean(), server_default='true'),
        sa.Column('beginner_title', sa.String(255)),
        sa.Column('beginner_description', sa.Text()),
        sa.Column('beginner_why', sa.Text()),
    )

    # --- answers ---
    op.create_table(
        'answers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('config_item_id', sa.String(50), sa.ForeignKey('config_items.id'), nullable=False),
        sa.Column('input_name', sa.String(100), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_answers_id', 'answers', ['id'])

    # --- decisions ---
    op.create_table(
        'decisions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('config_item_id', sa.String(50), sa.ForeignKey('config_items.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('rationale', sa.Text()),
        sa.Column('impact', sa.Text()),
        sa.Column('status', sa.String(50), server_default='DECIDED'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_decisions_id', 'decisions', ['id'])

    # --- backlog_items ---
    op.create_table(
        'backlog_items',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('config_item_id', sa.String(50), sa.ForeignKey('config_items.id'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'BLOCKED', 'READY', 'DONE', name='backlogstatus'), server_default='PENDING'),
        sa.Column('answered', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_backlog_items_id', 'backlog_items', ['id'])

    # --- artifacts ---
    op.create_table(
        'artifacts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('artifact_type', sa.Enum('DECISION_LOG', 'CONFIG_WORKBOOK', 'TEST_VIEW', 'MIGRATION_VIEW', name='artifacttype'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tbd_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_artifacts_id', 'artifacts', ['id'])


def downgrade() -> None:
    op.drop_table('artifacts')
    op.drop_table('backlog_items')
    op.drop_table('decisions')
    op.drop_table('answers')
    op.drop_table('config_items')
    op.drop_table('projects')

    # ENUM型を削除
    op.execute("DROP TYPE IF EXISTS projectmode")
    op.execute("DROP TYPE IF EXISTS backlogstatus")
    op.execute("DROP TYPE IF EXISTS artifacttype")
