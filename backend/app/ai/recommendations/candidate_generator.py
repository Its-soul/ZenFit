class RecommendationCandidateGenerator:
    def generate_for_event(self, *, event_type: str, context: dict) -> list[dict]:
        if event_type == "workout.missed":
            return [
                {
                    "title": "Protect workout consistency",
                    "body": "Do a shorter replacement session tomorrow instead of trying to cram extra volume today.",
                    "category": "workout",
                    "priority": "high",
                    "score": 0.9,
                    "reasoning_summary": "Missed workout indicates adherence friction; a smaller replacement protects continuity.",
                    "triggering_factors": ["workout.missed", "adherence_risk"],
                },
                {
                    "title": "Remove the blocker",
                    "body": "Write down why the session was missed so your coach can plan around the real constraint.",
                    "category": "adherence",
                    "priority": "normal",
                    "score": 0.7,
                    "reasoning_summary": "Capturing the miss reason improves future personalization.",
                    "triggering_factors": ["workout.missed", "missing_miss_reason"],
                },
            ]

        if event_type == "sleep.poor":
            return [
                {
                    "title": "Reduce training intensity",
                    "body": "Poor sleep detected. Keep today technical and avoid max-effort sets.",
                    "category": "recovery",
                    "priority": "high",
                    "score": 0.86,
                    "reasoning_summary": "Poor sleep increases fatigue risk; intensity should be moderated.",
                    "triggering_factors": ["sleep.poor", "recovery_risk"],
                }
            ]

        if event_type == "recovery.low":
            return [
                {
                    "title": "Use a recovery-first plan",
                    "body": "Readiness is low. Choose mobility, easy cardio, or reduced-load strength work.",
                    "category": "recovery",
                    "priority": "high",
                    "score": 0.88,
                    "reasoning_summary": "Low readiness suggests recovery stress is currently high.",
                    "triggering_factors": ["recovery.low", "readiness_low"],
                }
            ]

        if event_type == "adherence.low":
            return [
                {
                    "title": "Make the next action smaller",
                    "body": "Adherence risk increased. Choose a 20-minute minimum session or one nutrition log to rebuild momentum.",
                    "category": "adherence",
                    "priority": "high",
                    "score": 0.84,
                    "reasoning_summary": "Adherence risk responds best to smaller next actions.",
                    "triggering_factors": ["adherence.low", "missed_behavior"],
                }
            ]

        if event_type == "plan.replanned":
            return [
                {
                    "title": "Review your adjusted plan",
                    "body": "Your plan changed based on recent behavior and recovery signals. Check tomorrow's workout before training.",
                    "category": "workout",
                    "priority": "normal",
                    "score": 0.78,
                    "reasoning_summary": "Plan changes need visibility so the user knows what changed and why.",
                    "triggering_factors": ["plan.replanned"],
                }
            ]

        if event_type == "workout.rescheduled":
            return [
                {
                    "title": "Protect the new workout slot",
                    "body": "Your session moved. Keep the new slot smaller and specific so it is easier to complete.",
                    "category": "workout",
                    "priority": "normal",
                    "score": 0.74,
                    "reasoning_summary": "Rescheduling is useful when it preserves the next clear action.",
                    "triggering_factors": ["workout.rescheduled", "schedule_change"],
                }
            ]

        if event_type == "meal.logged":
            nutrition = context.get("dashboard", {}).get("nutrition", {})
            protein_target = nutrition.get("protein_target_g") or 0
            if protein_target > 0 and nutrition.get("protein_g", 0) < protein_target * 0.5:
                return [
                    {
                        "title": "Add a protein anchor",
                        "body": "Protein is behind pace today. Add a lean protein source in your next meal.",
                        "category": "nutrition",
                        "priority": "normal",
                        "score": 0.72,
                        "reasoning_summary": "Protein is behind target after meal logging.",
                        "triggering_factors": ["meal.logged", "protein_gap"],
                    }
                ]

        return [
            {
                "title": "Keep the signal strong",
                "body": "Log one more action today so the adaptive system has better context.",
                "category": "adherence",
                "priority": "normal",
                "score": 0.5,
                "reasoning_summary": "Default adherence support when the system has limited context.",
                "triggering_factors": [event_type],
            }
        ]
