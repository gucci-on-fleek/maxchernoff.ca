#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
set -euxo pipefail

# Keep a cache to speed up the build
cache=/var/cache/rpm-ostree

# Build the container
rpm-ostree compose image \
    --initialize-mode=query \
    --format=ociarchive \
    --cachedir=$cache \
    --max-layers=200 \
    /root/source/fedora-iot.yaml \
    fedora-iot.ociarchive

# Get the composefs info
composefs_repo=/var/tmp/composefs-repo
mkdir -p "$composefs_repo"

image_id="$(\
    bootc internals cfs \
        --repo="$composefs_repo" \
        oci pull oci-archive:fedora-iot.ociarchive \
    | grep --only-matching --perl-regexp '(?<=^Fetching config ).*$'\
)"

fsverity_id="$(\
    bootc internals cfs \
        --repo="$composefs_repo" \
        oci compute-id "$image_id" \
)"

# Rebuild the container with composefs fsverity info
podman build \
    --no-cache \
    --security-opt=label=disable \
    --volume=/var/cache/libdnf5/:/var/cache/libdnf5/:rw \
    --build-arg="COMPOSEFS_FSVERITY=$fsverity_id" \
    --label=containers.composefs.fsverity="$fsverity_id" \
    --file=/root/source/Containerfile \
    --iidfile=./image-id \
    --tag=maxchernoff.ca/fedora-iot:latest \
    "."

# Push the container
skopeo copy \
    containers-storage:maxchernoff.ca/fedora-iot:latest \
    oci-archive:/root/output/fedora-iot.ociarchive
