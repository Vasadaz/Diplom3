"""Счётчик ингредиента при добавлении в заказ."""
import allure


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
        before = page.ingredient_counter(page.FILLING)

        page.add_ingredient(page.FILLING)
        page.wait_counter(page.FILLING, before + 1)

        after = page.ingredient_counter(page.FILLING)
        assert after == before + 1, (
            f"счётчик ингредиента #{page.FILLING}: было {before}, стало {after}"
        )
