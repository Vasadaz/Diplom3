"""Чтение значений из DOM.

Слой между JS-скриптами и Page Object: страницы обращаются к смыслу
(«номер заказа», «счётчик по подписи»), а не к селекторам. Хеши
BEM-классов в этом приложении меняются от сборки к сборке, поэтому всё,
что можно прочитать по тексту и структуре, читается по тексту.

Драйвер сюда не передаётся: чтение идёт через методы BasePage, поэтому
прямых обращений к WebDriver вне базового класса нет.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from selenium.webdriver.remote.webelement import WebElement

from utils import js_scripts as js
from utils.numbers import to_int

if TYPE_CHECKING:  # pragma: no cover - только для типов
    from pages.base_page import BasePage


class Dom:
    """Фасад над JS-чтением страницы."""

    def __init__(self, page: "BasePage") -> None:
        self.page = page

    # --- конструктор ------------------------------------------------------

    def card_name(self, card: WebElement) -> str:
        """Название ингредиента из карточки или её контейнера."""
        name = self.page.execute_script(js.CARD_NAME, card) or ""
        if name:
            return name.strip()
        return self.page.execute_script(
            js.CARD_NAME, self.page.parent_of(card)) or ""

    # --- заказ ------------------------------------------------------------

    def order_number(self) -> str:
        """Номер заказа из модалки; пусто, пока висит плейсхолдер 9999."""
        text = (self.page.execute_script(js.ORDER_NUMBER) or "").strip()
        return "" if text == js.ORDER_NUMBER_PLACEHOLDER else text

    # --- лента ------------------------------------------------------------

    def counter(self, label_pattern: str) -> int | None:
        """Значение счётчика, найденного по шаблону подписи."""
        value = self.page.execute_script(js.COUNTER, label_pattern)
        return value if isinstance(value, int) else None

    def list_after_label(self, label_pattern: str) -> list[int]:
        """Номера из списка, идущего после подписи (например, «В работе»)."""
        texts = self.page.execute_script(js.LIST_AFTER_LABEL, label_pattern)
        return [to_int(text) for text in texts or [] if to_int(text)]

    def all_feed_numbers(self) -> list[int]:
        """Все номера из списков ленты — для текста ошибки."""
        texts = self.page.execute_script(js.ALL_FEED_NUMBERS) or []
        return sorted({to_int(text) for text in texts if to_int(text)})

    def number_after_label_in_text(self, label_pattern: str) -> int | None:
        """Последний фолбэк: число в строке сразу после подписи."""
        lines = [line.strip() for line in self.page.body_text().splitlines()
                 if line.strip()]
        for index, line in enumerate(lines):
            if not re.search(label_pattern, line):
                continue
            for candidate in lines[index + 1:index + 4]:
                if re.fullmatch(r"[\d\s]+", candidate):
                    return to_int(candidate)
        return None
