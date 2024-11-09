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

# Aliases
function ok
    argparse loop -- $argv
    if set --query _flag_loop
        set --local time 0
        while sleep $time
            _ok
            set time 1
        end
    else
        _ok
    end
end

function _ok
    truncate --size=0 ~repo/triggers/get-status.output
    echo "$(date)" > ~repo/triggers/get-status.trigger
    while not grep --quiet "service" ~repo/triggers/get-status.output
        sleep 0.1
    end
    cat ~repo/triggers/get-status.output
end

function refresh
    echo "$(date)" > ~repo/triggers/install-repo.trigger
end

function reboot
    sudo systemctl reboot
end
