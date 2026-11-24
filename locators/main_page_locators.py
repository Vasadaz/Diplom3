"""Локаторы страницы «Конструктор»."""
from selenium.webdriver.common.by import By


class MainPageLocators:
    """Шапка, карточки ингредиентов, модальное окно, корзина."""

    # --- шапка: кликаем по ссылке, а не по <p> внутри неё ---
    CONSTRUCTOR_TAB = (By.XPATH, "//a[.//p[normalize-space()='Конструктор']]")
    ORDER_FEED_TAB = (By.XPATH, "//a[.//p[normalize-space()='Лента Заказов']]")
    CONSTRUCTOR_TITLE = (By.XPATH, "//h1[normalize-space()='Соберите бургер']")

    # --- карточки ингредиентов ---
    # *= вместо ^= : href бывает и относительным, и абсолютным
    INGREDIENT_CARDS = (By.CSS_SELECTOR, "a[href*='/ingredient/']")
    INGREDIENT_COUNTER = (By.CSS_SELECTOR, "[class*='counter_counter__num']")

    # --- модальное окно ---
    # contentBox — именно окно; Modal_modal_overlay лежит отдельно и
    # перехватывает клики, поэтому в корень модалки его не берём
    MODAL_CONTENT = (By.CSS_SELECTOR, "[class*='Modal_modal__contentBox']")
    MODAL_TITLE = (By.XPATH,
                   "//*[contains(@class,'Modal_modal__contentBox')]//h2")
    MODAL_CLOSE = (By.XPATH, "//*[contains(@class,'Modal_modal__close')]")
    MODAL_CLOSE_FALLBACK = (
        By.XPATH,
        "//*[contains(@class,'Modal_modal__contentBox')]//button",
    )

    # --- конструктор бургера ---
    CONSTRUCTOR_BASKET = (
        By.XPATH,
        "//*[contains(@class,'BurgerConstructor_basket')]",
    )
    PLACE_ORDER_BUTTON = (By.XPATH, "//button[normalize-space()='Оформить заказ']")
