"""Фикстуры: браузер на сессию, пользователь через API, вход через UI.

Браузер поднимается один раз на всю сессию, состояние сбрасывается перед
каждым тестом. Так прогон не платит за старт драйвера 16 раз, а изоляция
тестов сохраняется.
"""
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from api.user_api import UserApi
from data.test_data import generate_user
from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.main_page import MainPage
from pages.order_feed_page import OrderFeedPage

BROWSERS = ("chrome", "firefox")


def pytest_addoption(parser: pytest.Parser) -> None:
    """Добавляет CLI-опции: --browser и --headless."""
    parser.addoption("--browser", action="store", default=None,
                     choices=list(BROWSERS))
    parser.addoption("--headless", action="store_true", default=False)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Прикладывает к Allure снимок, URL и разметку при падении теста."""
    outcome = yield
    report = outcome.get_result()
    if not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    page = BasePage(driver)
    with allure.step("Состояние страницы на момент падения"):
        allure.attach(page.screenshot(), "screenshot",
                      allure.attachment_type.PNG)
        allure.attach(page.current_url, "url", allure.attachment_type.TEXT)
        allure.attach(page.page_source, "page_source",
                      allure.attachment_type.HTML)


def _build_driver(browser: str, headless: bool):
    """Создаёт драйвер нужного браузера."""
    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        if headless:
            options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)
    else:
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1920, 1080)

    # готовность элементов проверяют явные ожидания, а не событие load
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(0)
    return driver


@pytest.fixture(scope="session", params=BROWSERS)
def _browser(request: pytest.FixtureRequest):
    """Браузер на всю сессию: по одному на Chrome и Firefox."""
    browser = request.param
    from_cli = request.config.getoption("--browser")
    if from_cli and from_cli != browser:
        pytest.skip(f"Пропущено: --browser={from_cli}")

    driver = _build_driver(browser, request.config.getoption("--headless"))
    yield driver
    driver.quit()


@pytest.fixture
def driver(_browser):
    """Чистое состояние браузера перед каждым тестом."""
    BasePage(_browser).reset_state()
    return _browser


@pytest.fixture
def user_api() -> UserApi:
    """Создаёт пользователя через API и удаляет его после теста."""
    data = generate_user()
    api = UserApi()
    api.register(**data)
    api.user = data
    yield api
    api.delete()


@pytest.fixture
def authorized_driver(driver, user_api: UserApi):
    """Авторизует пользователя через форму входа.

    Через localStorage не логинимся: приложение без refreshToken
    сбрасывает сессию на первом же запросе к /api/auth/user.
    """
    user = user_api.user
    LoginPage(driver).open().login(user["email"], user["password"])
    return driver


@pytest.fixture
def guest_page(driver) -> MainPage:
    """MainPage без авторизации — для проверок навигации."""
    return MainPage(driver)


@pytest.fixture
def guest_feed(driver) -> OrderFeedPage:
    """OrderFeedPage без авторизации — для проверок навигации."""
    return OrderFeedPage(driver)


@pytest.fixture
def main_page(authorized_driver) -> MainPage:
    """MainPage в авторизованной сессии."""
    return MainPage(authorized_driver)


@pytest.fixture
def order_feed_page(authorized_driver) -> OrderFeedPage:
    """OrderFeedPage в авторизованной сессии."""
    return OrderFeedPage(authorized_driver)
