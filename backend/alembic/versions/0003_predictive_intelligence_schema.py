"""predictive intelligence schema

Revision ID: 0003_predictive_schema
Revises: 0002_core_fitness_schema
Create Date: 2026-05-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_predictive_schema"
down_revision: Union[str, None] = "0002_core_fitness_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recommendations", sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.6"))
    op.add_column("recommendations", sa.Column("reasoning_summary", sa.Text(), nullable=True))
    op.add_column("recommendations", sa.Column("triggering_factors", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column("recommendations", sa.Column("related_memory_ids", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")))

    op.create_table(
        "recommendation_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feedback_type", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_recommendation_feedback_user", "recommendation_feedback", ["user_id", "created_at"])

    op.create_table(
        "ai_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("operation", sa.String(length=120), nullable=False),
        sa.Column("agent_name", sa.String(length=80), nullable=True),
        sa.Column("prompt_name", sa.String(length=120), nullable=True),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column("output_summary", sa.Text(), nullable=True),
        sa.Column("retrieved_memory_ids", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("tool_calls", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("scores", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_audit_logs_user_created", "ai_audit_logs", ["user_id", "created_at"])
    op.create_index("ix_ai_audit_logs_operation", "ai_audit_logs", ["operation"])

    op.create_table(
        "ai_weekly_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("metrics", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("predictions", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_weekly_reports_user_week", "ai_weekly_reports", ["user_id", "week_start"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_ai_weekly_reports_user_week", table_name="ai_weekly_reports")
    op.drop_table("ai_weekly_reports")
    op.drop_index("ix_ai_audit_logs_operation", table_name="ai_audit_logs")
    op.drop_index("ix_ai_audit_logs_user_created", table_name="ai_audit_logs")
    op.drop_table("ai_audit_logs")
    op.drop_index("ix_recommendation_feedback_user", table_name="recommendation_feedback")
    op.drop_table("recommendation_feedback")
    op.drop_column("recommendations", "related_memory_ids")
    op.drop_column("recommendations", "triggering_factors")
    op.drop_column("recommendations", "reasoning_summary")
    op.drop_column("recommendations", "confidence_score")
