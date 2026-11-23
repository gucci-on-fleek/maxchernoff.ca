// @ts-check

// Utility functions
const qsa = document.querySelectorAll.bind(document)
const qs = document.querySelector.bind(document)

/**
 * @template Value, Target
 * @param {(Value & Target) extends Extract<Value, Target> ? Value : (Target extends Value ? Value : never)} value
 * @param {new (...args: any[]) => Target} constructor
 * @returns {Value extends Target ? Target : (Target extends Value ? Target : never)}
 */
function assert_is(value, constructor) {
    if (!(value instanceof constructor)) {
        throw new Error(
            `Expected ${constructor.name}, got ${value?.constructor.name ?? value}`
        )
    }
    return /** @type {Value extends Target ? Target : never} */ (value)
}

const row_template = assert_is(qs("#item"), HTMLTemplateElement).content

class ItemElement extends HTMLElement {
    /**
     * @param {string} name
     * @param {string} quality
     * @param {string} unit_price
     * @param {string} count
     * @param {string} location
     * @param {string} stack_price
     */
    constructor(name, quality, unit_price, count, location, stack_price) {
        super()
        const shadow = this.attachShadow({
            mode: "closed", slotAssignment: "manual",
        })
        this.role = "row"
        shadow.appendChild(row_template.cloneNode(true))
        shadow.querySelectorAll("slot").forEach((slot) => {
            let text
            switch (slot.name) {
                case "name":
                    text = name
                    break
                case "quality":
                    text = quality
                    break
                case "unit_price":
                    text = unit_price
                    break
                case "count":
                    text = count
                    break
                case "location":
                    text = location
                    break
                case "stack_price":
                    text = stack_price
                    break
                default:
                    throw new Error(`Unknown slot name: ${slot.name}`)
            }
            const node = new Text(text)
            this.appendChild(node)
            slot.assign(node)
        })
    };
}

customElements.define("x-item", ItemElement)

function initialize_page() {
    const target = assert_is(qs("#target"), HTMLTableRowElement)
    let item = new ItemElement("Test Item", "Gold", "100g", "5", "Test Location", "500g")
    target.replaceWith(item)
    for (let i = 0; i < 10; i++) {
        const new_item = new ItemElement(`Test Item ${i}`, "Silver", `${i * 10}g`, `${i}`, `Location ${i}`, `${i * 10}g`)
        item.after(new_item)
        item = new_item
    }
}

/* Initialize as soon as the page is loaded */
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize_page)
} else {
    initialize_page()
}
