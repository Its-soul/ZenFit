from app.ai.agents.base_agent import AgentInput, AgentOutput, BaseAgent


class RecoveryAgent(BaseAgent):
    name = "recovery_agent"

    def run(self, agent_input: AgentInput) -> AgentOutput:
        dashboard = agent_input.context.get("dashboard", {})
        readiness = dashboard.get("readiness_score")
        latest_sleep = dashboard.get("latest_sleep")

        if readiness is None:
            readiness = 70
        if latest_sleep and latest_sleep.get("duration_hours", 8) < 6:
            readiness = min(readiness, 50)

        if readiness < 55:
            message = "Recovery risk is elevated. Training should be reduced or shifted."
        else:
            message = "Recovery supports a normal training adjustment."

        return AgentOutput(message=message, recommendations=[{"readiness_score": readiness}], confidence=0.8)

