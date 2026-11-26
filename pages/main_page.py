"""Page Object «Конструктор»."""
from __future__ import annotations

import allure
from selenium.common.exceptions import TimeoutException

from config.config import BASE_URL, FEED_URL
from locators.main_page_locators import MainPageLocators
from pages.base_page import BasePage
from utils.dragdrop import drag_and_drop


class MainPage(BasePage):
    """Действия на странице конструктора."""

    BUN = 0
    FILLING = 2

    def open(self) -> "MainPage":
        """Открывает главную страницу."""
        self.open_url(BASE_URL)
        return self

    def open_feed(self) -> "MainPage":
        """Открывает ленту заказов напрямую по URL."""
        self.open_url(FEED_URL)
        return self

    def wait_opened(self) -> "MainPage":
        """Ждёт отрисовки конструктора."""
        self.wait_until(
            lambda _: self.is_opened(),
            message="конструктор не загрузился",
        )
        return self

    def is_opened(self) -> bool:
        """Страница конструктора отрисована."""
        return self.is_displayed(MainPageLocators.CONSTRUCTOR_TITLE)

    def click_constructor(self) -> None:
        """Клик по «Конструктор»."""
        self.click(MainPageLocators.CONSTRUCTOR_TAB)

    def click_order_feed(self) -> None:
        """Клик по «Лента Заказов»."""
        self.click(MainPageLocators.ORDER_FEED_TAB)

    # --- ингредиенты ------------------------------------------------------

    def card(self, index: int = 0):
        """Карточка ингредиента: 0-1 булки, дальше соусы и начинки."""
        return self.find_elements(MainPageLocators.INGREDIENT_CARDS)[index]

    def ingredient_name(self, index: int = 0) -> str:
        """Название ингредиента из карточки."""
        return self.dom.card_name(self.card(index))

    @allure.step("Открыть модалку ингредиента #{index}")
    def open_ingredient_modal(self, index: int = 0) -> str:
        """Клик по карточке открывает модалку. Возвращает название."""
        card = self.card(index)
        name = self.dom.card_name(card)
        self.click_element(card)
        self.wait_until(
            lambda _: self.is_modal_opened(),
            message="модалка ингредиента не открылась",
        )
        return name

    def modal_text(self) -> str:
        """Весь текст модального окна."""
        return self.get_text(MainPageLocators.MODAL_CONTENT)

    def is_modal_opened(self) -> bool:
        """Модалка есть в DOM и видима."""
        return self.is_displayed(MainPageLocators.MODAL_CONTENT)

    def close_modal(self) -> None:
        """Закрывает модалку крестиком (или Esc) и ждёт её исчезновения."""
        closed = self.try_click(
            MainPageLocators.MODAL_CLOSE,
            MainPageLocators.MODAL_CLOSE_FALLBACK,
        )
        if not closed:
            self.press_escape()
        self.wait_invisible(MainPageLocators.MODAL_CONTENT)

    # --- корзина ----------------------------------------------------------

    def add_ingredient(self, index: int = FILLING) -> None:
        """Перетаскивает ингредиент в корзину конструктора.

        Именно drag&drop добавляет ингредиент в заказ: клик по карточке
        открывает модалку с деталями и счётчик не меняет.
        """
        card = self.card(index)
        basket = self.find_visible(MainPageLocators.CONSTRUCTOR_BASKET)
        drag_and_drop(self, card, basket)

    def ingredient_counter(self, index: int = FILLING) -> int:
        """Счётчик ингредиента внутри его карточки (0, если не добавлен).

        Счётчик рендерится только при значении > 0, поэтому искать его
        по всей странице нельзя — индексы не совпадут с карточками.
        """
        card = self.card(index)
        counters = card.find_elements(*MainPageLocators.INGREDIENT_COUNTER)
        if not counters:
            counters = self.parent_of(card).find_elements(
                *MainPageLocators.INGREDIENT_COUNTER)
        return int(counters[0].text.strip()) if counters else 0

    def wait_counter(self, index: int, minimum: int = 1) -> None:
        """Ждёт, пока счётчик ингредиента станет не меньше minimum."""
        self.wait_until(
            lambda _: self.ingredient_counter(index) >= minimum,
            message=f"счётчик ингредиента #{index} не вырос до {minimum}",
        )

    def build_burger(self) -> None:
        """Собирает бургер: булка плюс начинка.

        Без булки заказ не оформляется. Ожидание одно на два перетаскивания:
        счётчики независимы, а лишний круг ожидания — это лишняя секунда.
        """
        self.add_ingredient(self.BUN)
        self.add_ingredient(self.FILLING)
        self.wait_until(
            lambda _: (self.ingredient_counter(self.BUN) >= 1
                       and self.ingredient_counter(self.FILLING) >= 1),
            message="в корзине нет булки и начинки",
        )

    @allure.step("Оформить заказ")
    def place_order(self, close_modal: bool = True) -> int:
        """Оформляет заказ и возвращает его номер.

        В заголовке модалки сначала висит плейсхолдер 9999, номер приходит
        только после успешного ответа сервера. Если номер не пришёл —
        заказ не создан, и об этом лучше сказать сразу, чем ждать таймаут
        на следующем шаге.
        """
        button = self.find_visible(MainPageLocators.PLACE_ORDER_BUTTON)
        if not button.is_enabled():
            raise AssertionError(
                "Кнопка «Оформить заказ» неактивна — в корзине нет булки"
            )
        self.click_element(button)

        try:
            number = self.wait_until(
                lambda _: self.dom.order_number() or False)
        except TimeoutException:
            raise AssertionError(
                "Номер заказа не появился: в модалке остался плейсхолдер "
                f"9999, значит заказ не создан. Текст модалки: "
                f"{self.modal_text()!r}"
            ) from None

        if close_modal:
            self.close_modal()
        return int(number)
