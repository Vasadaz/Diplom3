"""Page Object страницы авторизации."""
from __future__ import annotations

import allure
from selenium.webdriver.support import expected_conditions as EC

from config.config import LOGIN_URL
from locators.login_page_locators import LoginPageLocators
from locators.main_page_locators import MainPageLocators
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Вход по email и паролю через UI."""

    def open(self) -> "LoginPage":
        """Открывает форму входа."""
        self.driver.get(LOGIN_URL)
        self.find_visible(LoginPageLocators.EMAIL_INPUT)
        return self

    @allure.step("Войти как {email}")
    def login(self, email: str, password: str) -> "LoginPage":
        """Заполняет форму и ждёт возврата на главную."""
        self.send_keys(LoginPageLocators.EMAIL_INPUT, email)
        self.send_keys(LoginPageLocators.PASSWORD_INPUT, password)
        self.click(LoginPageLocators.SUBMIT_BUTTON)
        self.wait_until(
            EC.visibility_of_element_located(
                MainPageLocators.CONSTRUCTOR_TITLE),
            message="вход не выполнен: конструктор не открылся",
        )
        return self
