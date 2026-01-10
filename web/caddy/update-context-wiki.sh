#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff
set -euxo pipefail

if [ ! -d ".git" ]; then
    git clone --depth=1 --branch=mirror https://github.com/gucci-on-fleek/context-wiki-mirror.git .
fi

git pull origin mirror
restorecon -RF . || true
