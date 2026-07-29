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
    echo systemd-networkd systemd-udevd
    return 0
}

# Install the files
install() {
    for file in \
        "initrd-copy-network.service" \
        "sysefi.mount" \
        "systemd-networkd.service.wants/initrd-copy-network.service" \
    ; do
        inst_simple "$moddir/$file" "$systemdsystemunitdir/$file"
    done
}

