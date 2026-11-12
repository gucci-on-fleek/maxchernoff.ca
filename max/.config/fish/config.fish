# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

# Load the global configuration
if test -f /var/lib/repo/usr/share/fish/vendor_conf.d/99-local-config.fish
    source /var/lib/repo/usr/share/fish/vendor_conf.d/99-local-config.fish
end

# Add the required PATH entries
fish_add_path ~tex/texlive/bin/x86_64-linux/

function ok
    truncate --size=0 /var/lib/triggers/get-status.output
    echo "$(date)" > /var/lib/triggers/get-status.trigger
    set --local count 0
    while not grep --quiet "Memory Usage" /var/lib/triggers/get-status.output
        sleep 0.1
        set --local count (math $count + 1 % 5)
        if test $count = 0
            echo "$(date)" > /var/lib/triggers/get-status.trigger
        end
    end
    cat /var/lib/triggers/get-status.output
end

function refresh
    echo "$(date)" > /var/lib/triggers/install-repo-maxchernoff.ca.trigger
end

function refresh-credentials
    echo "$(date)" > /var/lib/triggers/install-repo-credentials.trigger
end

function journalctl
    command journalctl --exclude-identifier='sshd-session' --exclude-identifier='dmarc-metrics' $argv
end
