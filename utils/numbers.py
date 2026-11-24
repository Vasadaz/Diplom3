"""Приведение чисел из интерфейса к int."""


def to_int(text: str) -> int:
    """'28 752' -> 28752; '034567' -> 34567; пустая строка -> 0."""
    digits = "".join(ch for ch in str(text) if ch.isdigit())
    return int(digits) if digits else 0
