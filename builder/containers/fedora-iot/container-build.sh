#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
set -euxo pipefail

# Keep a cache to speed up the build
cache=/var/cache/rpm-ostree

# Build and push the container
rpm-ostree compose image \
    --initialize-mode=query \
    --format=registry \
    --cachedir=$cache \
    --max-layers=200 \
    /root/source/fedora-iot.yaml \
    localhost:!!registry.port!!/fedora-iot:latest
