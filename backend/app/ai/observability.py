import time
import uuid
from contextlib import contextmanager

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime

from sqlalchemy.orm import Mapped, Session, mapped_column

from app.db.base_class import Base


class AIAuditLog(Base):
    __tablename__ = "ai_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    operation: Mapped[str] = mapped_column(String(120), nullable=False)
    agent_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    prompt_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    retrieved_memory_ids: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    tool_calls: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    scores: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AILogger:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        operation: str,
        user_id=None,
        agent_name: str | None = None,
        prompt_name: str | None = None,
        input_summary: str | None = None,
        output_summary: str | None = None,
        retrieved_memory_ids: list | None = None,
        tool_calls: list | None = None,
        scores: dict | None = None,
        latency_ms: int = 0,
    ) -> AIAuditLog:
        entry = AIAuditLog(
            operation=operation,
            user_id=user_id,
            agent_name=agent_name,
            prompt_name=prompt_name,
            input_summary=input_summary,
            output_summary=output_summary,
            retrieved_memory_ids=retrieved_memory_ids or [],
            tool_calls=tool_calls or [],
            scores=scores or {},
            latency_ms=latency_ms,
        )
        self.db.add(entry)
        self.db.flush()
        return entry


@contextmanager
def observe_ai_operation(db: Session, **metadata):
    started_at = time.perf_counter()
    result = {"output_summary": None, "scores": {}, "retrieved_memory_ids": [], "tool_calls": []}
    try:
        yield result
    finally:
        latency_ms = round((time.perf_counter() - started_at) * 1000)
        AILogger(db).log(
            latency_ms=latency_ms,
            output_summary=result.get("output_summary"),
            scores=result.get("scores"),
            retrieved_memory_ids=result.get("retrieved_memory_ids"),
            tool_calls=result.get("tool_calls"),
            **metadata,
        )
