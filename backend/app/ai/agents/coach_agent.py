from app.ai.agents.base_agent import AgentInput, AgentOutput, BaseAgent


class CoachAgent(BaseAgent):
    name = "coach_agent"

    def run(self, agent_input: AgentInput) -> AgentOutput:
        message = agent_input.message.lower()
        dashboard = agent_input.context.get("dashboard", {})
        workout = dashboard.get("today_workout", {})
        nutrition = dashboard.get("nutrition", {})
        readiness = dashboard.get("readiness_score")
        memory_hint = self._memory_hint(agent_input.memories, agent_input.context)

        if "replan" in message or "missed" in message or "why" in message:
            answer = self._replanning_answer(agent_input.context)
        elif "workout" in message or "train" in message:
            answer = self._workout_answer(workout, readiness, memory_hint)
        elif "meal" in message or "protein" in message or "calorie" in message:
            answer = self._nutrition_answer(nutrition, memory_hint)
        elif "sleep" in message or "recovery" in message or "tired" in message:
            answer = self._recovery_answer(readiness, agent_input.memories, memory_hint)
        else:
            answer = self._general_answer(workout, nutrition, readiness, memory_hint)

        memory_to_write = None
        if any(word in message for word in ["hard", "tired", "busy", "missed", "struggle"]):
            memory_to_write = f"User coaching signal: {agent_input.message}"

        return AgentOutput(
            message=answer,
            recommendations=self._recommendations(workout, nutrition, readiness),
            memory_to_write=memory_to_write,
            confidence=0.82,
        )

    def _workout_answer(self, workout: dict, readiness: int | None, memory_hint: str) -> str:
        title = workout.get("title", "today's session")
        status = workout.get("status", "scheduled")
        intensity = workout.get("planned_intensity", "moderate")
        if readiness is not None and readiness < 55:
            return (
                f"Your readiness is low, so keep {title} technique-focused. "
                f"Use a lighter version, stop a few reps early, and count the win as showing up consistently.{memory_hint}"
            )
        if status == "missed":
            return (
                f"{title} is marked missed. Do not cram extra volume today. "
                f"Pick a smaller replacement slot, protect sleep tonight, and let the system adapt the next session.{memory_hint}"
            )
        return (
            f"{title} is currently {status}. Keep it {intensity}, start with an easy warm-up, "
            f"and log how it goes so the next recommendation has a stronger signal.{memory_hint}"
        )

    def _nutrition_answer(self, nutrition: dict, memory_hint: str) -> str:
        calories = nutrition.get("calories", 0)
        target = nutrition.get("calorie_target", 2200)
        protein = nutrition.get("protein_g", 0)
        protein_target = nutrition.get("protein_target_g", 150)
        protein_gap = max(0, round(protein_target - protein))
        calorie_gap = max(0, target - calories)
        return (
            f"You have logged {calories}/{target} calories and {protein}/{protein_target}g protein today. "
            f"The useful next move is a meal that closes about {min(protein_gap, 45)}g of protein without overshooting the remaining {calorie_gap} calories.{memory_hint}"
        )

    def _recovery_answer(self, readiness: int | None, memories: list[dict], memory_hint: str) -> str:
        if readiness is None:
            return "I do not have a recovery check-in yet. Log fatigue, soreness, and stress so I can adjust training intensity with better context."
        if readiness < 55:
            return (
                f"Your readiness is low at {readiness}. Keep training optional or reduced, choose an earlier bedtime, "
                f"and make tomorrow's plan smaller instead of trying to force intensity.{memory_hint}"
            )
        return f"Your readiness is {readiness}, which supports normal training if warm-ups feel good. Keep the first set honest and adjust from there.{memory_hint}"

    def _general_answer(self, workout: dict, nutrition: dict, readiness: int | None, memory_hint: str) -> str:
        next_action = "complete the scheduled workout"
        if readiness is not None and readiness < 55:
            next_action = "log recovery and choose a lower-intensity session"
        elif nutrition.get("protein_g", 0) < 80:
            next_action = "add one protein-forward meal"
        return (
            f"Today I see readiness at {readiness or 'unknown'}, workout status as {workout.get('status', 'scheduled')}, "
            f"and {nutrition.get('calories', 0)} calories logged. Best next action: {next_action}.{memory_hint}"
        )

    def _replanning_answer(self, context: dict) -> str:
        behavior_memory = context.get("behavior_memory", {})
        adherence_patterns = behavior_memory.get("adherence_patterns", [])
        workout_patterns = behavior_memory.get("workout_consistency", [])
        memory_hint = ""
        relevant_memory = (adherence_patterns + workout_patterns)[:1]
        if relevant_memory:
            memory_hint = f" I also found relevant memory: {relevant_memory[0]}"

        return (
            "Replanning happens when the system sees a behavior event such as a missed workout, poor sleep, or low readiness. "
            "The goal is to preserve consistency by shifting or reducing the next training target while keeping the plan realistic."
            f"{memory_hint}"
        )

    def _recommendations(self, workout: dict, nutrition: dict, readiness: int | None) -> list[dict]:
        recommendations = []
        if workout.get("status") == "missed":
            recommendations.append({"title": "Recover the missed workout", "body": "Move the session to tomorrow or reduce volume by 30% today."})
        if nutrition.get("protein_g", 0) < 80:
            recommendations.append({"title": "Raise protein signal", "body": "Add a high-protein meal so nutrition guidance becomes more accurate."})
        if readiness is not None and readiness < 55:
            recommendations.append({"title": "Lower intensity", "body": "Use a recovery-biased training day to protect consistency."})
        return recommendations

    def _memory_hint(self, memories: list[dict], context: dict) -> str:
        if memories:
            text = memories[0].get("text", "").strip()
            if text:
                return f" I am factoring in this pattern: {text[:160]}"

        behavior_memory = context.get("behavior_memory", {})
        for key in ["adherence_patterns", "sleep_trends", "nutrition_habits", "workout_consistency"]:
            values = behavior_memory.get(key) or []
            if values:
                return f" I am factoring in this pattern: {values[0][:160]}"
        return ""
