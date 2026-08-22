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
    echo systemd-udevd
    return 0
}

# Install the files
install() {
    for file in \
        "dev-mapper-swap.swap" \
        "swap.target.wants/dev-mapper-swap.swap" \
    ; do
        inst_simple "$moddir/$file" "$systemdsystemunitdir/$file"
    done
    inst_simple "$moddir/crypttab" "/etc/crypttab"
}

