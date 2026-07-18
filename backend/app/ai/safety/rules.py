from app.ai.safety.red_flags import RED_FLAGS
from app.ai.schemas import SafetyResult


def evaluate_safety(text: str) -> SafetyResult:
    normalized = text.lower()
    flags = [name for name, phrases in RED_FLAGS.items() if any(p in normalized for p in phrases)]
    if not flags: return SafetyResult(safe_to_continue=True)
    urgent = any(flag in flags for flag in {"emergency_symptoms", "severe_injury"})
    message = ("Stop exercising and seek urgent medical help now; contact local emergency services if symptoms are severe or ongoing." if urgent else "I can't help intensify this behavior. Please speak with a qualified healthcare professional for safe, individualized support.")
    return SafetyResult(safe_to_continue=False, severity="urgent" if urgent else "high", flags=flags, message=message)
