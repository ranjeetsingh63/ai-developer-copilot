"""add repositories table

Revision ID: c2aa1764647b
Revises: abcd1164994a
Create Date: 2026-09-05 14:42:57.351180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2aa1764647b'
down_revision: Union[str, Sequence[str], None] = 'abcd1164994a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('repositories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('github_url', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('default_branch', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repositories_id'), 'repositories', ['id'], unique=False)
    op.create_index(op.f('ix_repositories_project_id'), 'repositories', ['project_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_repositories_project_id'), table_name='repositories')
    op.drop_index(op.f('ix_repositories_id'), table_name='repositories')
    op.drop_table('repositories')