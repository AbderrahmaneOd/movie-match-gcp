"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(128), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("poster_path", sa.String(500), nullable=True),
        sa.Column("release_date", sa.String(50), nullable=True),
        sa.Column("vote_average", sa.Float(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "session_id", "movie_id", name="uq_favorites_session_movie"
        ),
    )
    op.create_index("ix_favorites_session_id", "favorites", ["session_id"])



def downgrade() -> None:
    op.drop_index("ix_favorites_session_id", table_name="favorites")
    op.drop_table("favorites")