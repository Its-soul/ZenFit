"""product quality schema

Revision ID: 0004_product_quality_schema
Revises: 0003_predictive_schema
Create Date: 2026-05-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0004_product_quality_schema"
down_revision: Union[str, None] = "0003_predictive_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("meals", sa.Column("image_path", sa.String(length=500), nullable=True))
    op.add_column("meals", sa.Column("analysis_explanation", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("meals", "analysis_explanation")
    op.drop_column("meals", "image_path")
