"""Переходы между «Конструктором» и «Лентой заказов»."""
import allure

from config.config import BASE_URL


@allure.feature("Навигация")
class TestNavigation:
    """Переключение основных разделов шапки."""

    @allure.title("Переход по клику на «Конструктор»")
    def test_open_constructor(self, guest_page):
        """С /feed клик по «Конструктор» возвращает на главную."""
        guest_page.open_feed()
        guest_page.click_constructor()
        guest_page.wait_opened()

        assert guest_page.is_opened(), "конструктор не отрисовался"
        assert guest_page.current_url.rstrip("/") == BASE_URL, (
            f"открылся {guest_page.current_url}"
        )

    @allure.title("Переход по клику на «Лента заказов»")
    def test_open_order_feed(self, guest_page, guest_feed):
        """Клик по «Лента Заказов» открывает /feed со счётчиками."""
        guest_page.open().wait_opened()
        guest_page.click_order_feed()
        guest_feed.wait_opened()

        assert "/feed" in guest_feed.current_url, (
            f"открылся {guest_feed.current_url}"
        )
        assert guest_feed.is_opened(), "счётчики ленты не отрисовались"
