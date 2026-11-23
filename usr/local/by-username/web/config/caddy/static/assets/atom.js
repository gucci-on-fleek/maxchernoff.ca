// @ts-check
// Source Code for maxchernoff.ca
// https://github.com/gucci-on-fleek/maxchernoff.ca
// SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
// SPDX-FileCopyrightText: 2025 Max Chernoff

// We need this file because Firefox does not properly obey the
// `disable-output-escaping` XSLT attribute.

function initialize_page() {
    const details = document.querySelectorAll("details.atom")
    for (const detail of details) {
        const nodes = detail.childNodes
        if (nodes.length == 2 && nodes[1] instanceof Text) {
            // We're using Firefox, so we need this workaround.
        } else {
            // We're using a browser that supports `disable-output-escaping`
            // so we don't need to do anything.
            return
        }
        // @ts-ignore
        const summary_text = nodes[0].outerHTML
        const content_text = nodes[1].textContent
        detail.innerHTML   = summary_text + content_text
    }
}

if (document.readyState === "loading") {
    // Initialize as soon as the page is loaded
    document.addEventListener("DOMContentLoaded", initialize_page)
} else {
    // DOMContentLoaded has already fired, so run it now
    initialize_page()
}
