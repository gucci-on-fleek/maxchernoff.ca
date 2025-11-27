# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
FROM localhost:!!registry.port!!/fedora-iot-base:latest as base

FROM base as kernel
ARG COMPOSEFS_ID
RUN <<EOF
    set -euxo pipefail

    # Install required packages
    dnf5 install \
        --assumeyes \
        --nodocs \
        --setopt=install_weak_deps=false \
        --setopt=keepcache=true \
        --use-host-config \
        systemd-boot-unsigned \
        systemd-ukify

    # Determine kernel version
    kver="$(cd /usr/lib/modules && echo *)"
    kernel_path="/usr/lib/modules/$kver"

    # Create cmdline file
    echo "composefs=${COMPOSEFS_ID} root=gpt-auto rootflags=compress=zstd:3,noatime lockdown=confidentiality rw testkey=$(TZ='America/Edmonton' date --iso-8601=seconds)" > /etc/cmdline

    # Reenable dracut
    mv /usr/libexec/dracut /usr/bin/dracut

    # Dracut configuration
    mkdir -p /etc/dracut.conf.d/
    echo "export DRACUT_NO_XATTR=1" > /etc/dracut.conf.d/no-xattr.conf
    dracut --verbose --force --reproducible --zstd --no-hostonly --kver="$kver" "$kernel_path/initramfs.img"

    # Get the UKI name
    uki_name="$(\
        source /usr/lib/os-release && \
        echo "${OSTREE_VERSION//./-}" \
    )"

    # Build systemd-boot EFI executable
    mkdir -p /boot/EFI/Linux/
    ukify build \
        --linux="$kernel_path/vmlinuz" \
        --initrd="$kernel_path/initramfs.img" \
        --cmdline="@/etc/cmdline" \
        --os-release="@/usr/lib/os-release" \
        --uname="$kver" \
        --measure \
        --output="/boot/EFI/Linux/$uki_name.efi"

    mkdir -p /boot/EFI/BOOT/ /boot/EFI/systemd/
    cp /usr/lib/systemd/boot/efi/systemd-bootx64.efi /boot/EFI/BOOT/BOOTX64.EFI
    cp /usr/lib/systemd/boot/efi/systemd-bootx64.efi /boot/EFI/systemd/systemd-bootx64.efi

    bootc container lint || true
EOF

FROM base AS bootable
COPY --from=kernel /boot /boot
