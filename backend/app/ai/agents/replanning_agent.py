from datetime import date, timedelta

from app.ai.agents.base_agent import AgentInput, AgentOutput, BaseAgent


class ReplanningAgent(BaseAgent):
    name = "replanning_agent"

    def run(self, agent_input: AgentInput) -> AgentOutput:
        dashboard = agent_input.context.get("dashboard", {})
        readiness = dashboard.get("readiness_score") or 70
        missed_workout = dashboard.get("today_workout", {})

        if readiness < 55:
            title = "Recovery Rebuild Session"
            duration = 30
            intensity = "low"
            explanation = "Readiness is low, so the missed session is converted into a shorter recovery-biased session."
        else:
            title = missed_workout.get("title", "Rescheduled Workout")
            duration = max(int(missed_workout.get("duration_minutes", 45)) - 10, 30)
            intensity = "moderate"
            explanation = "The missed session is shifted forward with slightly reduced duration to protect consistency."

        scheduled_date = (date.today() + timedelta(days=1)).isoformat()
        return AgentOutput(
            message=explanation,
            recommendations=[
                {
                    "title": title,
                    "scheduled_date": scheduled_date,
                    "duration_minutes": duration,
                    "planned_intensity": intensity,
                    "notes": explanation,
                }
            ],
            memory_to_write=f"Plan replanned after missed workout: {explanation}",
            confidence=0.78,
        )

