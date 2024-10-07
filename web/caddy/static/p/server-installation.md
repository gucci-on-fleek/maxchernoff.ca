---
title: Server Installation
date: "2024-08-26"
description: >-
    A list of commands summarizing how I set up the server for this
    website.
---

{{- /* Source Code for maxchernoff.ca
     https://github.com/gucci-on-fleek/maxchernoff.ca
     SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
     SPDX-FileCopyrightText: 2024 Max Chernoff */ -}}

<style> .sidenote { padding-right: 2rem; } </style>

Contents
--------

<nav>

- [Preliminaries](#preliminaries)
- [Pre-installation](#pre-installation)
- [Installation](#installation)
- [Post-installation](#post-installation)
- [Installing TeX Live](#installing-tex-live)
- [Web Server](#web-server)
- [Snapshots](#snapshots)

</nav>

Preliminaries
-------------

- This guide is mainly intended for myself in case I ever need to
  rebuild the server, but I'm making it public in case it's useful to
  others.

- I've provided the exact IP addresses and usernames for my server; if
  you're following along, you'll want to replace these with the
  appropriate values for your own server.

- Commands that start with `$` are ran as the `max` user on the server,
  while commands that start with `%` are ran as some other user.

- This guide was tested with Fedora IoT 40.

Pre-installation
----------------

1. Download the [Fedora IoT `.iso`
   installer](https://github.com/gucci-on-fleek/maxchernoff.ca). <span
   class=sidenote>In the unlikely scenario that your hosting provider
   offers Fedora IoT images, you can skip until step 4.</span>

2. Upload and attach the `.iso` installer to the virtual machine.

3. Configure the <abbr>VM</abbr> for <abbr>UEFI</abbr> boot.

4. Set the following <abbr>DNS</abbr> records:

    <span class=sidenote>The `CAA` records make sure that only
    <cite>Let's Encrypt</cite> and <cite>Zero<abbr>SSL</abbr></cite> can
    issue certificates for the domain, and the `HTTPS` records can
    sometimes speed up the initial connection times.</span>

    <div class=hscroll>

    | Type    | Hostname     | Value                       |
    |---------|--------------|-----------------------------|
    | `A`     | —            | `152.53.36.213`             |
    | `AAAA`  | —            | `2a0a:4cc0:2000:172::1`     |
    | `HTTPS` | —            | `1 . alpn="h3,h2" ipv4hint="152.53.36.213" ipv6hint="2a0a:4cc0:2000:172::1"` |
    | `CNAME` | `www`        | `maxchernoff.ca.`           |
    | `CNAME` | `overleaf`   | `maxchernoff.ca.`           |
    | `CNAME` | `woodpecker` | `maxchernoff.ca.`           |
    | `CAA`   | —            | `0 issue "letsencrypt.org"` |
    | `CAA`   | —            | `0 issue "sectigo.com"`     |
    | `CAA`   | —            | `0 issuewild ";"`           |

    </div>

Installation
------------

1. Start the installer.

2. Disable the `root` account and create an administrator `max`.

3. Partition as follows:

    <div class=hscroll>

    | Index | Mount Point | Size      | Type   |
    |-------|-------------|-----------|--------|
    | 1     | `/boot/efi` | 500M      | EFI    |
    | 2     | `/boot`     | 4G        | ext4   |
    | 3     | `[SWAP]`    | 8G        | swap   |
    | 4     | `/`         | remaining | btrfs  |
    | 4.1   | `/home/`    | —         | subvol |

    </div>

4. Install the system.

5. Reboot into the installed system.

6. Install your <abbr>SSH</abbr> key:

    ```shell-session
    % ssh-copy-id max@maxchernoff.ca  # From your local machine
    ```

7. Log in to the server:

    ```shell-session
    % ssh max@maxchernoff.ca
    ```

10. Enable IPv6:

    ```shell-session
    $ sudo nmcli connection modify ens3 ipv6.method manual ipv6.addresses 2a0a:4cc0:2000:172::1/64 ipv6.gateway fe80::1
    $ sudo nmcli connection up ens3
    ```

12. Reboot.

    ```shell-session
    $ sudo systemctl reboot
    ```

Post-installation
-----------------

1. Install the needed packages:

    ```shell-session
    $ sudo rpm-ostree install borgbackup btrfs-progs fail2ban fish git goaccess htop snapper vim
    ```

2. Switch shell to `fish`:

    ```shell-session
    $ chsh -s /usr/bin/fish
    ```

4. Fix `/etc/fstab`:

    Change the options for `/` to `defaults,compress=zstd:1`.

5. Fix `/etc/passwd`: <span class=sidenote>If not done, `podman` will
   complain about a mismatched home location.</span>

    Change the home for `max` to `/var/home/max`.


Installing TeX Live
-------------------

1. Create the `tex` user:

    ```shell-session
    $ sudo useradd --create-home --shell /usr/sbin/nologin tex
    $ sudo loginctl enable-linger tex
    ```

2. Switch to the `tex` user:

    ```shell-session
    $ sudo -u tex fish
    ```

3. Create the necessary directories:

    ```shell-session
    % mkdir -p ~/texlive  # As the `tex` user
    ```

4. Download the installer:

    ```shell-session
    % cd $(mktemp -d)
    % curl -O 'https://ftp.math.utah.edu/pub/ctan/tex-archive/systems/texlive/tlnet/install-tl-unx.tar.gz'
    % tar xf install-tl-unx.tar.gz
    ```

5. Install TeX Live:

    ```shell-session
    % ./install-tl-*/install-tl \
    >     --repository=https://ftp.math.utah.edu/pub/ctan/tex-archive/systems/texlive/tlnet \
    >     --texdir=/var/home/tex/texlive --scheme=full --paper=letter
    ```


Web Server
----------

1. Generate a new <abbr>SSH</abbr> key:

    ```shell-session
    $ ssh-keygen -t ed25519
    ```

2. Add this new key as a single-repo deploy key on GitHub.

3. Clone the repository:

    ```shell-session
    $ git clone git@github.com:gucci-on-fleek/maxchernoff.ca.git
    ```

7. Create the `web` user:

    ```shell-session
    $ sudo useradd --create-home --shell /usr/sbin/nologin web
    ```

8. Allow the `web` user to run services:

    ```shell-session
    $ sudo loginctl enable-linger web
    ```

9. Switch to the `web` user:

    ```shell-session
    $ sudo -u web fish
    ```

14. Enable the analytics processor:

    ```shell-session
    $ sudo touch ~web/caddy/access.log
    $ touch ~/maxchernoff.ca/web/caddy/static/analytics/{graphs,requests.tsv}
    ```

18. Reboot to make sure everything starts correctly.


Woodpecker CI
-------------

1. Switch to the `web` user:

    ```shell-session
    $ sudo -u web fish
    ```

3. Add the Woodpecker server Podman secrets:

    ```shell-session
    % cat | tr -d '\n' | \ # Paste the secret, Enter, Ctrl+D
    >     podman secret create woodpecker_github_secret -
    % head --bytes=36 /dev/urandom | basenc --z85 | tr -d '\n' | \
    >     tee /dev/stderr | \ # Copy this value for later
    >     podman secret create woodpecker_agent_secret -
    ```

4. Create the `woodpecker` user:

    ```shell-session
    $ sudo useradd --create-home --shell /usr/sbin/nologin woodpecker
    $ sudo loginctl enable-linger woodpecker
    ```

5. Switch to the `woodpecker` user:

    ```shell-session
    $ sudo -u woodpecker fish
    ```

6. Set the Unix permissions:

    ```shell-session
    % chmod -R g-rX,o-rX ~  # As the `woodpecker` user
    % chmod a+X ~
    ```

7. Add the Woodpecker agent Podman secrets:

    ```shell-session
    % cat | tr -d '\n' | \ # Paste the secret, Enter, Ctrl+D
    >     podman secret create woodpecker_agent_secret -
    ```


Snapshots
---------

2. Mount the snapshot directory:

    ```ini
    # /etc/fstab
    # This line was here originally
    UUID={uuid}  /home/            btrfs  subvol={subvol},compress=zstd:1             0  0
    # Add this line
    UUID={uuid}  /home/.snapshots  btrfs  subvol={subvol}/.snapshots,compress=zstd:1  0  0
    ```
    ```shell-session
    $ sudo systemctl daemon-reload
    $ sudo mount -av
    ```
