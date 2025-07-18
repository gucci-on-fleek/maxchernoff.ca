#!/bin/bash
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff
set -euo pipefail

# Generate the TeX caches
tl=/opt/texlive/bin/x86_64-linux
ctx=/opt/context/texmf-linux-64/bin

{
    cd "$(mktemp --directory)"
    $tl/luaotfload-tool --update || exit 1
    $tl/lualatex /root/make-font-cache/latex-cache.tex || exit 1
    $tl/lualatex /root/make-font-cache/latex-cache.tex || exit 1
} &
{
    cd "$(mktemp --directory)"
    $tl/context --make > /dev/null || exit 1
    $tl/mtxrun --script fonts --reload > /dev/null || exit 1
    $tl/context /root/make-font-cache/context-cache.tex || exit 1
} &
{
    cd "$(mktemp --directory)"
    $tl/context --luatex --make > /dev/null || exit 1
    $tl/mtxrun --luatex --script fonts --reload > /dev/null || exit 1
    $tl/context --luatex /root/make-font-cache/context-cache.tex || exit 1
} &
{
    cd "$(mktemp --directory)"
    $ctx/context --make > /dev/null || exit 1
    $ctx/mtxrun --script fonts --reload > /dev/null || exit 1
    $ctx/context /root/make-font-cache/context-cache.tex || exit 1
} &
{
    cd "$(mktemp --directory)"
    $ctx/context --luatex --make > /dev/null || exit 1
    $ctx/mtxrun --luatex --script fonts --reload > /dev/null || exit 1
    $ctx/context --luatex /root/make-font-cache/context-cache.tex || exit 1
} &

wait

# Remove the temporary files
shopt -s extglob
rm -rf /root/make-font-cache/!(*.tex)
