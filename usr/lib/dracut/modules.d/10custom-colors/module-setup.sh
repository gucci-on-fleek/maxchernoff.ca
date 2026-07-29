#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff

# Prerequisites
check() {
    # Only include if explicitly enabled.
    return 255
}

# Dependencies
depends() {
	return 0
}

install() {
	inst_hook pre-trigger 10 "/usr/bin/console-colors.sh"
}
