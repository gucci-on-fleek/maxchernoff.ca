# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

# Fix Ctrl-L
bind \f 'clear && commandline -f repaint'

# Add the required PATH entries
fish_add_path ~tex/texlive/bin/x86_64-linux/

# Aliases
function ok
    sudo --validate
    web-uptime
    echo
    sudo web-status ~repo/maxchernoff.ca/unit-status.conf
end

function refresh
    sudo systemctl start install-repo.service
    ok
end

function reboot
    sudo systemctl reboot
end
