# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff
FROM localhost:!!registry.port!!/fedora-iot-base:latest as base

FROM base as kernel
ARG IMAGE_ID
RUN <<EOF
    set -euxo pipefail

    # Install required packages
    dnf5 install \
        --assumeyes \
        --nodocs \
        --setopt=install_weak_deps=false \
        --setopt=keepcache=true \
        --use-host-config \
        strip \
        systemd-boot-unsigned \
        systemd-ukify

    # Get the composefs ID
    {
        cat "/run/.containerenv"
        echo "imageid=$IMAGE_ID"
    } > /run/.containerenv

    # Add the composefs ID to the kernel command line
    echo "composefs=$(\
        bootc container compute-composefs-digest-from-storage \
    )" >> /etc/kernel/cmdline

    # UKI generation
    kernel-install add-all

    mkdir -p /boot/EFI/BOOT/ /boot/EFI/systemd/
    cp /usr/lib/systemd/boot/efi/systemd-bootx64.efi /boot/EFI/BOOT/BOOTX64.EFI
    cp /usr/lib/systemd/boot/efi/systemd-bootx64.efi /boot/EFI/systemd/systemd-bootx64.efi

    # Lint the bootc container
    rm -rf {/var/log,/run/dnf,/tmp,/var/lib}/{.,}* || true
    bootc container lint || true
EOF

FROM base AS bootable
COPY --from=kernel /boot /boot
