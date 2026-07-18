ALIASES = {
    "roti": "whole wheat chapati flatbread",
    "chapati": "whole wheat chapati flatbread",
    "paneer": "indian cottage cheese paneer",
    "dal": "cooked lentils",
    "daal": "cooked lentils",
    "basmati rice": "cooked white basmati rice",
    "poha": "cooked flattened rice",
    "khichdi": "cooked rice and lentils",
}

def food_search_name(name: str) -> str:
    normalized = " ".join(name.lower().strip().split())
    return ALIASES.get(normalized, normalized)
