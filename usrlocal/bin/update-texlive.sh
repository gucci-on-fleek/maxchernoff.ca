#!/usr/bin/env bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
set -euo pipefail

# Set the environment variables
export PATH="/var/home/tex/texlive/bin/x86_64-linux:/usr/local/bin:/usr/bin"

# Update the TeX Live installation
tlmgr update --all --self

# Remake the ConTeXt formats
context --make
context --luatex --make

# Rebuild the font caches
luaotfload-tool --update
mtxrun --script fonts --reload
mtxrun --luatex --script fonts --reload
