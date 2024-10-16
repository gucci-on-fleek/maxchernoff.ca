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
    echo "$(date)" > ~repo/triggers/get-status.trigger
    sleep 0.50
    cat ~repo/triggers/get-status.output
end

function refresh
    echo "$(date)" > ~repo/triggers/install-repo.trigger
end

function reboot
    sudo systemctl reboot
end
