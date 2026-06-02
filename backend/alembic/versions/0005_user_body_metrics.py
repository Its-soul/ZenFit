"""add user body metrics

Revision ID: 0005_user_body_metrics
Revises: 0004_product_quality_schema
Create Date: 2026-06-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0005_user_body_metrics"
down_revision: Union[str, None] = "0004_product_quality_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("weight_kg", sa.Float(), nullable=True))
    op.add_column("user_profiles", sa.Column("height_cm", sa.Float(), nullable=True))
    op.add_column("user_profiles", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("biological_sex", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("user_profiles", "biological_sex")
    op.drop_column("user_profiles", "age")
    op.drop_column("user_profiles", "height_cm")
    op.drop_column("user_profiles", "weight_kg")
