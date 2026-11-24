"""Счётчики ленты заказов и блок «В работе»."""
import allure

from utils.expect import expect


@allure.feature("Лента заказов")
class TestOrderFeed:
    """Счётчики выполненных заказов и номер в «В работе»."""

    @allure.title("«Выполнено за всё время» растёт после создания заказа")
    def test_total_done_grows(self, main_page, order_feed_page):
        """Счётчик за всё время становится больше baseline."""
        feed = order_feed_page.open().wait_opened()
        baseline = feed.total_done()

        main_page.open().wait_opened().build_burger()
        main_page.place_order(close_modal=False)

        feed.open().wait_opened()
        expect(feed.wait_total_done_grows(baseline),
               "счётчик «Выполнено за всё время»").to_be_greater(baseline)

    @allure.title("«Выполнено за сегодня» растёт после создания заказа")
    def test_today_done_grows(self, main_page, order_feed_page):
        """Счётчик за сегодня становится больше baseline."""
        feed = order_feed_page.open().wait_opened()
        baseline = feed.today_done()

        main_page.open().wait_opened().build_burger()
        main_page.place_order(close_modal=False)

        feed.open().wait_opened()
        expect(feed.wait_today_done_grows(baseline),
               "счётчик «Выполнено за сегодня»").to_be_greater(baseline)

    @allure.title("Номер заказа появляется в «В работе»")
    def test_order_number_in_progress(self, main_page, order_feed_page):
        """Номер созданного заказа есть в блоке «В работе»."""
        main_page.open().wait_opened().build_burger()
        number = main_page.place_order(close_modal=False)

        feed = order_feed_page.open().wait_opened()
        expect(number, "номер заказа").to_be_greater(0)
        expect(feed.wait_order_in_progress(number),
               "заказ в «В работе»").to_be_truthy()
