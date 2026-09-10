# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

# Load the global configuration
if test -f ~repo/maxchernoff.ca/usr/share/fish/vendor_conf.d/99-local-config.fish
    source ~repo/maxchernoff.ca/usr/share/fish/vendor_conf.d/99-local-config.fish
end

# Add the required PATH entries
fish_add_path ~tex/texlive/bin/x86_64-linux/

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

function refresh
    echo "$(date)" > ~repo/triggers/install-repo-maxchernoff.ca.trigger
end

function refresh-credentials
    echo "$(date)" > ~repo/triggers/install-repo-credentials.trigger
end

function journalctl
    command journalctl --exclude-identifier='sshd-session' --exclude-identifier='dmarc-metrics' $argv
end
