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
base_image="localhost:!!registry.port!!/fedora-iot-base:latest"

podman run \
    --cap-add=NET_ADMIN \
    --cap-add=SYS_ADMIN \
    --device=/dev/fuse \
    --network=pasta:-T,!!registry.port!! \
    --pull=newer \
    --rm \
    --security-opt=label=nested \
    --security-opt=label=role:user_r \
    --security-opt=label=user:user_u \
    --userns=host \
    --volume="/etc/containers/:/etc/containers/:ro" \
    --volume="/usr/local/bin/composefs-setup-root:/usr/local/bin/composefs-setup-root:ro" \
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
        "$base_image"

# Weird hack
podman image rm "localhost/fedora-iot-tmp:latest" || true
podman build \
    --file="$script_dir/base.containerfile" \
    --inherit-annotations=true \
    --inherit-labels \
    --no-cache \
    --pull=always \
    --tag="localhost/fedora-iot-tmp:latest" \
    "$script_dir"

# Get the composefs info
mkdir -p "$temp_dir/composefs/tmp/"
composefs_id="$(\
    podman run \
        --network="none" \
        --privileged \
        --pull=never \
        --read-only \
        --rm \
        --userns=host \
        --volume="$(podman system info -f '{{.Store.GraphRoot}}'):/run/host-container-storage:ro" \
        --volume="$temp_dir/composefs/:/var:rw" \
        "localhost/fedora-iot-tmp:latest" \
        bootc container compute-composefs-digest
)"

# Rebuild the container with composefs fsverity info
podman build \
    --build-arg="COMPOSEFS_ID=$composefs_id" \
    --file="$script_dir/final.containerfile" \
    --inherit-annotations=true \
    --inherit-labels \
    --label="containers.bootc=sealed" \
    --no-cache \
    --tag="maxchernoff.ca/fedora-iot:latest" \
    --unsetlabel="ostree.bootable" \
    --unsetlabel="ostree.commit" \
    --unsetlabel="ostree.final-diffid" \
    --unsetlabel="ostree.linux" \
    --unsetlabel="rpmostree.inputhash" \
    --volume="$HOME/.cache/podman-dnf/:/var/cache/libdnf5/:rw" \
    "$script_dir"

# Push the container
skopeo copy \
    --all \
    --dest-compress-format="zstd" \
    --dest-compress-level=15 \
    --dest-precompute-digests \
    --dest-tls-verify=false \
    --image-parallel-copies=4 \
    --preserve-digests \
    --sign-by-sigstore="/var/home/repo/credentials/builder/sigstore-builder.yaml" \
    --sign-identity="maxchernoff.ca/fedora-iot:latest" \
    "containers-storage:maxchernoff.ca/fedora-iot:latest" \
    "docker://localhost:!!registry.port!!/fedora-iot:latest"
