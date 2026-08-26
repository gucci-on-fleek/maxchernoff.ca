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
    inst_simple \
        "$moddir/dev-mapper-swap.swap" \
        "$systemdsystemunitdir/dev-mapper-swap.swap"

    mkdir -p "$initdir/$systemdsystemunitdir/swap.target.wants"
    ln -s \
        "../dev-mapper-swap.swap" \
        "$initdir/$systemdsystemunitdir/swap.target.wants/dev-mapper-swap.swap"

    cp -r --target-directory="$initdir/$systemdsystemunitdir/" \
        /usr/lib/systemd/system/*.device.d

    inst_simple /usr/sbin/swapon

    inst_simple \
        "$systemdsystemunitdir/systemd-cryptsetup@swap.service.d/override.conf"

    inst_simple "$moddir/crypttab" "/etc/crypttab"
}

