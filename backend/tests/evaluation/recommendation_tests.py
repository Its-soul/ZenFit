import json
from pathlib import Path

from app.ai.recommendations.candidate_generator import RecommendationCandidateGenerator
from app.ai.recommendations.ranker import RecommendationRanker

DATASET = Path(__file__).parent.parent / "fixtures" / "recommendation_cases.json"


def run_recommendation_quality_tests() -> list[dict]:
    cases = json.loads(DATASET.read_text())
    generator = RecommendationCandidateGenerator()
    ranker = RecommendationRanker()
    results = []

    for case in cases:
        ranked = ranker.rank(generator.generate_for_event(event_type=case["event_type"], context=case["context"]), context=case["context"])
        top = ranked[0]
        results.append(
            {
                "name": case["name"],
                "passed": top["category"] == case["expected_category"] and top["confidence_score"] >= case["minimum_confidence"],
                "top": top,
            }
        )
    return results

