#!/bin/bash
set -euo pipefail

# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

# Install the necessary packages
dnf_packages=(
    # Base dependencies
    git
    libxcrypt-compat  # For `biber`

    # gucci-on-fleek/lua-widow-control
    curl
    libxslt
    moreutils
    pandoc
    poppler-utils
)

microdnf install --assumeyes --setopt=install_weak_deps=False "${dnf_packages[@]}"
