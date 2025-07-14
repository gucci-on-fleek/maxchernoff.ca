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
    command journalctl --exclude-identifier='sshd-session' $argv
end

function ls
    command ls --classify --color=auto --human-readable --almost-all $argv
    if test $status = 2
        sudo ls --classify --color=auto --human-readable --almost-all $argv
    end
end

function pps
    ps --no-headers -eo pid,user:12,context:40,cmd | \
    tr --squeeze-repeats ' ' | \
    sed -E \
        -e 's/ /\x00/g5' \
        -e 's/ /\t/g' \
        -e 's/\x00/ /g' \
        -e 's/^\t//' \
        -e 's/:s0[^\t]*//' \
        -e 's/^([^\t]*)(\t[^\t]{,12})[^\t]*(\t[^\t]{,40})[^\t]*(.*)/\1\2\3\4/' \
    | \
    column --table \
        --separator="$(printf "\t")" \
        --output-width=$COLUMNS \
        --table-column=name=PID,right \
        --table-column=name=User,width=12,trunc \
        --table-column=name='SELinux Context',width=40,trunc \
        --table-column=name=Command,wrap
end
