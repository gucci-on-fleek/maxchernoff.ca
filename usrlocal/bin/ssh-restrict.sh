#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
set -euo pipefail

command=(systemd-run --user --quiet --wait --collect --pipe
    -p BindReadOnlyPaths='/bin/ /etc/ /lib/ /lib64/ /usr/'
    -p CapabilityBoundingSet=''
    -p NoNewPrivileges='true'
    -p PrivateDevices='true'
    -p PrivateNetwork='true'
    -p PrivateTmp='true'
    -p PrivateUsers='true'
    -p TemporaryFileSystem='/'
)

command+=(-p BindPaths="$HOME")

if [ -z "${SSH_ORIGINAL_COMMAND:-}" ]; then
    command+=(--pty -- "$SHELL" --login)
else
    command+=(-- $SSH_ORIGINAL_COMMAND)
fi

exec "${command[@]}"
