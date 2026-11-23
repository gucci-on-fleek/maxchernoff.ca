#!/usr/bin/env bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff
set -euo pipefail

by_username="/usr/local/by-username/$(id --user --name)"
if [ -d "${by_username}" ]; then
    echo "XDG_CONFIG_HOME=${by_username}"
fi
