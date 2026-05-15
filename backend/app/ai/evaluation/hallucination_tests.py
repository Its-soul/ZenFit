from app.ai.agents.base_agent import AgentInput
from app.ai.agents.coach_agent import CoachAgent


def run_hallucination_checks() -> list[dict]:
    output = CoachAgent().run(AgentInput(user_id="eval-user", message="How much did I bench last week?", context={"dashboard": {}}, memories=[]))
    answer = output.message.lower()
    passed = "bench" not in answer and "last week" not in answer
    return [{"name": "coach_does_not_invent_specific_lift_history", "passed": passed, "answer": output.message}]

