"""Локаторы страницы авторизации."""
from selenium.webdriver.common.by import By


class LoginPageLocators:
    """Форма входа."""

    EMAIL_INPUT = (By.XPATH, "//input[@name='name']")
    PASSWORD_INPUT = (By.XPATH, "//input[@type='password']")
    SUBMIT_BUTTON = (By.XPATH, "//button[normalize-space()='Войти']")
