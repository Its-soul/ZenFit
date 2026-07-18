from app.zenfit_ai.safety.rules import evaluate_safety

def test_chest_pain(): assert evaluate_safety("I have chest pain during exercise").severity=="urgent"
def test_normal(): assert evaluate_safety("How should I structure a normal workout?").safe_to_continue
def test_restriction(): assert not evaluate_safety("I want to eat 500 calories a day").safe_to_continue
