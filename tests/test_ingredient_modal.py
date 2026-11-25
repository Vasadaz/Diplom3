"""Модальное окно «Детали ингредиента»."""
import allure

MODAL_TITLE = "Детали ингредиента"


@allure.feature("Детали ингредиента")
class TestIngredientModal:
    """Открытие и закрытие всплывающего окна."""

    @allure.title("Клик по ингредиенту открывает модалку с деталями")
    def test_modal_opens(self, main_page):
        """В модалке есть заголовок и название выбранного ингредиента."""
        page = main_page.open().wait_opened()

        name = page.open_ingredient_modal(0)
        modal_text = page.modal_text()

        assert page.is_modal_opened(), "модалка не открылась"
        assert MODAL_TITLE in modal_text, (
            f"в модалке нет заголовка {MODAL_TITLE!r}: {modal_text!r}"
        )
        assert name, "не удалось прочитать название ингредиента из карточки"
        assert name in modal_text, (
            f"в модалке нет ингредиента {name!r}: {modal_text!r}"
        )

    @allure.title("Модалка закрывается кликом по крестику")
    def test_modal_closes_by_cross(self, main_page):
        """После клика по крестику окна на странице не остаётся."""
        page = main_page.open().wait_opened()
        page.open_ingredient_modal(0)
        page.close_modal()

        assert not page.is_modal_opened(), "модалка осталась открытой"
