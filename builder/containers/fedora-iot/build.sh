#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
set -euxo pipefail

# Get the script directory
script_dir="$(dirname "$(realpath "$0")")"

# Initialize the build directory
temp_dir="$(mktemp --directory --tmpdir=/var/tmp/)"
trap 'rm -rf "$temp_dir"' EXIT
cd "$temp_dir"

# Download the previous image
skopeo copy --remove-signatures \
    docker://localhost:!!registry.port!!/fedora-iot:latest \
    "oci-archive:$temp_dir/fedora-iot.ociarchive"

# Build the container
rpm-ostree compose image \
    --initialize-mode=query \
    --format=ociarchive \
    --cachedir="$HOME/.cache/rpm-ostree/" \
    --max-layers=200 \
    "$script_dir/fedora-iot.yaml" \
    "$temp_dir/fedora-iot.ociarchive"

# Get the composefs command
composefs_cmd="bootc internals cfs --repo=$temp_dir/composefs-repo/"
mkdir -p "$temp_dir/composefs-repo/"

# Get the composefs info
image_id="$(\
    $composefs_cmd oci pull oci-archive:./fedora-iot.ociarchive \
    2>&1 | grep --only-matching --perl-regexp '(?<=^sha256 ).*$'\
)"

fsverity_id="$($composefs_cmd oci compute-id "$image_id")"

# Rebuild the container with composefs fsverity info
podman build \
    --no-cache \
    --volume="$HOME/.cache/podman-dnf/:/var/cache/libdnf5/:rw" \
    --build-arg="COMPOSEFS_FSVERITY=$fsverity_id" \
    --label="containers.composefs.fsverity=$fsverity_id" \
    --file="$script_dir/Containerfile" \
    --tag=maxchernoff.ca/fedora-iot:latest \
    "$script_dir"

# Push the container
skopeo copy \
    --all \
    --dest-tls-verify=false \
    --dest-compress-format=zstd:chunked \
    --dest-compress-level=5 \
    --dest-precompute-digests \
    --sign-by-sigstore=/var/home/repo/credentials/builder/sigstore-builder.yaml \
    --sign-identity=maxchernoff.ca/fedora-iot:latest \
    "containers-storage:maxchernoff.ca/fedora-iot:latest" \
    "docker://localhost:!!registry.port!!/fedora-iot:latest"
