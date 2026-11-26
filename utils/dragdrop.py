"""HTML5 drag&drop.

ActionChains.drag_and_drop с react-dnd не срабатывает: событие drop не
доходит до контейнера. Поэтому генерируем dragstart/dragover/drop напрямую
с общим объектом dataTransfer. Скрипт выполняется через BasePage, драйвер
здесь не используется.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - только для типов
    from pages.base_page import BasePage
    from selenium.webdriver.remote.webelement import WebElement

DRAG_AND_DROP_JS = """
const source = arguments[0];
const target = arguments[1];
const dataTransfer = {
    data: {},
    effectAllowed: 'all',
    dropEffect: 'move',
    files: [],
    items: [],
    types: [],
    setData(format, value) { this.data[format] = value; },
    getData(format) { return this.data[format] || ''; }
};
function fire(element, type) {
    const event = new Event(type, { bubbles: true, cancelable: true });
    Object.defineProperty(event, 'dataTransfer', { value: dataTransfer });
    element.dispatchEvent(event);
}
fire(source, 'dragstart');
fire(target, 'dragenter');
fire(target, 'dragover');
fire(target, 'drop');
fire(source, 'dragend');
"""


def drag_and_drop(page: "BasePage", source: "WebElement",
                  target: "WebElement") -> None:
    """Перетаскивает source на target событиями HTML5 DnD."""
    page.execute_script(DRAG_AND_DROP_JS, source, target)
