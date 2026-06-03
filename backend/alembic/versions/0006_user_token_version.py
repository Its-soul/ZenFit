"""add user token version and role

Revision ID: 0006_user_token_version
Revises: 0005_user_body_metrics
Create Date: 2026-06-03
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0006_user_token_version"
down_revision: Union[str, None] = "0005_user_body_metrics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=40), nullable=False, server_default="user"))
    op.alter_column("users", "role", server_default=None)
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("users", "token_version", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "token_version")
    op.drop_column("users", "role")
