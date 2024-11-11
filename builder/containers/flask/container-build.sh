#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff
set -euo pipefail

# Create a mount point for the container
root=/mnt/build/
mkdir -p $root
cd $root

# Link the cache to the host
mkdir -p $root/var/cache/
ln -s /var/cache/libdnf5 $root/var/cache/libdnf5

# Install the base packages
dnf5 install \
    --assumeyes \
    --installroot=$root \
    --nodocs \
    --setopt=install_weak_deps=false \
    --setopt=keepcache=true \
    --use-host-config \
    coreutils-single \
    generic-release \
    glibc-minimal-langpack \
    python3-flask \
    python3-waitress

# Unlink the cache from the host
rm $root/var/cache/libdnf5

# Remove the caches, part 1
dnf5 clean all --installroot=$root

# Remove the excess packages
rpm --root=$root --nodeps --erase $(rpm --root=$root --query --all \
    | grep -Ev 'lib|python3|^basesystem|^filesystem|^setup|^generic-release|^ca-certificates')

# Remove the caches, part 2
rm -rf $root/var/{cache,log}/*
