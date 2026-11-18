#!/usr/bin/env bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff
set -euo pipefail
umask a=rx,ug+w

# Make sure that ConTeXt isn't already installed
if [ -d "/var/lib/tex/context" ]; then
    echo "ConTeXt is already installed."
    exit 1
fi

# Download and unpack the installer
mkdir -p ~/context-installer
cd ~/context-installer
curl -O 'https://lmtx.pragma-ade.com/install-lmtx/context-linux-64.zip'
busybox unzip context-linux-64.zip
chmod a+x install.sh

# Run the installer
./install.sh
ln -s ~/context-installer/tex ~/context
