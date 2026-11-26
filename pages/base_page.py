"""Базовый Page Object.

Единственное место, где живёт WebDriver. Объекты страниц не обращаются
к `self._driver` напрямую, а используют методы базового класса: навигацию,
JS, клавиатуру, чтение состояния.

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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config.config import BASE_URL, DEFAULT_TIMEOUT, POLL_FREQUENCY
from utils.dom import Dom

CLEAR_STORAGE_JS = (
    "window.localStorage.clear(); window.sessionStorage.clear();"
)


class BasePage:
    """Общие операции для всех страниц."""

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
        self.dom = Dom(self)

    # --- навигация --------------------------------------------------------

    def open_url(self, url: str) -> None:
        """Открывает адрес в текущей вкладке."""
        self._driver.get(url)

    @property
    def current_url(self) -> str:
        """Текущий адрес страницы."""
        return self._driver.current_url

    @property
    def page_source(self) -> str:
        """Разметка текущей страницы."""
        return self._driver.page_source

    def refresh(self) -> None:
        """Перезагружает страницу: сбрасывает состояние, пришедшее по WS."""
        self._driver.refresh()

    def screenshot(self) -> bytes:
        """Снимок экрана в PNG."""
        return self._driver.get_screenshot_as_png()

    def reset_state(self) -> None:
        """Приводит браузер к чистому состоянию перед тестом."""
        self.open_url(BASE_URL)
        self.execute_script(CLEAR_STORAGE_JS)
        self._driver.delete_all_cookies()

    # --- JS и клавиатура --------------------------------------------------

    def execute_script(self, script: str, *args: Any) -> Any:
        """Выполняет JS в контексте страницы."""
        return self._driver.execute_script(script, *args)

    def press_escape(self) -> None:
        """Отправляет Esc в страницу — закрывает модалку без крестика."""
        self.body().send_keys(Keys.ESCAPE)

    def body(self) -> WebElement:
        """Элемент body."""
        return self._driver.find_element(By.TAG_NAME, "body")

    def body_text(self) -> str:
        """Видимый текст страницы."""
        return self.body().text

    # --- ожидания ---------------------------------------------------------

    def wait_until(self, predicate: Callable[[WebDriver], Any],
                   message: str = "", timeout: float | None = None) -> Any:
        """Ждёт, пока предикат вернёт истинное значение."""
        return WebDriverWait(
            self._driver,
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
            self.execute_script("arguments[0].click();", element)

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

    def find_all(self, locator: tuple[str, str]) -> list[WebElement]:
        """Все элементы по локатору прямо сейчас, без ожидания."""
        return self._driver.find_elements(*locator)

    def is_present(self, locator: tuple[str, str]) -> bool:
        """Наличие элемента без ожидания и без падения теста."""
        return bool(self.find_all(locator))

    def is_displayed(self, locator: tuple[str, str]) -> bool:
        """Элемент есть в DOM и видим."""
        elements = self.find_all(locator)
        return bool(elements) and elements[0].is_displayed()

    def try_click(self, *locators: tuple[str, str],
                  timeout: float = 5) -> bool:
        """Кликает по первому доступному из локаторов."""
        for locator in locators:
            try:
                element = WebDriverWait(
                    self._driver, timeout, POLL_FREQUENCY
                ).until(EC.element_to_be_clickable(locator))
            except TimeoutException:
                continue
            self.click_element(element)
            return True
        return False
