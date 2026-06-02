from __future__ import annotations


DEFAULT_WEIGHT_KG = 70
DEFAULT_HEIGHT_CM = 170
DEFAULT_AGE = 30


class NutritionTargetCalculator:
    def calculate(
        self,
        *,
        weight_kg: float | None,
        height_cm: float | None,
        age: int | None,
        biological_sex: str | None,
        training_frequency: int | None,
        goal: str | None,
    ) -> dict:
        estimated = False
        if not weight_kg:
            weight_kg = DEFAULT_WEIGHT_KG
            estimated = True
        if not height_cm:
            height_cm = DEFAULT_HEIGHT_CM
            estimated = True
        if not age:
            age = DEFAULT_AGE
            estimated = True

        sex = (biological_sex or "").strip().lower()
        sex_adjustment = -161 if sex == "female" else 5
        if sex not in {"male", "female"}:
            estimated = True

        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + sex_adjustment
        calories = bmr * self._activity_multiplier(training_frequency)
        goal_key = self._goal_key(goal)
        calories += {"lose_fat": -300, "build_muscle": 250, "maintain": 0}[goal_key]
        protein_multiplier = {"lose_fat": 2.0, "build_muscle": 1.6, "maintain": 1.4}[goal_key]

        return {
            "calorie_target": max(1200, round(calories)),
            "protein_target_g": round(weight_kg * protein_multiplier, 1),
            "targets_are_estimated": estimated,
        }

    @staticmethod
    def _activity_multiplier(training_frequency: int | None) -> float:
        days = training_frequency or 3
        if days >= 6:
            return 1.725
        if days >= 4:
            return 1.55
        return 1.375

    @staticmethod
    def _goal_key(goal: str | None) -> str:
        normalized = (goal or "").strip().lower().replace("-", " ")
        if normalized in {"lose fat", "fat loss", "weight loss"}:
            return "lose_fat"
        if normalized in {"build muscle", "muscle gain", "hypertrophy", "build strength"}:
            return "build_muscle"
        return "maintain"
