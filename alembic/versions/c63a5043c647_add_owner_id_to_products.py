"""add owner_id to products
Revision ID: c63a5043c647
Revises: 97fc188a265e
Create Date: 2026-05-19 04:11:52.119644
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c63a5043c647'
down_revision: Union[str, Sequence[str], None] = '97fc188a265e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('products', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'products', 'users', ['owner_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint(None, 'products', type_='foreignkey')
    op.drop_column('products', 'owner_id')
