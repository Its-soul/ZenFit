from dataclasses import dataclass


@dataclass(frozen=True)
class DemoUserProfile:
    email: str
    full_name: str
    persona: str
    goal: str
    fitness_level: str
    training_days: int
    adherence_level: float
    sleep_base: float
    sleep_volatility: float
    meal_consistency: float
    fatigue_bias: float
    workout_focus: str
    password: str = "DemoPass123!"


DEMO_USERS = [
    DemoUserProfile(
        email="ava.consistent@demo.fitness",
        full_name="Ava Consistent",
        persona="highly_consistent_athlete",
        goal="Improve endurance",
        fitness_level="Advanced",
        training_days=5,
        adherence_level=0.92,
        sleep_base=7.7,
        sleep_volatility=0.55,
        meal_consistency=0.88,
        fatigue_bias=0.2,
        workout_focus="Performance Conditioning",
    ),
    DemoUserProfile(
        email="ben.weightloss@demo.fitness",
        full_name="Ben Weight Loss",
        persona="beginner_weight_loss_user",
        goal="Lose fat",
        fitness_level="Beginner",
        training_days=4,
        adherence_level=0.72,
        sleep_base=6.9,
        sleep_volatility=0.9,
        meal_consistency=0.7,
        fatigue_bias=0.35,
        workout_focus="Fat Loss Foundation",
    ),
    DemoUserProfile(
        email="maya.inconsistent@demo.fitness",
        full_name="Maya Inconsistent",
        persona="adherence_struggles",
        goal="Improve consistency",
        fitness_level="Beginner",
        training_days=3,
        adherence_level=0.48,
        sleep_base=6.6,
        sleep_volatility=1.1,
        meal_consistency=0.45,
        fatigue_bias=0.45,
        workout_focus="Consistency Builder",
    ),
    DemoUserProfile(
        email="leo.fatigue@demo.fitness",
        full_name="Leo Fatigue",
        persona="poor_sleep_high_fatigue",
        goal="Build strength",
        fitness_level="Intermediate",
        training_days=4,
        adherence_level=0.62,
        sleep_base=5.8,
        sleep_volatility=1.0,
        meal_consistency=0.68,
        fatigue_bias=0.75,
        workout_focus="Strength With Recovery Guardrails",
    ),
    DemoUserProfile(
        email="nina.musclegain@demo.fitness",
        full_name="Nina Muscle Gain",
        persona="muscle_gain_focused",
        goal="Build muscle",
        fitness_level="Intermediate",
        training_days=5,
        adherence_level=0.82,
        sleep_base=7.2,
        sleep_volatility=0.7,
        meal_consistency=0.83,
        fatigue_bias=0.32,
        workout_focus="Hypertrophy Progression",
    ),
]

