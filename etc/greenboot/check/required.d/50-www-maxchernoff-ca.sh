#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff
set -euo pipefail

# Make sure that the website is up and running
curl --silent --show-error --fail 'https://www.maxchernoff.ca/status' \
| jq --exit-status '(now - 5) <= .unix_time and .unix_time <= (now + 5)'

exit $?

