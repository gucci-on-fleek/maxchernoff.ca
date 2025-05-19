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

    # gucci-on-fleek/extractbb
    diffutils
    groff-perl
    parallel
    perl-Compress-Zlib

    # gucci-on-fleek/context-packaging
    awk
    binutils # For `ar`
    dos2unix # For EOL conversion
    llvm # For `llvm-lipo`
    prename
    tar
    xz
    zip
)

dnf install \
    --assumeyes \
    --nodocs \
    --setopt=install_weak_deps=False \
    --setopt=keepcache=true \
     "${dnf_packages[@]}"
