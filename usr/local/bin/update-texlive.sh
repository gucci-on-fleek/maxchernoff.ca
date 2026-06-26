#!/usr/bin/env bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
set -euo pipefail

# Set the environment variables
export PATH="/var/home/tex/texlive/bin/x86_64-linux:/usr/local/bin:/usr/bin"

# Update the TeX Live installation. Anything that depends on XeTeX will fail
# because we've uninstalled it, so ignore any errors.
tlmgr update --all --self || true

# Reset the ls-R dates so that ConTeXt doesn't auto-remake its formats
touch --date='2 days ago' /var/home/tex/texlive/texmf-{config,dist,local,var}/ls-R

# Remake the ConTeXt formats
context --make > /dev/null
context --luatex --make > /dev/null

# Rebuild the font caches
luaotfload-tool --update
mtxrun --script fonts --reload > /dev/null
mtxrun --luatex --script fonts --reload > /dev/null
