import math


def joint_angle(a, b, c) -> float:
    ba = (a[0]-b[0], a[1]-b[1]); bc = (c[0]-b[0], c[1]-b[1])
    denom = math.hypot(*ba) * math.hypot(*bc)
    if not denom: raise ValueError("Joint points must be distinct")
    cosine = max(-1, min(1, sum(x*y for x,y in zip(ba,bc))/denom))
    return math.degrees(math.acos(cosine))
