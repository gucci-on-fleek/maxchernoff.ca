#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff

# This script is used to install Tang <https://github.com/latchset/tang> on a
# minimal Alpine Linux server installation.
set -euxo pipefail


############
### Swap ###
############

# Create the swap file
fallocate -l 256M /var/lib/swapfile
chmod a-rwx,u=rw /var/lib/swapfile
mkswap /var/lib/swapfile
echo '/var/lib/swapfile none swap defaults 0 0' >> /etc/fstab

# Configure zswap
cat > /etc/init.d/zswap <<-'EOF'
	#!/sbin/openrc-run

	depend() {
		need swap
		after swap
	}

	start() {
		mark_service_starting
		echo 3200 > /proc/sys/vm/min_free_kbytes
		echo  100 > /proc/sys/vm/swappiness
		echo  250 > /proc/sys/vm/watermark_scale_factor
		echo  lz4 > /sys/module/zswap/parameters/compressor
		echo    1 > /sys/module/zswap/parameters/enabled
		echo   33 > /sys/module/zswap/parameters/max_pool_percent
		echo    1 > /sys/module/zswap/parameters/shrinker_enabled
		mark_service_started
	}

	stop() {
		mark_service_stopped
	}
EOF
chmod a+x /etc/init.d/zswap

# Enable the swap
rc-update add zswap
rc-update add swap
rc-service --verbose swap restart


######################
### Kernel Modules ###
######################

# The list of modules to blacklist
modules=(
	# Graphics
	drm
	drm_client_lib
	drm_kms_helper
	drm_panel_orientation_quirks
	drm_shmem_helper
	drm_sysfb_helper
	simpledrm
	virtio_gpu

	# USB
	hid
	hid_generic
	usb_common
	usb_storage
	usbcore
	usbhid
	xhci_hcd
	xhci_pci

	# Networking
	ena
	gve
	mana

	# I2C
	i2c_core
	i2c_piix4
	i2c_smbus

	# Miscellaneous
	af_packet
	cdrom
	loop
	sr_mod
	virtio_balloon
)

# Blacklist the modules
truncate -s 0 /etc/modprobe.d/minimize.conf
for module in "${modules[@]}"; do
	echo "blacklist $module" >> /etc/modprobe.d/minimize.conf
	echo "install $module /bin/true" >> /etc/modprobe.d/minimize.conf
done

# Unload the modules, since some are loaded by the initramfs
cat > /etc/init.d/remove-modules <<-EOF
	#!/sbin/openrc-run

	depend() {
		after modloop
		after modules
		after hwdrivers
	}

	start() {
		mark_service_starting
		for _ in "\$(seq 1 10)"; do
			rmmod ${modules[@]} >/dev/null 2>&1 || true
		done
		mark_service_started
	}

	stop() {
		mark_service_stopped
	}
EOF

chmod a+x /etc/init.d/remove-modules
rc-update add remove-modules
rc-service --verbose remove-modules start


###########
### SSH ###
###########

# Change the SSH configuration
cat > /etc/ssh/sshd_config.d/99-local.conf <<-'EOF'
	# Only allow public key authentication
	PubkeyAuthentication yes
	AuthenticationMethods publickey
	PasswordAuthentication no
	KbdInteractiveAuthentication no

	# Block failed login attempts
	MaxAuthTries 1
	MaxStartups 60:30:100
	LoginGraceTime 10
	PerSourceNetBlockSize 32:64
	PerSourcePenalties authfail:1m noauth:1m grace-exceeded:1m crash:5m

	# Only allow a single algorithm for each category to reduce attack surface.
	# I've chosen the first (aka most preferred) algorithm in the list of OpenSSH's
	# defaults as of 2026-07-24.
	Ciphers chacha20-poly1305@openssh.com
	FingerprintHash sha256
	HostKeyAlgorithms ssh-ed25519
	KexAlgorithms mlkem768x25519-sha256
	MACs umac-64-etm@openssh.com
	PubkeyAcceptedAlgorithms ssh-ed25519
EOF
ln -sf /dev/null /etc/ssh/sshd_config.d/50-cloud-init.conf


#####################
### Miscellaneous ###
#####################

# Reduce the bootloader timeout
sed -i '/^TIMEOUT/c\TIMEOUT 1' /boot/extlinux.conf

# Remove cloud-init after initialization has finished
apk del cloud-init

# Ensure that /usr is merged
if test ! -L /bin; then
	apk add --update-cache merge-usr
	merge-usr --dryrun
	apk del merge-usr
fi

# Start services in parallel
sed -i '/rc_parallel/c\rc_parallel="YES"' /etc/rc.conf


#########################
### Automatic Updates ###
#########################

# Always use the latest release
cat > /etc/apk/repositories <<-'EOF'
	https://dl-cdn.alpinelinux.org/alpine/latest-stable/main
	https://dl-cdn.alpinelinux.org/alpine/latest-stable/community
	@testing https://dl-cdn.alpinelinux.org/alpine/edge/testing
EOF

# Create the auto-update script
cat > /etc/periodic/daily/auto-update <<-'EOF'
	#!/bin/sh
	apk upgrade \
		--preupgrade-depends="apk-tools" \
		--available \
		--prune \
		--update-cache \
		--interactive="no" \
		--logfile="yes"

	reboot
EOF
chmod a+x /etc/periodic/daily/auto-update

# Enable cron
rc-update add crond
rc-service --verbose crond start


############
### Tang ###
############

# Install Tang
apk add --update-cache tang@testing tang-openrc@testing

# Configure Tang
cat > /etc/conf.d/tang <<-'EOF'
	socat_address="tcp6-listen:80,bind=::,fork"
EOF

# Allow Tang to bind to port 80
cat > /etc/sysctl.d/99-tang.conf <<-'EOF'
	net.ipv4.ip_unprivileged_port_start=80
EOF

# Enable Tang
rc-update add tang


####################
### Finalization ###
####################

# Update all packages and reboot
/etc/periodic/daily/auto-update
