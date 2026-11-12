#!/usr/bin/env bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2026 Max Chernoff
set -euo pipefail
umask a=rx,og+w

# Make sure that TL isn't already installed
if [ -d "/var/lib/tex/texlive" ]; then
    echo "TeX Live is already installed."
    exit 1
fi

# Initialize the temporary directory
temp_dir="$(mktemp --directory --tmpdir=/var/tmp/)"
trap 'rm -rf "$temp_dir"' EXIT
cd "$temp_dir"

# Set the path
export PATH="/var/lib/tex/texlive/bin/x86_64-linux:/usr/local/bin:/usr/bin"

# Download the installer
cd "$temp_dir"
curl -O \
    'https://ftp.math.utah.edu/pub/ctan/tex-archive/systems/texlive/tlnet/install-tl-unx.tar.gz'
tar xf install-tl-unx.tar.gz

# Install TeX Live
# shellcheck disable=SC2211
./install-tl-*/install-tl \
    --repository='https://ftp.math.utah.edu/pub/ctan/tex-archive/systems/texlive/tlnet' \
    --texdir='/var/home/tex/texlive' \
    --scheme='full' \
    --paper='letter' \
    # (end of arguments)

# Install the TeX Live gpg keys
curl -fsSL https://tug.org/texlive/files/texlive.asc | tlmgr key add -
curl -fsSL https://www.preining.info/rsa.asc | tlmgr key add -

# Install the extra TeX Live repositories
tlmgr repository add \
    https://tug.org/texlive/tlcritical/ \
    tlcritical

tlmgr repository add \
    https://ctan.math.utah.edu/ctan/tex-archive/systems/texlive/tlcontrib \
    tlcontrib

tlmgr pinning add tlcontrib "*"
tlmgr install collection-contrib
