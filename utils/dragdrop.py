"""HTML5 drag&drop.

ActionChains.drag_and_drop с react-dnd не срабатывает: событие drop
не доходит до контейнера. Поэтому генерируем dragstart/dragover/drop
напрямую с общим объектом dataTransfer.
"""
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


def drag_and_drop(driver, source, target) -> None:
    """Перетаскивает source на target событиями HTML5 DnD."""
    driver.execute_script(DRAG_AND_DROP_JS, source, target)
