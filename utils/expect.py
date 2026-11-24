"""Утверждения с предметными сообщениями.

Стандартный `assert actual > baseline` при падении показывает два числа,
но не говорит, что это за числа. Здесь у каждого значения есть «субъект»:

    expect(counter, "счётчик «Выполнено за всё время»").to_be_greater(baseline)

    AssertionError: счётчик «Выполнено за всё время»: ожидалось > 4419,
    получено 4419
"""
from __future__ import annotations

from typing import Any, Iterable


class ExpectationError(AssertionError):
    """Провал утверждения. Наследник AssertionError — pytest считает падением."""


class Expect:
    """Цепочка утверждений над одним значением."""

    def __init__(self, actual: Any, subject: str = "значение") -> None:
        self.actual = actual
        self.subject = subject

    def _fail(self, expected: Any) -> None:
        raise ExpectationError(
            f"{self.subject}: ожидалось {expected}, получено {self.actual!r}"
        )

    def to_be_greater(self, other: Any) -> None:
        """Значение строго больше другого."""
        if not self.actual > other:
            self._fail(f"> {other}")

    def to_equal(self, other: Any) -> None:
        """Значение равно другому."""
        if self.actual != other:
            self._fail(f"{other}")

    def to_be_truthy(self) -> None:
        """Значение истинно (не пустое и не ноль)."""
        if not self.actual:
            self._fail("непустое значение")

    def to_contain(self, item: Any) -> None:
        """Значение содержит элемент."""
        if item not in self.actual:
            self._fail(f"элемент {item!r}")

    def to_contain_any(self, items: Iterable[Any]) -> None:
        """Значение содержит хотя бы один из элементов."""
        items = list(items)
        if not any(item in self.actual for item in items):
            self._fail(f"любой из {items!r}")


def expect(actual: Any, subject: str = "значение") -> Expect:
    """Начинает цепочку утверждений над значением."""
    return Expect(actual, subject)
