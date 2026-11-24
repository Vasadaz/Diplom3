"""Page Object «Лента заказов»."""
from __future__ import annotations

from functools import partial

import allure
from selenium.common.exceptions import TimeoutException

from config.config import FEED_URL
from locators.order_feed_locators import OrderFeedLocators
from pages.base_page import BasePage

FEED_SETTLE_TIMEOUT = 10


class OrderFeedPage(BasePage):
    """Счётчики выполненных заказов и блок «В работе»."""

    def open(self) -> "OrderFeedPage":
        """Открывает /feed и ждёт, пока отрисуются счётчики."""
        self.driver.get(FEED_URL)
        return self

    def wait_opened(self) -> "OrderFeedPage":
        """Ждёт отрисовки счётчиков ленты."""
        self.wait_until(
            lambda _: self.is_opened(),
            message="счётчики ленты не отрисовались",
        )
        return self

    def is_opened(self) -> bool:
        """Страница ленты отрисована (есть блок статистики)."""
        return self.total_done() is not None

    # --- счётчики ---------------------------------------------------------

    def _value(self, locator: tuple[str, str], pattern: str) -> int | None:
        """Значение счётчика: XPath -> JS по подписи -> текст страницы."""
        for element in self.driver.find_elements(*locator):
            text = element.text.strip()
            if text.isdigit() or (text and text.replace(" ", "").isdigit()):
                return int(text.replace(" ", ""))
        value = self.dom.counter(pattern)
        if value is not None:
            return value
        return self.dom.number_after_label_in_text(pattern)

    def total_done(self) -> int | None:
        """Счётчик «Выполнено за всё время»."""
        return self._value(
            OrderFeedLocators.TOTAL_DONE_VALUE,
            OrderFeedLocators.TOTAL_DONE_PATTERN,
        )

    def today_done(self) -> int | None:
        """Счётчик «Выполнено за сегодня»."""
        return self._value(
            OrderFeedLocators.TODAY_DONE_VALUE,
            OrderFeedLocators.TODAY_DONE_PATTERN,
        )

    def _wait_growth(self, getter, baseline: int, name: str) -> int:
        """Ждёт роста счётчика; при таймауте один раз обновляет страницу.

        Счётчики приходят по WebSocket: если соединение не доставило
        обновление, перезагрузка сбрасывает состояние.
        """
        for attempt in range(2):
            try:
                return self.wait_until(
                    lambda _: (value := getter()) is not None
                    and value > baseline and value,
                    timeout=FEED_SETTLE_TIMEOUT,
                )
            except TimeoutException:
                if attempt:
                    raise AssertionError(
                        f"{name} не вырос за {FEED_SETTLE_TIMEOUT * 2} с: "
                        f"было {baseline}, стало {getter()}"
                    ) from None
                self.refresh()
        raise AssertionError("недостижимо")

    def wait_total_done_grows(self, baseline: int) -> int:
        """Ждёт, пока «Выполнено за всё время» превысит baseline."""
        return self._wait_growth(self.total_done, baseline,
                                 "Счётчик «Выполнено за всё время»")

    def wait_today_done_grows(self, baseline: int) -> int:
        """Ждёт, пока «Выполнено за сегодня» превысит baseline."""
        return self._wait_growth(self.today_done, baseline,
                                 "Счётчик «Выполнено за сегодня»")

    # --- блок «В работе» --------------------------------------------------

    def orders_in_progress(self) -> list[int]:
        """Номера заказов в блоке «В работе» (без ведущих нулей)."""
        numbers = [
            int(text.replace(" ", ""))
            for element in self.driver.find_elements(
                *OrderFeedLocators.IN_PROGRESS_ITEMS)
            for text in [element.text.strip()]
            if text.replace(" ", "").isdigit()
        ]
        return sorted(set(numbers) or self.dom.list_after_label(
            OrderFeedLocators.IN_PROGRESS_PATTERN))

    @allure.step("Дождаться заказа {number} в разделе «В работе»")
    def wait_order_in_progress(self, number: int) -> bool:
        """Ждёт появления номера в «В работе» с одним обновлением страницы."""
        for attempt in range(2):
            try:
                return self.wait_until(
                    partial(self._has_order, number),
                    timeout=FEED_SETTLE_TIMEOUT,
                )
            except TimeoutException:
                if attempt:
                    raise AssertionError(
                        f"Номер {number} не появился в «В работе» за "
                        f"{FEED_SETTLE_TIMEOUT * 2} с. В «В работе»: "
                        f"{self.orders_in_progress()}. Все номера в ленте: "
                        f"{self.dom.all_feed_numbers()}"
                    ) from None
                self.refresh()
        return False

    def _has_order(self, number: int, _driver) -> bool:
        """Номер есть среди заказов «В работе»."""
        return number in self.orders_in_progress()
