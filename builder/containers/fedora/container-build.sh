#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff
set -euo pipefail

# Create a mount point for the container
cache=/var/cache/rpm-ostree/
root=$cache/root/
rm -rf $root || true
mkdir -p $root
cd $root

# Install rpm-ostree in the build container
dnf5 install \
    --assumeyes \
    --nodocs \
    --setopt=install_weak_deps=false \
    --setopt=keepcache=true \
    --use-host-config \
    rpm-ostree \
    selinux-policy-targeted \
    skopeo

# Initialize the ostree repository
repo=/root/repo/
mkdir -p $repo
ostree --repo=$repo init --mode=bare-user

# Install the artifact container packages
ln -s /etc/yum.repos.d/fedora*.repo /root/  # Use the host's repositories
rpm-ostree compose install \
    --unified-core \
    --cachedir=$cache \
    --repo=$repo \
    /root/fedora.yaml \
    $root

# Postprocess the container
rpm-ostree compose postprocess \
    --unified-core \
    $root/rootfs \
    /root/fedora.yaml

# Commit the container
rpm-ostree compose commit \
    --unified-core \
    --repo=$repo \
    /root/fedora.yaml \
    $root/rootfs

# Get the previous container manifest
skopeo inspect --tls-verify=false docker://localhost:23719/fedora:latest > /root/manifest.json || true

# Export the image
if [ -s /root/manifest.json ]; then
    rpm-ostree compose container-encapsulate \
        --repo=$repo \
        --previous-build-manifest=/root/manifest.json \
        maxchernoff.ca/fedora/latest \
        oci-archive:/var/image-out/image.tar
else
    rpm-ostree compose container-encapsulate \
        --repo=$repo \
        maxchernoff.ca/fedora/latest \
        oci-archive:/var/image-out/image.tar
fi
