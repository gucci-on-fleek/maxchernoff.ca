# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

# Fix Ctrl-L
bind \f 'clear && commandline -f repaint'

# Add the required PATH entries
fish_add_path ~tex/texlive/bin/x86_64-linux/

# Theme
fish_config theme choose max

# Colours
set --global fish_color_user --bold yellow

if set --query TOOLBOX_PATH
    set --global fish_color_user --reverse --bold --dim yellow
end

function ok
    truncate --size=0 ~repo/triggers/get-status.output
    echo "$(date)" > ~repo/triggers/get-status.trigger
    set --local count 0
    while not grep --quiet "Memory Usage" ~repo/triggers/get-status.output
        sleep 0.1
        set --local count (math $count + 1 % 5)
        if test $count = 0
            echo "$(date)" > ~repo/triggers/get-status.trigger
        end
    end
    cat ~repo/triggers/get-status.output
end

function container
    # podman run --name=fedora -it --network=host --volume=/var/home/max:/home/max --security-opt=label=disable fedora:latest
    podman start fedora
    podman exec -lit /usr/bin/fish
end

function refresh
    echo "$(date)" > ~repo/triggers/install-repo-maxchernoff.ca.trigger
end

function refresh-credentials
    echo "$(date)" > ~repo/triggers/install-repo-credentials.trigger
end

function reboot
    sudo systemctl reboot
end

function journalctl
    command journalctl --exclude-identifier='sshd-session' --grep='^(?!{"t":{)((?!system_u:system_r:sshd_t|container health_status).)+$' $argv
end
