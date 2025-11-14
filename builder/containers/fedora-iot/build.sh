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

# Build the container
podman run \
    --cap-add=NET_ADMIN \
    --cap-add=SYS_ADMIN \
    --device=/dev/fuse \
    --network=pasta:-T,!!registry.port!! \
    --pull=always \
    --rm \
    --security-opt=label=nested \
    --security-opt=label=role:user_r \
    --security-opt=label=user:user_u \
    --userns=host \
    --volume="/etc/containers/:/etc/containers/:ro" \
    --volume="$HOME/.cache/rpm-ostree/:/var/cache/rpm-ostree:rw,z" \
    --volume="$script_dir:/root/source/:ro" \
    --volume="$temp_dir:/root/output/:rw,z" \
    "maxchernoff.ca/bootc-builder:latest" \
    rpm-ostree compose image \
        --initialize-mode=query \
        --format=registry \
        --cachedir="/var/cache/rpm-ostree" \
        --max-layers=200 \
        "/root/source/fedora-iot.yaml" \
        "localhost:!!registry.port!!/fedora-iot-base:latest" \

# Get the composefs command
composefs_cmd="bootc internals cfs --repo=$temp_dir/composefs-repo/"
mkdir -p "$temp_dir/composefs-repo/"

# Get the composefs info
image_id="$(\
    $composefs_cmd oci pull "docker://localhost:!!registry.port!!/fedora-iot-base:latest" \
    2>&1 | grep --only-matching --perl-regexp '(?<=^sha256 ).*$' \
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
    --dest-compress-format=zstd:chunked \
    --dest-compress-level=5 \
    --dest-precompute-digests \
    --dest-tls-verify=false \
    --image-parallel-copies=4 \
    --preserve-digests \
    --sign-by-sigstore=/var/home/repo/credentials/builder/sigstore-builder.yaml \
    --sign-identity=maxchernoff.ca/fedora-iot:latest \
    "containers-storage:maxchernoff.ca/fedora-iot:latest" \
    "docker://localhost:!!registry.port!!/fedora-iot:latest"
