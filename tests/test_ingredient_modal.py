"""Модальное окно «Детали ингредиента»."""
import allure

from utils.expect import expect

MODAL_TITLE = "Детали ингредиента"


@allure.feature("Детали ингредиента")
class TestIngredientModal:
    """Открытие и закрытие всплывающего окна."""

    @allure.title("Клик по ингредиенту открывает модалку с деталями")
    def test_modal_opens(self, main_page):
        """В модалке есть заголовок и название выбранного ингредиента."""
        main_page.open().wait_opened()

        name = main_page.open_ingredient_modal(0)
        modal_text = main_page.modal_text()

        expect(main_page.is_modal_opened(), "модалка").to_be_truthy()
        expect(modal_text, "текст модалки").to_contain(MODAL_TITLE)
        expect(name, "название ингредиента в карточке").to_be_truthy()
        expect(modal_text, "текст модалки").to_contain(name)

    @allure.title("Модалка закрывается кликом по крестику")
    def test_modal_closes_by_cross(self, main_page):
        """После клика по крестику окна на странице не остаётся."""
        main_page.open().wait_opened()
        main_page.open_ingredient_modal(0)

        expect(main_page.is_modal_opened(), "модалка").to_be_truthy()
        main_page.close_modal()
        expect(main_page.is_modal_opened(), "модалка после закрытия") \
            .to_equal(False)
