from app.ai.evaluation.hallucination_tests import run_hallucination_checks
from app.ai.evaluation.prompt_tests import run_prompt_regression_tests
from app.ai.evaluation.recommendation_tests import run_recommendation_quality_tests
from app.ai.evaluation.retrieval_tests import run_retrieval_quality_tests
from app.ai.evaluation.schema_tests import run_agent_schema_tests, run_tool_call_validation_tests


def run_all_evaluations() -> dict:
    groups = {
        "prompt_regression": run_prompt_regression_tests(),
        "retrieval_quality": run_retrieval_quality_tests(),
        "recommendation_quality": run_recommendation_quality_tests(),
        "schema_validation": run_agent_schema_tests(),
        "tool_validation": run_tool_call_validation_tests(),
        "hallucination_checks": run_hallucination_checks(),
    }
    total = sum(len(results) for results in groups.values())
    passed = sum(1 for results in groups.values() for result in results if result["passed"])
    return {"passed": passed, "total": total, "groups": groups}

