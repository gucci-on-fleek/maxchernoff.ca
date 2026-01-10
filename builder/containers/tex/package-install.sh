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

    # For TeX Live
    perl-File-Find
    perl-interpreter
    perl-LWP-Protocol-https
    tar
    xz

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
    add-determinism
    dos2unix # For EOL conversion
    llvm # For `llvm-lipo`
    prename
    zip

    # gucci-on-fleek/context-wiki-mirror
    uv
    vips
)

for _ in $(seq 3); do
    dnf install \
        --assumeyes \
        --nodocs \
        --setopt=install_weak_deps=False \
        --setopt=keepcache=true \
        "${dnf_packages[@]}" \
    && break \
    || sleep $((30 + RANDOM % 90))
done
