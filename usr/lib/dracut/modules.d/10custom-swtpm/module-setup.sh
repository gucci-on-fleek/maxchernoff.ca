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
    echo tpm2-tss
    return 0
}

# Install the files
install() {
    inst_multiple \
        "/usr/bin/swtpm"* \
        "/usr/lib/systemd/systemd-tpm2-swtpm" \
        "/etc/swtpm"* \
        "$systemdsystemunitdir/systemd-tpm2-swtpm.service" \
        "$systemdsystemunitdir/systemd-tpm2-setup-early.service" \
        "$systemdsystemunitdir/systemd-tpm2-setup.service" \
        "$systemdsystemunitdir/systemd-fsck@dev-disk-by\x2ddesignator-esp.service.d/override.conf" \
    # (end of files)
}

