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

# Install the builder packages
for _ in $(seq 3); do
    dnf5 install \
        --assumeyes \
        --nodocs \
        --setopt=install_weak_deps=false \
        --setopt=keepcache=true \
        gzip \
        tar \
    && break \
    || sleep $((30 + RANDOM % 90))
done

# Install the base packages
dnf5 install \
    --assumeyes \
    --installroot=$root \
    --nodocs \
    --setopt=install_weak_deps=false \
    --setopt=keepcache=true \
    --use-host-config \
    coreutils-single \
    curl \
    diffutils \
    generic-release \
    glibc-minimal-langpack \
    mailcap \
    python3-subversion \
    python3-waitress

# Install ViewVC
mkdir -p ~/viewvc
cd ~/viewvc

curl -L https://github.com/viewvc/viewvc/archive/refs/heads/master.tar.gz | tar xz

python_version="$(basename "$(realpath $root/usr/bin/python3)")"
mkdir -p $root/usr/local/lib/$python_version/site-packages/
cp -r ./viewvc-*/lib/* $root/usr/local/lib/$python_version/site-packages/

mkdir -p $root/usr/local/share/viewvc/
cp -r ./viewvc-*/templates/default/* $root/usr/local/share/viewvc/

mkdir -p $root/etc/viewvc/
for name in viewvc mimetypes; do
    cp ./viewvc-*/conf/$name.conf.dist $root/etc/viewvc/$name.conf
done

# Patch ViewVC
cp /root/cgi.py $root/usr/local/lib/$python_version/site-packages/cgi.py
sed -i '/self.closed = 0/d' $root/usr/local/lib/$python_version/site-packages/sapi.py

# Create the ViewVC user
useradd --root=$root viewvc

# Links
mkdir -p \
    $root/etc/caddy \
    $root/etc/viewvc \
    $root/home/viewvc/.config/ \
    $root/home/viewvc/.local/share/

ln -sf /srv/Caddyfile $root/etc/caddy/Caddyfile
ln -sfT /srv/data/caddy-config $root/home/viewvc/.config/caddy
ln -sfT /srv/data/caddy-data $root/home/viewvc/.local/share/caddy
ln -sf /srv/mimetypes.conf $root/etc/viewvc/mimetypes.conf
ln -sf /srv/viewvc.conf $root/etc/viewvc/viewvc.conf

# GeoIP folder
mkdir -p $root/usr/local/share/GeoIP/
chmod -R a+rX $root/usr/local/share/GeoIP/
curl -L 'https://cdn.jsdelivr.net/npm/@ip-location-db/asn-mmdb/asn.mmdb' -o $root/usr/local/share/GeoIP/asn.mmdb
chmod a=r,u+w $root/usr/local/share/GeoIP/asn.mmdb

# Unlink the cache from the host
rm $root/var/cache/libdnf5

# Remove the caches
dnf5 clean all --installroot=$root
rm -rf $root/var/{cache,log}/*
