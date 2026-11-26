# Stellar Burgers — автотесты UI

Дипломный проект, задание 3: сквозные UI-тесты для
[Stellar Burgers](https://stellarburgers.education-services.ru/) на Selenium + pytest,
паттерн Page Object, отчётность в Allure.

**Текущий статус:** 8 тестов × 2 браузера = `16 passed` (Chrome, Firefox, Windows).

---

## Стек

| Слой | Инструмент |
|---|---|
| Автотесты | Python 3.10+, pytest |
| Браузер | Selenium WebDriver (Chrome, Firefox) |
| Отчёт | allure-pytest |
| API-подготовка данных | requests |
| Генерация данных | faker |

Драйверы скачиваются автоматически через Selenium Manager — отдельно
устанавливать chromedriver и geckodriver не нужно.

## Установка

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Состав `requirements.txt`: `selenium`, `pytest`, `allure-pytest`, `requests`, `faker`.

## Запуск

```powershell
pytest -v                        # все тесты, Chrome + Firefox
pytest --browser chrome -v       # только Chrome
pytest --browser firefox -v      # только Firefox
pytest --headless -v             # без окон браузера
pytest tests/test_order_feed.py -v --browser chrome
```

Отчёт Allure:

```powershell
pytest -v
allure serve allure-results
```

Параллельный запуск (нужен `pytest-xdist`):

```powershell
pip install pytest-xdist
pytest -n 2 -v
```

> Учтите: два воркера × два браузера — это четыре окна и четыре заказа на общем
> стенде. Счётчики ленты поэтому проверяются как «стало больше baseline», а не
> «ровно +1».

### Переменные окружения

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `SB_BASE_URL` | `https://stellarburgers.education-services.ru` | стенд |
| `SB_TIMEOUT` | `15` | таймаут явных ожиданий, с |
| `SB_POLL` | `0.25` | частота опроса в ожиданиях, с |
| `SB_API_TIMEOUT` | `10` | таймаут запросов к API, с |

---

## Структура

```
.
├── conftest.py                  фикстуры: браузер на сессию, пользователь, вход
├── pytest.ini                   настройки прогона и testpaths
├── requirements.txt
├── api/
│   └── user_api.py              регистрация и удаление пользователя через API
├── config/
│   └── config.py                URL и таймауты (из переменных окружения)
├── data/
│   └── test_data.py             генерация уникального пользователя
├── locators/
│   ├── login_page_locators.py   форма входа
│   ├── main_page_locators.py    шапка, карточки, модалка, корзина
│   └── order_feed_locators.py   счётчики и списки ленты
├── pages/
│   ├── base_page.py             ожидания, клики, состояние элементов
│   ├── login_page.py            вход через форму
│   ├── main_page.py             конструктор: ингредиенты, корзина, заказ
│   └── order_feed_page.py       лента: счётчики, «В работе»
├── tests/
│   ├── test_navigation.py       переходы между разделами
│   ├── test_ingredient_modal.py модалка «Детали ингредиента»
│   ├── test_counter.py          счётчик ингредиента
│   └── test_order_feed.py       счётчики ленты и «В работе»
├── tools/
│   ├── inspect_dom.py           дамп разметки (диагностика локаторов)
│   └── feed_probe.py            проба оформления заказа и чтения ленты
└── utils/
    ├── dom.py                   чтение значений из DOM (фасад над JS)
    ├── js_scripts.py            JS-скрипты
    ├── dragdrop.py              HTML5 drag&drop
    └── numbers.py               приведение чисел интерфейса к int
```

---

## Что покрыто

| Файл тестов | Сценарий | Проверка |
|---|---|---|
| `test_navigation.py` | переход по клику на «Конструктор» | с `/feed` открывается главная и конструктор отрисован |
| `test_navigation.py` | переход по клику на «Лента заказов» | открывается `/feed`, блок статистики отрисован |
| `test_ingredient_modal.py` | клик по ингредиенту | открывается модалка с заголовком «Детали ингредиента» и названием выбранного ингредиента |
| `test_ingredient_modal.py` | крестик в модалке | после закрытия модалки на странице нет |
| `test_counter.py` | добавление ингредиента в заказ | счётчик начинки увеличивается на 1 |
| `test_order_feed.py` | создание заказа | «Выполнено за всё время» становится больше baseline |
| `test_order_feed.py` | создание заказа | «Выполнено за сегодня» становится больше baseline |
| `test_order_feed.py` | оформление заказа | номер заказа появляется в разделе «В работе» |

Каждый тест выполняется в Chrome и Firefox (параметризация фикстуры браузера).

---

## Как устроено

### Слои

```
tests/  →  pages/  →  locators/ + utils/dom.py  →  DOM
```

* **tests** знают только про Page Object. Локаторов и `driver` в тестах нет вообще.
* **pages** возвращают значения (`int` номер заказа, `str` название, `bool`), а не `WebElement`.
* **pages/base_page.py** — единственное место, где живёт `WebDriver`. Навигация, JS,
  клавиатура и чтение состояния доступны страницам по наследованию: `open_url()`,
  `execute_script()`, `press_escape()`, `current_url`, `body_text()`.
* **utils/dom.py** — единственное место, где значения читаются из DOM через JS.

### Page Object

```python
def test_order_number_in_progress(self, main_page, order_feed_page):
    main_page.open().wait_opened().build_burger()
    number = main_page.place_order(close_modal=False)

    feed = order_feed_page.open().wait_opened()
    assert feed.wait_order_in_progress(number), (
        f"номер {number} не появился в «В работе»"
    )
```

### Ожидания

`time.sleep` в проекте нет вообще. Всё через `BasePage.wait_until(predicate, message, timeout)`
поверх `WebDriverWait` с частотой опроса `POLL_FREQUENCY`. У каждого ожидания есть
сообщение — при падении видно, чего именно не дождались.

### Проверки

Только обычный `assert` pytest. Действия выполняются до проверок, в каждом
тесте одна проверяемая ситуация, после ассерта шагов нет. Сообщение в ассерте
показывает фактическое состояние:

```python
actual = order_feed_page.wait_total_done_grows(baseline)
assert actual > baseline, f"«Выполнено за всё время»: было {baseline}, стало {actual}"
```

### Allure

* `@allure.feature` на классе тестов, `@allure.title` на тесте;
* `@allure.step` на ключевых действиях (`Войти как ...`, `Оформить заказ`,
  `Дождаться заказа N в разделе «В работе»`);
* при падении автоматически прикладываются скриншот, URL и page source.

---

## Решения, которые важно знать

**Добавление ингредиента — только drag&drop.** Клик по карточке открывает модалку
с деталями и счётчик не меняет. В Page Object это два разных метода:
`open_ingredient_modal()` и `add_ingredient()`. `ActionChains.drag_and_drop`
с react-dnd не работает — событие `drop` не доходит, поэтому в `utils/dragdrop.py`
генерируются HTML5-события `dragstart/dragenter/dragover/drop` с общим `dataTransfer`.

**Заказ собирается из булки и начинки.** Без булки заказ не оформляется: в модалке
остаётся плейсхолдер `9999` вместо номера. `place_order()` ждёт значение, отличное
от `9999`, и при таймауте падает с текстом модалки — иначе провал всплывает на
следующем шаге в виде непонятного таймаута в ленте.

**Локаторы не завязаны на хеши BEM-классов.** `OrderFeed_number__2MbrQ`,
`OrderFeed_orderListReady__1YFem`, `Modal_modal__container__Wo2l_` меняются при
пересборке фронта. Счётчики ищутся по подписи:

```python
TOTAL_DONE_VALUE = (
    By.XPATH,
    "//p[contains(text(),'Выполнено за') and contains(text(),'время')]/following-sibling::p",
)
```

**В разметке «Выполнено за все время:»** — без «ё» и с двоеточием, поэтому точное
`text()='Выполнено за всё время'` не находит ничего.

**`OrderFeed_orderListReady` — это блок «Готовы», а не «В работе».** Список «В работе»
берётся как первый `<ul>` после соответствующей подписи.

**Вход через форму, а не через localStorage.** Подстановка одного `accessToken`
без `refreshToken` даёт сброс сессии на первом же запросе к `/api/auth/user`,
и заказ оформляется от неавторизованного пользователя.

**Браузер поднимается один раз на сессию.** Фикстура `_browser` (scope=session)
создаёт драйвер, фикстура `driver` перед каждым тестом чистит cookies и
localStorage. Это 2 старта драйвера вместо 16 при сохранении изоляции тестов.

---

## Диагностика

Если локатор перестал совпадать с разметкой, не нужно угадывать классы:

```powershell
python tools/inspect_dom.py     # дамп карточки, модалок, блоков статистики
python tools/feed_probe.py      # состав корзины, состояние кнопки, номер в модалке,
                                # оба списка ленты, история заказов
```

Оба скрипта только читают страницы и создают по одному заказу под новым
пользователем; файлов проекта не меняют. `inspect_dom.py` пишет отчёт в
`tools/dom_dump.txt`.

---

## Ограничения

* Тесты идут против общего стенда: другие студенты создают заказы параллельно,
  поэтому счётчики сравниваются с baseline («стало больше»), а не на «+1».
* Покрыт UI-функционал из задания. API-тестов, проверок адаптивности и
  кроссбраузерности Safari/Edge в проекте нет.
* Тесты намеренно не проверяют вёрстку (цвета, отступы) — только поведение.
* Данные не изолируются на уровне стенда: пользователь создаётся через API и
  удаляется в фикстуре, но созданные заказы остаются в ленте.

## Частые проблемы

| Симптом | Причина | Что делать |
|---|---|---|
| `IndexError: list index out of range` | список карточек получен без ожидания | использовать `find_elements()` из `BasePage` — он ждёт появления |
| `ElementClickInterceptedException` | клик перехватывает `Modal_modal_overlay` | `click_element()` с JS-фолбэком, `close_modal()` перед навигацией |
| В модалке заказа `9999` | заказ не создан (нет булки / не авторизованы) | `build_burger()`, вход через `LoginPage` |
| Счётчик не растёт | данные не пришли по WebSocket | ожидание делает одну перезагрузку страницы |
| `TimeoutException` на счётчике | подпись ищется точным `text()` | `contains()` + `utils/dom.py` |
