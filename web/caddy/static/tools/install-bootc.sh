#!/usr/bin/env bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff
set -euxo pipefail


##############################
### Command-line Arguments ###
##############################

# Make sure that we have the correct "getopt"
getopt --test && true
if [[ $? -ne 4 ]]; then
	echo "\"getopt\" does not support long options."
	exit 1
fi

# Print an error message and exit
fail_with_help() {
	if [[ ! -z "${1:-}" ]]; then
		echo "Error: $1" >&2
	fi
	echo "Usage: $(basename "$0") [--help] --disk=<disk>" 2>&1
	exit 2
}

# Parse the arguments
if [[ $# -eq 0 ]]; then
	fail_with_help "Missing required arguments."
fi

eval set -- "$(getopt \
	--name="$(basename "$0")" \
	--shell="bash" \
	--options="" \
	--longoptions="help,disk:" \
	-- "$@"
)"

# Process the arguments
while true; do
	case "$1" in
		("--help")
			fail_with_help
		;;
		("--disk")
			disk="$2"
			shift 2
		;;
		(--)
			shift
			break
		;;
		(*)
			fail_with_help "Invalid option: $1"
		;;
	esac
done


##################
### Validation ###
##################

# Make sure that we're running from a Live CD
if ! mount | grep -q "on / type overlay"; then
	fail_with_help "This script must be run from a Live CD."
fi

# Make sure that we're running as root
if [[ "$(id -u)" -ne 0 ]]; then
	fail_with_help "This script must be run as root."
fi

# Make sure that the disk exists
if [[ ! -b "$disk" ]]; then
	fail_with_help "The specified disk does not exist: $disk"
fi

# Make sure that Podman is installed
if ! command -v podman &> /dev/null; then
	fail_with_help "Podman is not installed."
fi

# Make sure that sfdisk is installed
if ! command -v sfdisk &> /dev/null; then
	fail_with_help "sfdisk is not installed."
fi

# Make sure that Clevis is installed
if ! command -v clevis &> /dev/null; then
	fail_with_help "Clevis is not installed."
fi

# Make sure that systemd-cryptenroll is installed
if ! command -v systemd-cryptenroll &> /dev/null; then
	fail_with_help "systemd-cryptenroll is not installed."
fi

# Make sure that dbus-broker is running
if ! systemctl is-active --quiet dbus-broker; then
	fail_with_help "dbus-broker is not running."
fi


####################
### Partitioning ###
####################

# Make sure that the disk is not mounted
if mount | grep -q "$disk"; then
	fail_with_help "The specified disk is mounted: $disk"
fi

# Make sure that the disk is unpartitioned, to prevent accidental data loss
if sfdisk --verify "$disk" 2>&1 | grep -q 'No errors detected'; then
	fail_with_help "The specified disk is partitioned: $disk"
fi

# Partition the disk
cat <<-EOF | sfdisk "$disk"
	label: gpt

	name="efi", type="EFI System", size=1GiB
	name="swap", type="Linux swap", size=$(
		free --giga | awk '/Mem/ { print $2 "GiB" }'
	)
	name="root", type="Linux root (x86-64)", size=+
EOF


#######################
### Root Filesystem ###
#######################

# Format the root partition with LUKS
head --bytes=32 /dev/urandom > /tmp/luks-keyfile

cryptsetup luksFormat \
	--batch-mode \
	--cipher="aes-xts-plain64" \
	--iter-time="500" \
	--key-file="/tmp/luks-keyfile" \
	--key-size="256" \
	--label="root" \
	--pbkdf-memory="$((2 * 1024**2))" \
	--pbkdf="argon2id" \
	--sector-size="4096" \
	--type="luks2" \
	"${disk}3"

# Add a Clevis Tang binding to the LUKS partition
clevis luks bind \
	-y \
	-d "${disk}3" \
	-k "/tmp/luks-keyfile" \
	tang '{"url": "http://tang.maxchernoff.ca"}'

# Mount the LUKS partition
cryptsetup open \
	--key-file="/tmp/luks-keyfile" \
	--allow-discards \
	--persistent \
	"${disk}3" \
	"root"

# Create a Btrfs filesystem on the LUKS partition
mkfs.btrfs \
	--checksum="blake2" \
	--label="root" \
	--features="block-group-tree" \
	/dev/mapper/root

# Mount the root filesystem
mkdir --parents /mnt/root
mount \
	--onlyonce \
	--source="/dev/mapper/root" \
	--target="/mnt/root" \
	--options="defaults,noatime,compress=zstd:3"


####################
### Installation ###
####################

# We need some scratch space to pull the container, so we'll use the new swap
# partition for this temporarily.
mkfs.ext4 -F -L "scratch" "${disk}2"

# Mount the scratch partition
rm --recursive --force /var/lib/containers
mkdir --parents /var/lib/containers
mount "${disk}2" /var/lib/containers

# Create the EFI partition
mkfs.fat -F32 -n "EFI" "${disk}1"

# Mount the EFI partition
mkdir --parents /mnt/boot
mount \
	--onlyonce \
	--source="${disk}1" \
	--target="/mnt/boot"

# Install the container to the disk
podman run \
	--pull="newer" \
	--rm \
	--privileged \
	--pid="host" \
	--security-opt="label=disable" \
	--volume="/var/lib/containers/:/var/lib/containers/" \
	--volume="/mnt/root:/target/root" \
	--volume="/mnt/boot:/target/root/boot" \
	--volume="/dev:/dev" \
	"docker://maxchernoff.ca/fedora-bootc:latest" \
		 bootc install to-filesystem \
		 	--generic-image \
			--bootloader="systemd" \
			--composefs-backend \
			--enforce-container-sigpolicy \
			--experimental-unified-storage \
			--root-mount-spec="" \
			--boot-mount-spec="UUID=$(\
				lsblk --noheadings --output=UUID ${disk}1\
			)" \
			"/target/root"


####################
### Finalization ###
####################

# Unmount the root filesystem
umount --all-targets /mnt/root
cryptsetup close "root"

# Unmount the EFI partition
umount --all-targets /mnt/boot

# Unmount the scratch partition
umount --all-targets /var/lib/containers

# Convert the scratch partition to swap
blkdiscard --force "${disk}2"

# Add a recovery key to the LUKS partition and remove the password
systemd-cryptenroll \
	--recovery-key \
	--wipe-slot="password" \
	--unlock-key-file="/tmp/luks-keyfile" \
	"${disk}3"
rm --force /tmp/luks-keyfile


##################
### Networking ###
##################

# Mount the boot partition
mkdir --parents /mnt/boot
mount \
	--onlyonce \
	--source="${disk}1" \
	--target="/mnt/boot"

# Create the systemd-networkd configuration
mkdir --parents /mnt/boot/loader/credentials/
cat <<-EOF | systemd-creds encrypt --with-key="null" --name="network.network.85-initramfs" - "/mnt/boot/loader/credentials/network.network.85-initramfs.cred"
	[Match]
	Kind=!*
	Type=ether

	[Network]
	DHCP=no
	Address=$(
		ip --brief addr show scope global | awk '{ print $3 }' | head -n 1
	)
	Gateway=$(
		ip --brief route show default | awk '{ print $3 }' | head -n 1
	)
EOF

# Unmount the boot partition
umount --all-targets /mnt/boot

# Done
echo "Success!"
