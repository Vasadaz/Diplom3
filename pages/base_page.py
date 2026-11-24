"""Базовый Page Object.

Правила слоя:
  * все ожидания — через wait_until с POLL_FREQUENCY, без time.sleep;
  * методы возвращают значения (число, текст, bool), а не WebElement;
  * страница знает про DOM только через self.dom.
"""
from __future__ import annotations

from typing import Any, Callable

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config.config import DEFAULT_TIMEOUT, POLL_FREQUENCY
from utils.dom import Dom


class BasePage:
    """Общие операции для всех страниц."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.dom = Dom(driver)

    # --- ожидания ---------------------------------------------------------

    def wait_until(self, predicate: Callable[[WebDriver], Any],
                   message: str = "", timeout: float | None = None) -> Any:
        """Ждёт, пока предикат вернёт истинное значение."""
        return WebDriverWait(
            self.driver,
            timeout or DEFAULT_TIMEOUT,
            POLL_FREQUENCY,
        ).until(predicate, message)

    def find_element(self, locator: tuple[str, str]) -> WebElement:
        """Ждёт появления элемента в DOM."""
        return self.wait_until(EC.presence_of_element_located(locator))

    def find_elements(self, locator: tuple[str, str]) -> list[WebElement]:
        """Ждёт появления всех элементов.

        Без ожидания find_elements возвращает то, что успело отрисоваться,
        то есть чаще всего пустой список.
        """
        return self.wait_until(EC.presence_of_all_elements_located(locator))

    def find_visible(self, locator: tuple[str, str]) -> WebElement:
        """Ждёт, пока элемент станет видимым."""
        return self.wait_until(EC.visibility_of_element_located(locator))

    def wait_invisible(self, locator: tuple[str, str]) -> None:
        """Ждёт исчезновения элемента или его скрытия."""
        self.wait_until(EC.invisibility_of_element_located(locator))

    # --- действия ---------------------------------------------------------

    def click(self, locator: tuple[str, str]) -> None:
        """Ждёт кликабельности и кликает."""
        self.click_element(
            self.wait_until(EC.element_to_be_clickable(locator)))

    def click_element(self, element: WebElement) -> None:
        """Клик по найденному элементу с JS-фолбэком.

        На /feed в DOM висит Modal_modal_overlay, который перехватывает
        клики по шапке и карточкам.
        """
        try:
            element.click()
        except (ElementClickInterceptedException,
                StaleElementReferenceException):
            self.driver.execute_script("arguments[0].click();", element)

    def send_keys(self, locator: tuple[str, str], value: str) -> None:
        """Очищает поле и вводит значение."""
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(value)

    def get_text(self, locator: tuple[str, str]) -> str:
        """Текст видимого элемента без пробелов по краям."""
        return self.find_visible(locator).text.strip()

    def parent_of(self, element: WebElement) -> WebElement:
        """Родительский элемент."""
        return element.find_element(By.XPATH, "..")

    # --- состояние --------------------------------------------------------

    def is_present(self, locator: tuple[str, str]) -> bool:
        """Наличие элемента без ожидания и без падения теста."""
        return bool(self.driver.find_elements(*locator))

    def is_displayed(self, locator: tuple[str, str]) -> bool:
        """Элемент есть в DOM и видим."""
        elements = self.driver.find_elements(*locator)
        return bool(elements) and elements[0].is_displayed()

    def try_click(self, *locators: tuple[str, str],
                  timeout: float = 5) -> bool:
        """Кликает по первому доступному из локаторов."""
        for locator in locators:
            try:
                element = WebDriverWait(self.driver, timeout, POLL_FREQUENCY)\
                    .until(EC.element_to_be_clickable(locator))
            except TimeoutException:
                continue
            self.click_element(element)
            return True
        return False

    def refresh(self) -> None:
        """Перезагружает страницу: сбрасывает состояние, пришедшее по WS."""
        self.driver.refresh()
