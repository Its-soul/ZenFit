"""add meal analysis corrections

Revision ID: 0008_meal_corrections
Revises: 0007_ai_predictions
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op
revision="0008_meal_corrections";down_revision="0007_ai_predictions";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("meal_analysis_corrections",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("user_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("analysis_id",postgresql.UUID(as_uuid=True),nullable=False),sa.Column("predicted_foods",postgresql.JSONB(),nullable=False,server_default=sa.text("'[]'::jsonb")),sa.Column("confirmed_foods",postgresql.JSONB(),nullable=False,server_default=sa.text("'[]'::jsonb")),sa.Column("model_versions",postgresql.JSONB(),nullable=False,server_default=sa.text("'[]'::jsonb")),sa.Column("training_consent",sa.Boolean(),nullable=False,server_default=sa.false()),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()))
    op.create_index("ix_meal_analysis_corrections_user_id","meal_analysis_corrections",["user_id"]);op.create_index("ix_meal_analysis_corrections_analysis_id","meal_analysis_corrections",["analysis_id"],unique=True)
def downgrade():op.drop_table("meal_analysis_corrections")
