"""Счётчик ингредиента при добавлении в заказ."""
import allure

from utils.expect import expect


@allure.feature("Счётчик ингредиента")
class TestIngredientCounter:
    """Проверка увеличения счётчика."""

    @allure.title("Счётчик ингредиента увеличивается на 1")
    def test_counter_increments(self, main_page):
        """Перетаскивание начинки в корзину увеличивает её счётчик на 1.

        Индекс 2 — первая начинка: у булки второй ингредиент заменяет
        первый, и счётчик остаётся равным единице.
        """
        page = main_page.open().wait_opened()
        index = page.FILLING

        before = page.ingredient_counter(index)
        page.add_ingredient(index)
        page.wait_counter(index, before + 1)

        expect(page.ingredient_counter(index),
               "счётчик ингредиента").to_equal(before + 1)
