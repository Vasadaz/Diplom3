"""Локаторы и текстовые шаблоны страницы «Лента заказов».

Разметка (проверено на стенде):
    <p>Выполнено за все время:</p>                      <- «все», не «всё»
    <p class="OrderFeed_number__2MbrQ ...">4419</p>     <- соседний <p>

    Готовы:
      <ul class="OrderFeed_orderListReady__... OrderFeed_orderList__...">
          <li class="text text_type_digits-default">034567</li>
    В работе:
      <ul class="OrderFeed_orderList__...">...</ul>

`orderListReady` — это блок «Готовы», а не «В работе», поэтому список
«В работе» ищется как первый <ul> после соответствующей подписи.
"""
from selenium.webdriver.common.by import By


class OrderFeedLocators:
    """Подписи счётчиков и списки заказов."""

    TOTAL_DONE_VALUE = (
        By.XPATH,
        "//p[contains(text(),'Выполнено за') and contains(text(),'время')]"
        "/following-sibling::p",
    )
    TODAY_DONE_VALUE = (
        By.XPATH,
        "//p[contains(text(),'Выполнено за') and contains(text(),'сегодня')]"
        "/following-sibling::p",
    )

    # Список заказов в разделе «В работе»
    IN_PROGRESS_LIST = (
        By.XPATH,
        "//p[contains(text(),'В работе')]/following::ul[1]",
    )
    IN_PROGRESS_ITEMS = (
        By.XPATH,
        "//p[contains(text(),'В работе')]/following::ul[1]/li",
    )
    # Список «Готовы» — нужен только для текста ошибки
    READY_LIST = (By.CSS_SELECTOR, "[class*='OrderFeed_orderListReady']")

    TOTAL_DONE_PATTERN = r"Выполнено за\s*(всё|все)"
    TODAY_DONE_PATTERN = r"Выполнено за\s*сегодня"
    IN_PROGRESS_PATTERN = r"В работе"
