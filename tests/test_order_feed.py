"""Счётчики ленты заказов и блок «В работе»."""
import allure


@allure.feature("Лента заказов")
class TestOrderFeed:
    """Счётчики выполненных заказов и номер в «В работе»."""

    @allure.title("«Выполнено за всё время» растёт после создания заказа")
    def test_total_done_grows(self, main_page, order_feed_page):
        """Счётчик за всё время становится больше baseline."""
        baseline = order_feed_page.open().wait_opened().total_done()

        main_page.open().wait_opened().build_burger()
        main_page.place_order(close_modal=False)

        order_feed_page.open().wait_opened()
        actual = order_feed_page.wait_total_done_grows(baseline)
        assert actual > baseline, (
            f"«Выполнено за всё время»: было {baseline}, стало {actual}"
        )

    @allure.title("«Выполнено за сегодня» растёт после создания заказа")
    def test_today_done_grows(self, main_page, order_feed_page):
        """Счётчик за сегодня становится больше baseline."""
        baseline = order_feed_page.open().wait_opened().today_done()

        main_page.open().wait_opened().build_burger()
        main_page.place_order(close_modal=False)

        order_feed_page.open().wait_opened()
        actual = order_feed_page.wait_today_done_grows(baseline)
        assert actual > baseline, (
            f"«Выполнено за сегодня»: было {baseline}, стало {actual}"
        )

    @allure.title("Номер заказа появляется в «В работе»")
    def test_order_number_in_progress(self, main_page, order_feed_page):
        """Номер созданного заказа есть в блоке «В работе»."""
        main_page.open().wait_opened().build_burger()
        number = main_page.place_order(close_modal=False)

        order_feed_page.open().wait_opened()
        in_progress = order_feed_page.wait_order_in_progress(number)
        assert in_progress, (
            f"номер {number} не появился в «В работе»: "
            f"{order_feed_page.orders_in_progress()}"
        )
