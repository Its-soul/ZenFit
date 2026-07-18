import json
from pathlib import Path

from app.ai.agents.base_agent import AgentInput
from app.ai.agents.coach_agent import CoachAgent

DATASET = Path(__file__).parent.parent / "fixtures" / "prompt_regression_cases.json"


def run_prompt_regression_tests() -> list[dict]:
    cases = json.loads(DATASET.read_text())
    results = []
    agent = CoachAgent()

    for case in cases:
        output = agent.run(
            AgentInput(
                user_id="eval-user",
                message=case["message"],
                context=case["context"],
                memories=[],
            )
        )
        answer = output.message.lower()
        passed = all(term.lower() in answer for term in case["must_include"]) and not any(
            term.lower() in answer for term in case["must_not_include"]
        )
        results.append({"name": case["name"], "passed": passed, "answer": output.message})

    return results

