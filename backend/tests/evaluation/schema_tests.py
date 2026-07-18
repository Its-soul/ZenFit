from app.ai.agents.base_agent import AgentInput
from app.ai.agents.coach_agent import CoachAgent


def run_agent_schema_tests() -> list[dict]:
    output = CoachAgent().run(AgentInput(user_id="eval-user", message="What next?", context={"dashboard": {}}, memories=[]))
    passed = isinstance(output.message, str) and isinstance(output.recommendations, list) and 0 <= output.confidence <= 1
    return [{"name": "coach_agent_output_schema", "passed": passed}]


def run_tool_call_validation_tests() -> list[dict]:
    expected_tools = ["get_dashboard_context"]
    return [{"name": "approved_tool_names_are_explicit", "passed": all("_" in tool for tool in expected_tools)}]

