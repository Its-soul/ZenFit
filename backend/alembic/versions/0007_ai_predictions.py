"""add ai prediction audit table

Revision ID: 0007_ai_predictions
Revises: 0006_user_token_version
"""
from typing import Sequence,Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op
revision="0007_ai_predictions";down_revision="0006_user_token_version";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("ai_predictions",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("user_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("prediction_type",sa.String(40),nullable=False),sa.Column("entity_id",postgresql.UUID(as_uuid=True),nullable=True),sa.Column("model_name",sa.String(120),nullable=False),sa.Column("model_version",sa.String(80),nullable=False),sa.Column("prediction_value",sa.Float(),nullable=False),sa.Column("risk_level",sa.String(30),nullable=True),sa.Column("feature_snapshot",postgresql.JSONB(),nullable=False,server_default=sa.text("'{}'::jsonb")),sa.Column("shadow_mode",sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column("outcome",sa.String(30),nullable=True),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.Column("outcome_recorded_at",sa.DateTime(timezone=True),nullable=True))
    for name,cols in (("ix_ai_predictions_user_id",["user_id"]),("ix_ai_predictions_prediction_type",["prediction_type"]),("ix_ai_predictions_entity_id",["entity_id"]),("ix_ai_predictions_created_at",["created_at"])):op.create_index(name,"ai_predictions",cols)
def downgrade():op.drop_table("ai_predictions")
