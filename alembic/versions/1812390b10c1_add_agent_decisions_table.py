"""add_agent_decisions_table
Revision ID: 1812390b10c1
Revises: f3277cefc74e
Create Date: 2026-06-05 03:02:05.085535
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '1812390b10c1'
down_revision: Union[str, Sequence[str], None] = 'f3277cefc74e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'agent_decisions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('ip', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('action_method', sa.String(), nullable=True),
        sa.Column('action_path', sa.String(), nullable=True),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('decision', sa.String(), nullable=False),
        sa.Column('razones', sa.Text(), nullable=True),
        sa.Column('adaptive_flags', sa.Text(), nullable=True),
        sa.Column('recon_correlated', sa.Boolean(), default=False),
        sa.Column('history_len', sa.Integer(), nullable=True),
        sa.Column('long_history_len', sa.Integer(), nullable=True),
    )
    op.create_index('ix_agent_decisions_user_id', 'agent_decisions', ['user_id'])
    op.create_index('ix_agent_decisions_decision', 'agent_decisions', ['decision'])
    op.create_index('ix_agent_decisions_timestamp', 'agent_decisions', ['timestamp'])

def downgrade() -> None:
    op.drop_index('ix_agent_decisions_timestamp', 'agent_decisions')
    op.drop_index('ix_agent_decisions_decision', 'agent_decisions')
    op.drop_index('ix_agent_decisions_user_id', 'agent_decisions')
    op.drop_table('agent_decisions')
