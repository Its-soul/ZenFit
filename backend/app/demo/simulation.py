from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from app.demo.profiles import DemoUserProfile


@dataclass
class DaySimulation:
    day: date
    workout: dict | None
    meals: list[dict]
    sleep: dict
    recovery: dict
    events: list[dict]


WORKOUT_TITLES = {
    "Performance Conditioning": ["Threshold Intervals", "Tempo Run", "Mobility Strength", "Zone 2 Endurance", "Power Circuit"],
    "Fat Loss Foundation": ["Full Body Strength", "Incline Walk", "Core Circuit", "Beginner Intervals", "Lower Body Basics"],
    "Consistency Builder": ["20 Minute Minimum", "Full Body Foundation", "Easy Cardio", "Mobility Reset", "Strength Basics"],
    "Strength With Recovery Guardrails": ["Upper Strength", "Lower Strength", "Recovery Lift", "Posterior Chain", "Technique Day"],
    "Hypertrophy Progression": ["Push Hypertrophy", "Pull Hypertrophy", "Leg Volume", "Upper Pump", "Glute Focus"],
}

MEAL_NAMES = [
    "Greek yogurt bowl",
    "Chicken rice bowl",
    "Protein smoothie",
    "Egg toast",
    "Paneer wrap",
    "Salmon potatoes",
    "Lentil curry",
    "Turkey sandwich",
    "Oats and berries",
    "Tofu stir fry",
    "Pizza night",
    "Burger meal",
]


class DemoBehaviorSimulator:
    def __init__(self, profile: DemoUserProfile, days: int, seed: int):
        self.profile = profile
        self.days = days
        self.random = random.Random(seed)

    def simulate(self) -> list[DaySimulation]:
        start = date.today() - timedelta(days=self.days - 1)
        simulations = []
        streak_bonus = 0.0

        for offset in range(self.days):
            current_day = start + timedelta(days=offset)
            phase = self._phase(offset)
            sleep = self._sleep(current_day, phase)
            recovery = self._recovery(current_day, sleep, phase)
            workout = self._workout(current_day, offset, recovery, streak_bonus, phase)
            meals = self._meals(current_day, workout, phase)
            events = self._events(workout, meals, sleep, recovery)

            if workout and workout["status"] == "completed":
                streak_bonus = min(streak_bonus + 0.01, 0.08)
            elif workout and workout["status"] == "missed":
                streak_bonus = max(streak_bonus - 0.04, -0.12)

            simulations.append(DaySimulation(day=current_day, workout=workout, meals=meals, sleep=sleep, recovery=recovery, events=events))

        return simulations

    def _phase(self, offset: int) -> str:
        progress = offset / max(self.days, 1)
        if self.profile.persona == "adherence_struggles" and 0.45 < progress < 0.68:
            return "decline"
        if self.profile.persona == "poor_sleep_high_fatigue" and 0.55 < progress < 0.78:
            return "fatigue_wave"
        if self.profile.persona == "beginner_weight_loss_user" and 0.25 < progress < 0.38:
            return "plateau"
        if self.profile.persona == "muscle_gain_focused" and progress > 0.72:
            return "progression"
        return "normal"

    def _sleep(self, current_day: date, phase: str) -> dict:
        base = self.profile.sleep_base
        if phase == "fatigue_wave":
            base -= 0.7
        if phase == "decline":
            base -= 0.35
        weekend_boost = 0.35 if current_day.weekday() >= 5 else 0
        duration = max(4.1, min(9.2, self.random.gauss(base + weekend_boost, self.profile.sleep_volatility)))
        quality = round(max(35, min(98, duration * 10 + self.random.gauss(12, 8) - self.profile.fatigue_bias * 10)))
        return {
            "sleep_date": current_day,
            "duration_hours": round(duration, 2),
            "quality_score": quality,
            "notes": self._sleep_note(duration, quality),
        }

    def _recovery(self, current_day: date, sleep: dict, phase: str) -> dict:
        fatigue = round(max(1, min(10, self.random.gauss(3.2 + self.profile.fatigue_bias * 4, 1.4))))
        soreness = round(max(1, min(10, self.random.gauss(3.4 + self.profile.training_days / 6, 1.2))))
        stress = round(max(1, min(10, self.random.gauss(3.0 + self.profile.fatigue_bias * 2, 1.4))))

        if sleep["duration_hours"] < 6:
            fatigue = min(10, fatigue + 2)
            stress = min(10, stress + 1)
        if phase in {"decline", "fatigue_wave"}:
            fatigue = min(10, fatigue + 2)
            soreness = min(10, soreness + 1)

        strain = (fatigue + soreness + stress) / 30
        readiness = max(1, min(100, round(100 - strain * 70)))
        return {
            "checkin_date": current_day,
            "fatigue_score": fatigue,
            "soreness_score": soreness,
            "stress_score": stress,
            "readiness_score": readiness,
            "notes": self._recovery_note(readiness, phase),
        }

    def _workout(self, current_day: date, offset: int, recovery: dict, streak_bonus: float, phase: str) -> dict | None:
        training_days = self._training_weekdays()
        if current_day.weekday() not in training_days:
            return None

        adherence = self.profile.adherence_level + streak_bonus
        if recovery["readiness_score"] < 50:
            adherence -= 0.14
        if phase == "decline":
            adherence -= 0.22
        if phase == "progression":
            adherence += 0.06

        completed = self.random.random() < max(0.08, min(0.98, adherence))
        status = "completed" if completed else "missed"
        title = self.random.choice(WORKOUT_TITLES[self.profile.workout_focus])
        intensity = "low" if recovery["readiness_score"] < 55 else self.random.choice(["moderate", "moderate", "high"])
        duration = self._progressive_duration(offset, intensity)
        completed_at = datetime.combine(current_day, time(hour=self.random.choice([7, 8, 18, 19]), minute=self.random.choice([0, 15, 30])), timezone.utc) if completed else None

        return {
            "title": title,
            "scheduled_date": current_day,
            "status": status,
            "planned_intensity": intensity,
            "duration_minutes": duration,
            "notes": self._workout_note(status, phase, recovery),
            "completed_at": completed_at,
        }

    def _meals(self, current_day: date, workout: dict | None, phase: str) -> list[dict]:
        meal_count = 3 if self.random.random() < self.profile.meal_consistency else self.random.choice([1, 2, 4])
        if phase == "decline":
            meal_count = max(1, meal_count - 1)

        meals = []
        base_hours = [8, 13, 20, 16]
        for index in range(meal_count):
            cheat = self.random.random() < (0.04 if self.profile.meal_consistency > 0.75 else 0.11)
            name = self.random.choice(["Pizza night", "Burger meal"] if cheat else MEAL_NAMES[:-2])
            calories = self._meal_calories(index, cheat)
            protein = max(5, round(calories * self.random.uniform(0.13, 0.24) / 4, 1))
            carbs = max(10, round(calories * self.random.uniform(0.35, 0.55) / 4, 1))
            fat = max(4, round(calories * self.random.uniform(0.18, 0.35) / 9, 1))
            hour = base_hours[index] if index < len(base_hours) else 21
            logged_at = datetime.combine(current_day, time(hour=hour, minute=self.random.choice([0, 10, 20, 35, 45])), timezone.utc)
            meals.append(
                {
                    "name": name,
                    "meal_type": ["breakfast", "lunch", "dinner", "snack"][min(index, 3)],
                    "calories": calories,
                    "protein_g": protein,
                    "carbs_g": carbs,
                    "fat_g": fat,
                    "logged_at": logged_at,
                }
            )
        return meals

    def _events(self, workout: dict | None, meals: list[dict], sleep: dict, recovery: dict) -> list[dict]:
        events = []
        if workout:
            event_type = "workout.completed" if workout["status"] == "completed" else "workout.missed"
            events.append({"event_type": event_type, "payload": {"planned_intensity": workout["planned_intensity"], "title": workout["title"]}})
        if meals:
            events.append({"event_type": "meal.logged", "payload": {"meal_count": len(meals), "calories": sum(meal["calories"] for meal in meals)}})
        events.append({"event_type": "sleep.logged", "payload": {"duration_hours": sleep["duration_hours"], "quality_score": sleep["quality_score"]}})
        if sleep["duration_hours"] < 6 or sleep["quality_score"] < 55:
            events.append({"event_type": "sleep.poor", "payload": {"duration_hours": sleep["duration_hours"], "quality_score": sleep["quality_score"]}})
        if recovery["readiness_score"] < 55:
            events.append({"event_type": "recovery.low", "payload": {"readiness": recovery["readiness_score"]}})
        return events

    def _training_weekdays(self) -> set[int]:
        schedules = {
            3: {0, 2, 4},
            4: {0, 1, 3, 5},
            5: {0, 1, 2, 4, 5},
        }
        return schedules.get(self.profile.training_days, {0, 2, 4})

    def _progressive_duration(self, offset: int, intensity: str) -> int:
        base = 35 + min(20, math.floor(offset / max(self.days, 1) * 20))
        if intensity == "low":
            base -= 10
        if intensity == "high":
            base += 8
        return max(20, min(80, base + self.random.choice([-5, 0, 5])))

    def _meal_calories(self, index: int, cheat: bool) -> int:
        if cheat:
            return self.random.randint(750, 1150)
        if self.profile.goal == "Build muscle":
            base = [650, 750, 820, 350][min(index, 3)]
        elif self.profile.goal == "Lose fat":
            base = [380, 520, 620, 220][min(index, 3)]
        else:
            base = [480, 650, 700, 260][min(index, 3)]
        return max(180, round(self.random.gauss(base, base * 0.18)))

    def _sleep_note(self, duration: float, quality: int) -> str:
        if duration < 6:
            return "Short sleep; likely recovery impact."
        if quality > 82:
            return "Restful sleep and strong recovery signal."
        return "Normal sleep log."

    def _recovery_note(self, readiness: int, phase: str) -> str:
        if readiness < 55:
            return "Readiness dip; adaptive planning should reduce intensity."
        if phase == "progression":
            return "Responding well to progressive overload."
        return "Standard recovery check-in."

    def _workout_note(self, status: str, phase: str, recovery: dict) -> str:
        if status == "missed" and phase == "decline":
            return "Missed during adherence decline phase."
        if status == "missed":
            return "Missed session; candidate for adaptive replanning."
        if recovery["readiness_score"] < 55:
            return "Completed with lower readiness; monitor fatigue."
        return "Completed as planned."

