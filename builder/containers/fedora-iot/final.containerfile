# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff
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
		dracut-config-generic \
		strip \
		systemd-boot-unsigned \
		systemd-ukify

	# Create cmdline file
	mkdir -p /etc/kernel/
	echo "composefs=${COMPOSEFS_ID} root=gpt-auto rootflags=compress=zstd:3,noatime lockdown=confidentiality rw" > /etc/kernel/cmdline

	# Dracut configuration
	mkdir -p /etc/dracut.conf.d/
	cat <<-'EODRACUT' > /etc/dracut.conf.d/99-composefs.conf
		export DRACUT_NO_XATTR=1
		add_dracutmodules+=" bootc "
		filesystems+=" btrfs overlay vfat "
		hostonly="no"
		compress="zstd"
		do_strip="yes"
		aggressive_strip="yes"
		reproducible="yes"
	EODRACUT

	# UKI generation
	mkdir -p /usr/lib/kernel/install.conf.d/
	cat <<-'EOCONF' > /usr/lib/kernel/install.conf.d/37composefs.conf
		layout = uki
		uki_generator = ukify
	EOCONF
	kernel-install add-all

	mkdir -p /boot/EFI/BOOT/ /boot/EFI/systemd/
	cp /usr/lib/systemd/boot/efi/systemd-bootx64.efi /boot/EFI/BOOT/BOOTX64.EFI
	cp /usr/lib/systemd/boot/efi/systemd-bootx64.efi /boot/EFI/systemd/systemd-bootx64.efi

	# Lint the bootc container
	rm -rf {/var/log,/run/dnf,/tmp,/var/lib}/{.,}*
	bootc container lint || true
EOF

FROM base AS bootable
COPY --from=kernel /boot /boot
