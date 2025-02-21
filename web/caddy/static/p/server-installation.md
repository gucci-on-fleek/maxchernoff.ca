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

- This guide was tested with Fedora IoT versions 40–41.

Pre-installation
----------------

1. Download the [Fedora IoT `.iso`
   installer](https://github.com/gucci-on-fleek/maxchernoff.ca). <span
   class=sidenote>In the unlikely scenario that your hosting provider
   offers Fedora IoT images, you can skip until step 4.</span>

2. Upload and attach the `.iso` installer to the virtual machine.

3. Configure the <abbr>VM</abbr> for <abbr>UEFI</abbr> boot.


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

12. Reboot.

    ```shell-session
    $ sudo systemctl reboot
    ```

Post-installation
-----------------

1. Install the needed packages:

    ```shell-session
    $ sudo rpm-ostree install borgbackup fish git-core htop perl-File-Find python3-pystemd qemu-guest-agent snapper vim
    ```

2. Switch shell to `fish`:

    ```shell-session
    $ chsh -s /usr/bin/fish
    ```

4. Fix `/etc/fstab`:

    Change the options for `/` to `defaults,compress=zstd:1,noatime`.

5. Fix `/etc/passwd`: <span class=sidenote>If not done, `podman` will
   complain about a mismatched home location.</span>

   Change the home for `max` to `/var/home/max`.

6. Disable `authselect`:

    ```shell-session
    $ sudo authselect opt-out
    ```


Downloading the repository
--------------------------

1. Create the `repo` user:

    ```shell-session
    $ sudo useradd --create-home --shell /usr/sbin/nologin repo
    ```

2. Switch to the `repo` user:

    ```
    $ sudo -u repo fish
    ```

1. Generate a new <abbr>SSH</abbr> key:

    ```shell-session
    % ssh-keygen -t ed25519
    ```

2. Add this new key as a single-repo deploy key on GitHub.

3. Clone the repository:

    ```shell-session
    % git clone git@github.com:gucci-on-fleek/maxchernoff.ca.git
    ```


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

6. Download and run the ConTeXt installer:

    ```shell-session
    % mkdir -p ~/context-installer
    % cd ~/context-installer
    % curl -O 'https://lmtx.pragma-ade.com/install-lmtx/context-linux-64.zip'
    % busybox unzip context-linux-64.zip
    % chmod a+x install.sh
    % ./install.sh
    % ln -s ~/context-installer/tex ~/context
    ```

7. Install the ConTeXt modules:

    ```shell-session
    % cd ~/context
    % ./texmf-linux-64/bin/mtxrun --script install-modules --install --all
    ```

Web Server
----------


1. Create the `web` user:

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

10. Add the GitHub webhook shared secret:

    ```shell-session
    % cat /dev/urandom | head --bytes=21 | base64 | tr -d '\n' \
        | podman secret create webhook_secret -

    % podman secret inspect webhook_secret --showsecret
    (then paste into the GitHub webhook secret field)
    ```

11. Add the DNS shared secrets:

    - A Podman secret `dnscontrol_tsig` that looks like

        ```text
        hmac-sha256:dnscontrol:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
        ```

    - A file `~web/knot/config/secrets.conf` that looks like

        ```yaml
        key:
          - id: dnscontrol
            algorithm: hmac-sha256
            secret: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=

          - id: maxchernoff-he
            algorithm: hmac-sha256
            secret: BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=

          - id: red-deer
            algorithm: hmac-sha256
            secret: CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC=

          # Plus some DNSControl stuff...
        ```

12. Add the email secrets:

    - A Podman secret `overleaf_smtp_password`:

        ```shell-session
        % cat /dev/urandom | head --bytes=21 | base64 | tr -d '\n' \
            | podman secret create overleaf_smtp_password -

        % podman secret inspect overleaf_smtp_password --showsecret \
            | podman run --rm -i --entrypoint=/bin/maddy \
                docker.io/foxcpp/maddy hash --hash argon2
        ```

    - A global service failure file:

        ```shell-session
        $ cat /dev/urandom | head --bytes=21 | base64 \
            | sudo tee ~repo/credentials/server@noreply.maxchernoff.ca \
            | podman run --rm -i --entrypoint=/bin/maddy \
                docker.io/foxcpp/maddy hash --hash argon2
        ```


    - A file `~web/maddy/config/users.conf` that looks like

        ```yaml
        overleaf@noreply.maxchernoff.ca: argon2:AAAAAAAAAAAAAAAAAAAAAAAA
        server@noreply.maxchernoff.ca: argon2:BBBBBBBBBBBBBBBBBBBBBBBBBB
        ```


18. Reboot to make sure everything starts correctly.

19. Once all the containers have been built, switch to `bootc`:

    ```shell-session
    $ sudo bootc switch maxchernoff.ca/fedora-iot:latest
    $ reboot
    ```


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

7. Add the Woodpecker agent Podman secrets:

    ```shell-session
    % cat | tr -d '\n' | \ # Paste the secret, Enter, Ctrl+D
    >     podman secret create woodpecker_agent_secret -
    ```


Container Builders
------------------

Sometimes there aren't any pre-built containers for the software that
you want to run, so we'll need to add a container builder.

1. Create the `builder` user:

    ```shell-session
    $ sudo useradd --create-home --shell /usr/sbin/nologin builder
    $ sudo loginctl enable-linger builder
    ```

2. That's pretty much it.


Snapshots
---------

1. Create subvolumes for the `.local` and `.cache` directories for every user:

    ```shell-session
    $ btrfs subvolume create {.local,.cache}
    ```

1. Mount the snapshot directory:

    ```ini
    # /etc/fstab
    # This line was here originally
    UUID={uuid}  /home/            btrfs  subvol={subvol},compress=zstd:1,noatime             0  0
    # Add this line
    UUID={uuid}  /home/.snapshots  btrfs  subvol={subvol}/.snapshots,compress=zstd:1,noatime  0  0
    ```
    ```shell-session
    $ sudo systemctl daemon-reload
    $ sudo mount -av
    ```
