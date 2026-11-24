"""JS-скрипты чтения DOM.

Только сами скрипты, без обвязки: фасад для страниц — в utils/dom.py.
Все селекторы здесь опираются на смысл (текст подписи, порядок узлов),
а не на хеши BEM-классов, которые меняются при каждой пересборке фронта.
"""

# Плейсхолдер номера заказа: пока модалка грузится, в заголовке 9999.
ORDER_NUMBER_PLACEHOLDER = "9999"

CARD_NAME = r"""
const box = arguments[0];
if (!box) { return ''; }
const leaves = Array.from(box.querySelectorAll('*'))
    .filter(el => el.children.length === 0)
    .map(el => el.textContent.trim())
    .filter(t => t && !/^[\d\s]+$/.test(t) && t !== 'руб.' && t !== 'шт.');
return leaves.length ? leaves[0] : '';
"""

ORDER_NUMBER = r"""
const box = document.querySelector("[class*='Modal_modal__contentBox']");
if (!box) { return ''; }
const title = box.querySelector('h2');
const text = (title || box).textContent.replace(/\s+/g, ' ').trim();
const match = text.match(/\d{3,}/);
return match ? match[0] : '';
"""

COUNTER = r"""
const re = new RegExp(arguments[0]);
const labels = Array.from(document.querySelectorAll('p'))
    .filter(el => el.children.length === 0 && re.test(el.textContent.trim()));
if (!labels.length) { return null; }
const label = labels[0];
let box = label.parentElement;
for (let level = 0; level < 3 && box; level++) {
    const values = Array.from(box.querySelectorAll('p, span, div'))
        .filter(el => el !== label && !re.test(el.textContent.trim()))
        .map(el => el.textContent.trim())
        .filter(t => t && /^[\d\s]+$/.test(t));
    if (values.length) {
        const digits = values[0].replace(/\D/g, '');
        if (digits) { return parseInt(digits, 10); }
    }
    box = box.parentElement;
}
return null;
"""

LIST_AFTER_LABEL = r"""
const re = new RegExp(arguments[0]);
const labels = Array.from(document.querySelectorAll('p'))
    .filter(el => re.test(el.textContent.trim()));
if (!labels.length) { return []; }
const label = labels[0];
const lists = Array.from(document.querySelectorAll('ul')).filter(function (ul) {
    return label.compareDocumentPosition(ul) & Node.DOCUMENT_POSITION_FOLLOWING;
});
if (!lists.length) { return []; }
return Array.from(lists[0].querySelectorAll('li'))
    .map(el => el.textContent.trim())
    .filter(Boolean);
"""

ALL_FEED_NUMBERS = r"""
return Array.from(document.querySelectorAll("[class*='OrderFeed_orderList'] li"))
    .map(el => el.textContent.trim())
    .filter(Boolean);
"""
