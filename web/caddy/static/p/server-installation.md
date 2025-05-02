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
    $ sudo machinectl shell repo@ /usr/bin/fish
    ```

1. Generate a new <abbr>SSH</abbr> key:

    ```shell-session
    % ssh-keygen -t ed25519
    ```

2. Add this new key as a single-repo deploy key on GitHub.

3. Clone the repositories:

    ```shell-session
    % git clone https://github.com/gucci-on-fleek/maxchernoff.ca.git
    % git clone --no-checkout \
    >     git@github.com:gucci-on-fleek/maxchernoff.ca-credentials.git \
    >     credentials
    ```

4. Enable variable interpolation:

    ```shell-session
    % cd ~repo/maxchernoff.ca/
    % echo > .git/config <<EOF
    [filter "git-filter-params"]
        process = git-filter-params ./variables.toml
        required
    EOF
    % git checkout master
    ```

5. Decrypt the credentials' repository:

    ```shell-session
    % cd ~repo/credentials/
    % echo 'PRIVATE-KEY' > .git/git-encrypt.private-key
    % echo > .git/config <<EOF
    [filter "git-encrypt"]
        clean = git-encrypt encrypt %f
        smudge = git-encrypt decrypt %f
        required
    EOF
    % git checkout master
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
    $ sudo machinectl shell tex@ /usr/bin/fish
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

18. Reboot to make sure everything starts correctly.

19. Once all the containers have been built, switch to `bootc`:

    ```shell-session
    $ sudo bootc switch maxchernoff.ca/fedora-iot:latest
    $ reboot
    ```


Woodpecker CI
-------------

1. Create the `woodpecker` user:

    ```shell-session
    $ sudo useradd --create-home --shell /usr/sbin/nologin woodpecker
    $ sudo loginctl enable-linger woodpecker
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
