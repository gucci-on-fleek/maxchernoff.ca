#!/bin/sh
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
set -eu

{
    printf '\e[?24;112c'  # Cursor
    printf '\e]P0000000'  # Black
    printf '\e]P1c01c28'  # Dark Red
    printf '\e]P226a269'  # Dark Green
    printf '\e]P3a2734c'  # Brown
    printf '\e]P412488b'  # Dark Blue
    printf '\e]P5a347ba'  # Dark Magenta
    printf '\e]P62aa1b3'  # Dark Cyan
    printf '\e]P7d0cfcc'  # Light Grey
    printf '\e]P85e5c64'  # Dark Grey
    printf '\e]P9f66151'  # Red
    printf '\e]PA33da7a'  # Green
    printf '\e]PBe9ad0c'  # Yellow
    printf '\e]PC2a7bde'  # Blue
    printf '\e]PDc061cb'  # Magenta
    printf '\e]PE33c7de'  # Cyan
    printf '\e]PFffffff'  # White
} | tee /dev/tty?
