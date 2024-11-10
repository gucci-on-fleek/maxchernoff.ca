#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff
set -euo pipefail

# Create a mount point for the container
root=/mnt/build/
repo=/root/repo/
mkdir -p $root
cd $root

# Save the caches between runs
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
    fedora-iot-config \
    glibc-minimal-langpack \
    rpm-ostree

# Unlink the cache
rm $root/var/cache/libdnf5

# Move the RPM databases
ln -sf /usr/lib/sysimage/rpm $root/usr/share/rpm
rm $root/usr/share/rpm
mv -T $root/usr/lib/sysimage/rpm $root/usr/share/rpm

# Hide bubblewrap
ln -sf /usr/bin/true /usr/bin/bwrap

# Initialize the repository
ostree --repo=$repo init --mode=bare-user

# Clean up the repository
ostree --repo=$repo prune --refs-only --depth=0

# Create the base commit
printf 'container: true\nrepos:\n  - ignored\n' > /root/treefile.yaml
rpm-ostree compose commit --repo=$repo --write-commitid-to=/root/commitid --unified-core /root/treefile.yaml $root

# Export the image
rpm-ostree compose container-encapsulate --repo=$repo "$(cat /root/commitid)" oci-archive:/var/out/image.tar
