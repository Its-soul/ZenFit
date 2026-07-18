class RepCounter:
    def __init__(self, down_threshold: float, up_threshold: float):
        self.down_threshold, self.up_threshold, self.state, self.reps = down_threshold, up_threshold, "up", 0
    def update(self, angle: float) -> int:
        if angle <= self.down_threshold: self.state = "down"
        elif angle >= self.up_threshold and self.state == "down": self.reps += 1; self.state = "up"
        return self.reps
