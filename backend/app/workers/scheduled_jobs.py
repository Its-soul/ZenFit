import logging
from datetime import datetime, timezone

from app.ai.agents.memory_agent import MemoryAgent
from app.ai.memory.compression import MemoryCompressor
from app.ai.reporting import WeeklyReportService
from app.db.session import SessionLocal
from app.modules.analytics.service import AnalyticsService
from app.modules.auth.repository import UserRepository

logger = logging.getLogger(__name__)


class ScheduledAIJobs:
    def __init__(self):
        self.db = SessionLocal()
        self.memory = MemoryAgent()
        self.compressor = MemoryCompressor()

    def close(self) -> None:
        self.db.close()

    def run_nightly_behavioral_analysis(self) -> None:
        logger.info("Running nightly behavioral analysis")
        users = UserRepository(self.db).list_active()
        for user in users:
            summary = AnalyticsService(self.db).predictive_summary(user)
            self.memory.write(
                user_id=str(user.id),
                text=(
                    "Nightly behavior analysis: "
                    f"adherence risk {summary.predictions['adherence_risk']['level']}, "
                    f"fatigue escalation {summary.predictions['fatigue_escalation']['level']}, "
                    f"coaching style {summary.personalization['coaching_style']}."
                ),
                metadata={"category": "summary", "source": "nightly_behavioral_analysis", "importance": 0.78},
            )
        self.db.commit()

    def run_memory_summarization(self) -> None:
        logger.info("Running memory summarization")
        users = UserRepository(self.db).list_active()
        for user in users:
            memories = self.memory.retrieve(user_id=str(user.id), query="adherence recovery nutrition sleep workout behavior", limit=20)
            self.compressor.summarize(user_id=str(user.id), memories=memories)
        self.db.commit()

    def run_weekly_reports(self) -> None:
        logger.info("Running weekly AI reports")
        report_service = WeeklyReportService(self.db)
        for user in UserRepository(self.db).list_active():
            report_service.generate_for_user(user)
        self.db.commit()


def run_once() -> None:
    jobs = ScheduledAIJobs()
    try:
        jobs.run_nightly_behavioral_analysis()
        jobs.run_memory_summarization()
        if datetime.now(timezone.utc).weekday() == 6:
            jobs.run_weekly_reports()
    finally:
        jobs.close()

