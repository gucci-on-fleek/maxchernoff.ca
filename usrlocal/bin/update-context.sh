#!/usr/bin/env bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
set -euo pipefail

# Set the environment variables
export PATH="/var/home/tex/context/texmf-linux-64/bin/:/usr/local/bin:/usr/bin"
cd /var/home/tex/context-installer/

# Update the base ConTeXt installation
./install.sh

# Update the binaries for all platforms
for platform in \
    freebsd-amd64 \
    linux \
    linux-aarch64 \
    linuxmusl \
    linuxmusl-64 \
    mswin \
    openbsd-amd64 \
    osx-64 \
    osx-arm64 \
    win64 \
; do \
    mtxrun --script install --platform=$platform --update
done

# Remake the ConTeXt formats
context --make > /dev/null
context --luatex --make > /dev/null

# Rebuild the font caches
mtxrun --script fonts --reload > /dev/null
mtxrun --luatex --script fonts --reload > /dev/null

# Update the ConTeXt modules
cd /var/home/tex/context/
mtxrun --script install-modules --install --all > /dev/null
