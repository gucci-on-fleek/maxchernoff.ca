// @ts-check

/* Source Code for maxchernoff.ca
   https://github.com/gucci-on-fleek/maxchernoff.ca
   SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
   SPDX-FileCopyrightText: 2024 Max Chernoff */

/**
 * @type {Object<String, Function>}
 */
let template, elements

/**
 * Populates the template object with its members
 * @effects Modifies global `template`
 */
function create_templates() {
    /*
     * We're handling the elements a little differently here: instead
     * of calling `document.getElementById` to get an element, you need
     * to index the global object `elements`. This seems equivalent, but
     * it provides a few advantages:
     *  1) Elements are cached after they have been retrieved. This may
     *     provide a very small speedup
     *  2) The major reason is so that we can properly typecast elements
     *     globally. This way, we can typecast all of the elements in one
     *     place, and avoid messy typecasts inline.
     */
    const __elements = { // Holds the elements that require a typecast
        item_table: /** @type {HTMLTableElement} */ (document.getElementById("item_table"))
    }

    const elements_handler = {
        get(target, property) {
            if (target[property] === undefined || target[property] === null) {
                target[property] = document.getElementById(property)
            }
            return target[property]
        },

        deleteProperty(target, property) {
            target[property].remove()
            delete target[property]

            return true
        }
    }

    elements = new Proxy(__elements, elements_handler)

    /*
     * The `template` global is much like the `elements` global, however
     * the motivation is slightly different. The point of the `template`
     * being constructed this way is so that most of the templates can
     * be handled in a general way, but exceptions are easy to add.
     */
    const __template = {
        _header_cell(x) { // Creates each header cell
            const clone = clone_template(elements.header_cell_base).firstElementChild
            clone.insertAdjacentHTML("beforeend", x)

            return /** @type {HTMLTableHeaderCellElement} */ (clone)
        },
        column_header_cell(x) {
            const cell = this._header_cell(x)
            cell.setAttribute("scope", "col")

            return cell
        },
        row_header_cell(x) {
            const cell = this._header_cell(x)
            cell.setAttribute("scope", "row")

            return cell
        },
        link(x) { // Creates the email cell
            const clone = clone_template(elements.link_base).firstElementChild
            const a = clone.firstElementChild.firstElementChild
            a.href += x
            a.textContent = x

            return clone
        },
        header(x) { // Creates the header row
            const clone = clone_template(elements.header_base).firstElementChild
            clone.appendChild(x)

            return clone
        },
    }

    const template_handler = {
        get(target, property) {
            if (target[property] === undefined) {
                target[property] = () => clone_template(elements[`${property}_base`]).firstElementChild
            }
            return target[property]
        }
    }

    template = new Proxy(__template, template_handler)
}


/**
 * Initialize necessary features after the site has fully loaded
 * @effects Modifies global variables, adds event listeners
 */
function initialize_page() {
    create_templates()

    const listeners = [
        [elements.filter, "keyup", () => filter_table()],
        [elements.down_button, "click", () => download_as_csv(_csv_string)],
        [document.body, "dragover", event => event.preventDefault()], // Needed for the drop event to run
        ...[...qsa("summary")].map(x => [x, "mousedown", event => { // Allow a middle-click to open all summary/details elements
            event.preventDefault()
            event.target.click()
        }]),
    ]
    for (const [element, type, callback] of listeners) {
        element.addEventListener(type, callback)
    }

    load_responses()
}


if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize_page) // Initialize as soon as the page is loaded
} else { // DOMContentLoaded has already fired, so run it now
    initialize_page()
}

/**
 * Loads the response file
 * @effects Modifies the `#table_container` DOM element
 */
function load_responses() {
    loading_screen({show_loading: true, show_input: false})

    get_files(["requests.tsv"]).then(
    function (requests) {
        _csv_string = requests[0]

        array_to_table(csv_to_array(_csv_string))
    })
    .finally(() => loading_screen({show_loading: false, show_input: true}))
    .catch(() => show_element(elements.error))
}


/**
 * A shorthand for `document.querySelector()`
 * @param {String} selector - A selector for an element to retrieve
 * @returns {HTMLElement} The element requested
 * @effects None
 */
function qs(selector) {
    return document.querySelector(selector)
}


/**
 * A shorthand for `document.querySelectorAll()`
 * @param {String} selector - A selector for the elements to retrieve
 * @returns {NodeListOf<Element>} The elements requested
 * @effects None
 */
function qsa(selector) {
    return document.querySelectorAll(selector)
}


/**
 * Clone a template
 * @param {HTMLTemplateElement} element - The element to clone
 * @returns {HTMLElement} A duplicate of the initial element
 * @effects None
 */
function clone_template(element) {
    return /** @type {HTMLElement} */ (element.content.cloneNode(true))
}


/**
 * Makes an `HTML` table from `CSV` and inserts it into the DOM.
 * @param {String[][]} array - The `CSV` to make a table from
 * @effects None directly, however called functions modify the DOM.
 */
let array_to_table = function (array) {
    let table = template.table()
    table = make_html_table(array, table)
    table = make_header([["Date", "URL", "Referrer", "User Agent", "Status"]], table)
    set_output(table)
    enable_table_sort()
    enable_arrow_navigation(table)
}


function enable_arrow_navigation(table) {
    table.addEventListener("keydown", function (event) {
        const el = event.target
        const col = el.cellIndex
        const row = el.parentElement.rowIndex
        const goto_cell = (row, col) => {
            const cell = table?.rows[row]?.cells[col]
            if (cell) {
                event.preventDefault()
                cell.focus()
            }
        }

        switch ([event.key, event.shiftKey] + "") {
            case ["Enter", "false"] + "":
            case ["ArrowDown", "false"] + "":
                goto_cell(row + 1, col)
                break
            case ["ArrowUp", "false"] + "":
            case ["Enter", "true"] + "":
                goto_cell(row - 1, col)
                break
            case ["ArrowRight", "false"] + "":
            case ["Tab", "false"] + "":
                goto_cell(row, col + 1)
                break
            case ["ArrowLeft", "false"] + "":
            case ["Tab", "true"] + "":
                goto_cell(row, col - 1)
                break
        }
    })
}


/**
 * Hides a DOM element
 * @param {HTMLElement} element - The element to hide
 * @effects Modifies the DOM to hide the element
 */
function hide_element(element) {
    element.hidden = true
}


/**
 * Shows a DOM element that has been previously hidden
 * @param {HTMLElement} element - The element to show
 * @effects Modifies the DOM to show the element
 */
function show_element(element) {
    element.hidden = false
}


/**
 * Displays a loading indicator
 * @param {{show_loading?: Boolean; show_input?: Boolean}} arguments - Should we show/hide the input box or the loading screen
 * @effects Modifies the DOM to show/hide the loading display
 */
function loading_screen({show_loading = true, show_input = true} = {}) {
    const loading = elements.loading

    if (show_loading) {
        show_element(loading)
    } else {
        hide_element(loading)
    }
}


/**
 * Download an array of URLs
 * @param {String[]} paths - An array of URLs to fetch
 * @returns {Promise} A promise holding the text for each request
 * @effects Initiates a network request to download the URLs
 */
function get_files(paths) {
    const requests = []
    for (const path of paths) {
        requests.push(fetch(path, {cache: "no-store"}).then(x => x.text()))
    }
    return Promise.all(requests)
}


let _csv_string // Global, holds the CSV so that it can later be downloaded

/**
 * Parse the `CSV` file into an array
 * @param {String} csv - The `CSV` file
 * @returns {String[][]} - An array representing the `CSV`
 * @remarks This is a very basic `CSV` parser. It just splits on
 *          commas and newlines, so any edge cases **will not** be
 *          accounted for. However, there won't be any edge cases
 *          since we control the input `CSV`.
 * @effects None
 */
function csv_to_array(csv) {
    return csv
        .split("\n")
        .map(x => x.split("\t"))
        .slice(0, -1) // We made the csv file, so there won't be any edge cases
}


/**
 * Adds text to an `HTML` element
 * @param {HTMLTableCellElement } cell - The cell to add the text
 * @param {String} text - The text to add
 * @effects Modifies input param `cell`
 */
function cell_text(cell, text) {
    cell.appendChild(document.createTextNode(text))
}


/**
 * Converts the array into the `HTML` table
 * @param {String[][]} array - The array to make into a table
 * @param {HTMLTableElement} table - The document fragment to make the table in
 * @returns {HTMLTableElement} The input array as an `HTML` table
 * @effects None
 */
function make_html_table(array, table) {
    for (const csv_row of array) {
        const table_row = table.insertRow()

        for (const [index, csv_cell] of csv_row.entries()) {
            switch (index) {
                case 0: { // Name
                    table_row.appendChild(template.row_header_cell(csv_cell))
                    break
                }
                case 1: // URL
                case 2: { // Referrer
                    table_row.appendChild(template.link(csv_cell))
                    break
                }
                default: {
                    const table_cell = table_row.insertCell()
                    cell_text(table_cell, csv_cell)
                }
            }
        }
    }
    return table
}

/**
 * Extracts the header from the array and returns an `HTML` table header
 * @param {String[][]} array - The array to make into a header
 * @param {HTMLTableElement} table - The document fragment to make the table in
 * @returns {HTMLTableElement} The input array as an `HTML` table header
 * @effects None
 */
function make_header(array, table) {
    const html = new DocumentFragment()
    const row = array[0]
    for (const cell of row) {
        html.append(template.column_header_cell(cell))
    }
    table.tHead.appendChild(template.header(html))

    return table
}


/**
 * Put the table's `HTML` into the document
 * @param {HTMLTableElement} table - The `HTML` fragment to add to the document
 * @effects Modifies DOM element `#table_container`.
 */
const set_output = (function () {
    let previous_output = false // True on 2nd/3rd/xth save file loads

    return function (table) {
        hide_element(qs("article"))

        if (previous_output) { // Remove old table
            delete elements.item_table
        }
        table = calculate_sum(table) // eslint-disable-line no-param-reassign

        const container = elements.table_container
        container.appendChild(table)

        show_element(qs("article"))
        previous_output = true
    }
})()


/**
 * Show the table sums in its footer
 * @param {HTMLTableElement} table - The document fragment to sum
 * @effects None
 */
function calculate_sum(table) {
    const foot = table.tFoot
    let tot_price = 0
    let tot_count = 0
    const current_hidden_filter_class = `filter_${_filter_class}`

    while (foot.rows[0]) { // Remove old footers
        foot.rows[0].remove()
    }

    for (const row of table.tBodies[0].rows) {
        if (row.classList.contains(current_hidden_filter_class)) {
            continue
        } // Skip if hidden by filter
        tot_count += 1
    }

    const row = foot.insertRow()
    const blank = () => cell_text(row.insertCell(), "")

    cell_text(row.insertCell(), "Total")
    cell_text(row.insertCell(), tot_count)

    return table
}

/**
 * Adds an `onclick` event listener to an element
 * @param {*} element - The element which receives the click
 * @param {Function} callback - Callback function. Takes the event as its only parameter
 * @remarks This function is better than just `element
 *          .addEventListener("click", callback)` because it takes
 *          keyboard use into consideration. This is very important for
 *          accessibility, since the keyboard should be able to do
 *          everything that the mouse can.
 * @effects Adds event listeners and modifies DOM
 */
function add_click_event(element, callback) {
    element.addEventListener("click", callback)

    element.setAttribute("tabindex", "0")
    element.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault()
            callback(event)
        }
    })
}


/**
 * Allow the table to be sorted by clicking on the headings
 * @effects Initializes table sorting. Adds event listeners to the table headers.
 */
function enable_table_sort() {
    const get_header_cells = () => elements.item_table.tHead.rows[0].cells // This needs to be a function since the actual table element is replaced multiple times

    for (const cell of get_header_cells()) {
        add_click_event(cell, function ({target}) {
            const index = target.cellIndex
            const next_sort_ascending = target.getAttribute("aria-sort") !== "ascending"

            sort_table(index, next_sort_ascending)

            get_header_cells()[index].focus()
            get_header_cells()[index].setAttribute("aria-sort", next_sort_ascending ? "ascending" : "descending")
            filter_table()
        })
    }
}


const sort_table = (function () {
    const sort = {
            test() { return true }, // Fallback String
            compare(a, b) { return a.localeCompare(b) }
        }

    /**
     * Sorts the item table
     * @param {Number} column_index - The column to sort by
     * @param {Boolean} ascending - `true` if the sort should be smallest-to-largest; `false` if the sort should be largest-to-smallest
     * @effects Modifies the item table in the DOM
     */
    return function (column_index, ascending = true) {
        const csv_array = csv_to_array(_csv_string)
        const sorting_array = csv_array.slice(1) // Remove the header
        let compare

        if (ascending) {
            compare = (a, b) => sort.compare(a[column_index], b[column_index])
        } else {
            compare = (a, b) => sort.compare(b[column_index], a[column_index])
        }

        sorting_array.sort(compare)

        sorting_array.splice(0, 0, csv_array[0]) // Add back the header
        array_to_table(sorting_array)
    }
})()


/**
 * Allow the user to download their save as a CSV
 * @param {String} text
 * @remarks Called by the download button
 * @effects Temporarily modifies DOM. Triggers a download.
 */
function download_as_csv(text) {
    const element = document.createElement("a")
    element.setAttribute("href", `data:text/tab-separated-values;charset=utf-8,${encodeURIComponent(text)}`)
    element.setAttribute("download", "responses.tsv")
    hide_element(element)

    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
}


let _filter_class = 1 // Monotonically incrementing counter to ensure unique CSS classes
/**
 * Allows the table to be filtered
 * @remarks The naïve version of this function directly applied
 *          'display: none' to each row. However, this triggered
 *          a repaint for each row, since it was removed from display.
 *          The optimized version of this function applies a new
 *          and unique class to each row whenever a filter is
 *          applied. Then—and only then—can we hide that class.
 *          This means that only one repaint is triggered instead
 *          of one for each row. In benchmarks, this is about 250%
 *          faster than the old function.
 * @effects Modifies CSS and the `class` attribute of table rows. Modifies global variable `filter_class`.
 */
function filter_table() {
    const filter = elements.filter.value
    const table = elements.item_table
    const rows = table.tBodies[0].rows
    const search = RegExp(filter, "i")
    const last_filter_class = _filter_class - 1 // The class that we're adding
    const last_last_filter_class = last_filter_class - 1 // The class that we're removing
    const filter_class_name = `filter_${_filter_class}`
    const last_last_filter_class_name = `filter_${last_last_filter_class}`

    for (const row of rows) {
        if (!row.textContent.match(search)) {
            row.classList.add(filter_class_name)
        }
        row.classList.remove(last_last_filter_class_name) // Cleanup old filter classes
    }

    const style = document.styleSheets[0]
    style.insertRule(`.${filter_class_name} {visibility: collapse}`)
    if (last_last_filter_class >= 0) {
        style.deleteRule(1)
    }

    calculate_sum(table) // Update the footer after the filter is applied

    _filter_class++ // Increment the class's name
}
