#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff
set -euxo pipefail

# Keep a cache to speed up the build
cache=/var/cache/rpm-ostree

# Create a mount point for the container
root=$cache/root/
rm -rf $root || true
mkdir -p $root
cd $root

# Initialize the ostree repository
repo=$cache/repo/
rm -rf $repo || true
mkdir -p $repo
ostree --repo=$repo init --mode=bare-user

# ostree config settings
ostree config --repo=$repo set ex-integrity.composefs true
ostree config --repo=$repo set ex-integrity.readonly true
ostree config --repo=$repo set sysroot.bootloader none

# Build and push the container
rpm-ostree compose image \
    --initialize-mode=query \
    --format=registry \
    --cachedir=$cache \
    /root/source/fedora-iot.yaml \
    localhost:23719/fedora-iot:latest
