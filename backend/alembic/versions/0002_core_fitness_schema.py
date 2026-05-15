"""core fitness schema

Revision ID: 0002_core_fitness_schema
Revises: 0001_initial_auth_schema
Create Date: 2026-05-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_core_fitness_schema"
down_revision: Union[str, None] = "0001_initial_auth_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workout_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="scheduled"),
        sa.Column("planned_intensity", sa.String(length=30), nullable=False, server_default="moderate"),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="45"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_workout_sessions_user_date", "workout_sessions", ["user_id", "scheduled_date"])

    op.create_table(
        "meals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("meal_type", sa.String(length=40), nullable=False, server_default="meal"),
        sa.Column("calories", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("protein_g", sa.Float(), nullable=False, server_default="0"),
        sa.Column("carbs_g", sa.Float(), nullable=False, server_default="0"),
        sa.Column("fat_g", sa.Float(), nullable=False, server_default="0"),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_meals_user_logged_at", "meals", ["user_id", "logged_at"])

    op.create_table(
        "sleep_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sleep_date", sa.Date(), nullable=False),
        sa.Column("duration_hours", sa.Float(), nullable=False),
        sa.Column("quality_score", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_sleep_logs_user_date", "sleep_logs", ["user_id", "sleep_date"], unique=True)

    op.create_table(
        "recovery_checkins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("checkin_date", sa.Date(), nullable=False),
        sa.Column("fatigue_score", sa.Integer(), nullable=False),
        sa.Column("soreness_score", sa.Integer(), nullable=False),
        sa.Column("stress_score", sa.Integer(), nullable=False),
        sa.Column("readiness_score", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_recovery_checkins_user_date", "recovery_checkins", ["user_id", "checkin_date"], unique=True)

    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="normal"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("source_event_type", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_recommendations_user_status", "recommendations", ["user_id", "status"])

    op.create_table(
        "domain_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_domain_events_user_created", "domain_events", ["user_id", "created_at"])
    op.create_index("ix_domain_events_processed", "domain_events", ["processed"])


def downgrade() -> None:
    op.drop_index("ix_domain_events_processed", table_name="domain_events")
    op.drop_index("ix_domain_events_user_created", table_name="domain_events")
    op.drop_table("domain_events")
    op.drop_index("ix_recommendations_user_status", table_name="recommendations")
    op.drop_table("recommendations")
    op.drop_index("ix_recovery_checkins_user_date", table_name="recovery_checkins")
    op.drop_table("recovery_checkins")
    op.drop_index("ix_sleep_logs_user_date", table_name="sleep_logs")
    op.drop_table("sleep_logs")
    op.drop_index("ix_meals_user_logged_at", table_name="meals")
    op.drop_table("meals")
    op.drop_index("ix_workout_sessions_user_date", table_name="workout_sessions")
    op.drop_table("workout_sessions")

