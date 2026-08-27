#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff

# Prerequisites
check() {
    # Always include
    return 0
}

# Dependencies
depends() {
	return 0
}

install() {
    # Install the user database
    userdb_args=(
        --multiplexer="false"
        --output="classic"
        --disposition="system"
        --disposition="intrinsic"
    )
    userdbctl "${userdb_args[@]}" user  > "$initdir/etc/passwd"
    userdbctl "${userdb_args[@]}" group > "$initdir/etc/group"
}
