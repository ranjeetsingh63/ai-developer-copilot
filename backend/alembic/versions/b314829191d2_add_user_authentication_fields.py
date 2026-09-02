"""add user authentication fields

Revision ID: b314829191d2
Revises:
Create Date: 2026-09-01

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "b314829191d2"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE users
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
        """
    )

    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.drop_index(
        "ix_users_id",
        table_name="users",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False,
    )

    op.drop_column("users", "created_at")
    op.drop_column("users", "password_hash")