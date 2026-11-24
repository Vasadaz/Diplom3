"""Переходы между «Конструктором» и «Лентой заказов»."""
import allure

from config.config import BASE_URL
from pages.main_page import MainPage
from pages.order_feed_page import OrderFeedPage
from utils.expect import expect


@allure.feature("Навигация")
class TestNavigation:
    """Переключение основных разделов шапки."""

    @allure.title("Переход по клику на «Конструктор»")
    def test_open_constructor(self, driver):
        """С /feed клик по «Конструктор» возвращает на главную."""
        main = MainPage(driver)
        main.open_feed()
        main.click_constructor()

        expect(main.wait_opened().is_opened(), "конструктор").to_be_truthy()
        expect(driver.current_url.rstrip("/"), "URL после перехода") \
            .to_equal(BASE_URL)

    @allure.title("Переход по клику на «Лента заказов»")
    def test_open_order_feed(self, driver):
        """Клик по «Лента Заказов» открывает /feed со счётчиками."""
        MainPage(driver).open().wait_opened().click_order_feed()

        feed = OrderFeedPage(driver).wait_opened()
        expect(driver.current_url, "URL после перехода").to_contain("/feed")
        expect(feed.is_opened(), "счётчики ленты").to_be_truthy()
