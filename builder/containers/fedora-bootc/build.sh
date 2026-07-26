#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff
set -euxo pipefail

# Get the script directory
script_dir="$(dirname "$(realpath "$0")")"

# Initialize the build directory
temp_dir="$(mktemp --directory --tmpdir=/var/tmp/)"
trap 'rm -rf "$temp_dir"' EXIT
cd "$temp_dir"

# Rebuild the container with composefs fsverity info
chcon \
    --reference="$HOME/.local/share/containers/storage/overlay" \
    "$HOME/.local/share/containers/storage"

podman build \
    --build-arg="IMAGE_ID=$(\
        podman image inspect --format='{{.Id}}' \
            "maxchernoff.ca/fedora-bootc-base:latest" \
    )" \
    --volume="$(\
        podman system info --format '{{.Store.GraphRoot}}' \
    ):/run/host-container-storage:ro" \
    --cap-add="SYS_ADMIN" \
    --disable-compression="false" \
    --inherit-annotations="true" \
    --inherit-labels \
    --label="containers.bootc=sealed" \
    --network="none" \
    --no-cache \
    --pull="always" \
    --tag="maxchernoff.ca/fedora-bootc:latest" \
    --volume="$HOME/.cache/podman-dnf/:/var/cache/libdnf5/:rw" \
    --volume="$temp_dir:/var/lib/containers:U,z" \
    "$script_dir"

# Push the container
skopeo copy \
    --all \
    --dest-compress-format="zstd:chunked" \
    --dest-compress-level="15" \
    --dest-precompute-digests \
    --dest-tls-verify="false" \
    --format="oci" \
    --image-parallel-copies="8" \
    --preserve-digests \
    --sign-by-sigstore="/var/home/repo/credentials/builder/sigstore-builder.yaml" \
    --sign-identity="maxchernoff.ca/fedora-bootc:latest" \
    "containers-storage:maxchernoff.ca/fedora-bootc:latest" \
    "docker://localhost:!!registry.port!!/fedora-bootc:latest"
