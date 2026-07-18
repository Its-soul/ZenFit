from app.zenfit_ai.pose.angles import joint_angle
from app.zenfit_ai.pose.exercises import EXERCISES
from app.zenfit_ai.pose.rep_counter import RepCounter


class PoseAnalyzer:
    def __init__(self): self.counters = {}
    def analyze(self, exercise: str, landmarks: list[dict], timestamp=None) -> dict:
        if exercise not in EXERCISES: raise ValueError(f"Unsupported exercise: {exercise}")
        critical = [p for p in landmarks if p.get("name") in EXERCISES[exercise]["joint"]]
        if critical and any(float(p.get("visibility", 1)) < .6 for p in critical):
            return {"exercise": exercise, "body_visible": False, "reps": self.counters.get(exercise, RepCounter(0, 0)).reps, "observations": ["Move slightly farther back so your full body is visible."], "medical_grade": False}
        points = {p.get("name"): (p.get("x"),p.get("y")) for p in landmarks if p.get("name") and p.get("x") is not None and p.get("y") is not None}
        names = EXERCISES[exercise]["joint"]
        if any(n not in points for n in names): raise ValueError(f"Missing landmarks: {', '.join(n for n in names if n not in points)}")
        angle = joint_angle(*(points[n] for n in names)); cfg = EXERCISES[exercise]
        counter = self.counters.setdefault(exercise, RepCounter(cfg["down"], cfg["up"]))
        reps = counter.update(angle)
        observations = ["limited_range_of_motion"] if cfg["down"] < angle < cfg["up"] else []
        return {"exercise": exercise, "body_visible": True, "joint_angle": round(angle,1), "state": counter.state, "reps": reps, "observations": observations, "medical_grade": False}
