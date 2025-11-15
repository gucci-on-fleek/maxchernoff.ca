#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2025 Max Chernoff
set -euxo pipefail

# Victoria Logs doesn't provide `latest` or semver `v1` tags, so to keep up with
# the latest version, we'll manually parse the list of versions and push the
# latest one to my own registry.

# Get the image name from the command line
image_name="$1"

# Get the base name of the image, without the registry
base_name="$(echo "$image_name" | awk -F/ '{print $NF}')"

# Get the latest version from the upstream registry
latest_version="v$(\
    skopeo list-tags "docker://$image_name" | \
    jq --raw-output '.Tags[]' | \
    sed -e 's/-victorialogs//' -e 's/^v//' | \
    grep --invert-match --perl-regexp '(?[[-]+[:alpha:]-[v]])' | \
    sort --field-separator='.' --numeric-sort --reverse --key=1,1 --key=2,2 --key=3,3 | \
    head --lines=1 \
)"

# Copy the latest version to my own registry
for _ in $(seq 3); do # This is flaky, so try up to 3 times
    skopeo copy \
        --all \
        --dest-tls-verify=false \
        --dest-compress-format=zstd:chunked \
        --dest-compress-level=15 \
        --dest-precompute-digests \
        --sign-by-sigstore=/var/home/repo/credentials/builder/sigstore-builder.yaml \
        --sign-identity="maxchernoff.ca/$base_name:latest" \
        "docker://$image_name:$latest_version" \
        "docker://localhost:!!registry.port!!/$base_name:latest" \
    && break \
    || sleep 5
done
