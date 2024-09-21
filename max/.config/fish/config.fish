# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

# Fix Ctrl-L
bind \f 'clear && commandline -f repaint'

# Add the required PATH entries
fish_add_path ~/maxchernoff.ca/scripts/
fish_add_path ~tex/texlive/bin/x86_64-linux/

# Refresh the server contents
function refresh
    sudo --validate; or return $status

    # Get the new files
    web-pull; or return $status

    # Install the files
    sudo (type -p web-install); or return $status

    # Reload all the services
    for user in max tex web woodpecker
        sudo systemctl --user --machine "$user@" daemon-reload
    end
    sudo systemctl --system daemon-reload

    # Restart the server
    sudo systemctl --user --machine web@ restart caddy.service

    # Check the status
    sleep 1
    sudo (type -p web-status)
end
