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

    | Index | Mount Point | Name   | Size      | Type  |
    |-------|-------------|--------|-----------|-------|
    | 1     | `/boot/efi` | `efi`  | 500M      | EFI   |
    | 2     | `/boot`     | `boot` | 4G        | ext4  |
    | 3     | `[SWAP]`    |        | 8G        | swap  |
    | 4     | `/`         | `root` | remaining | btrfs |
    | 4.1   | `/ostree/deploy/fedora-iot/var/home/` | `/ostree/deploy/fedora-iot/var/home/` | — | subvol |

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

8. Fix the partition types and labels:

    ```shell-session
    $ sudo sfdisk --part-type /dev/vda 1 'EFI System'
    $ sudo sfdisk --part-label /dev/vda 1 'efi'

    $ sudo sfdisk --part-type /dev/vda 2 'Linux extended boot'
    $ sudo sfdisk --part-label /dev/vda 2 'boot'

    $ sudo sfdisk --part-type /dev/vda 3 'Linux swap'
    $ sudo sfdisk --part-label /dev/vda 3 'swap'

    $ sudo sfdisk --part-type /dev/vda 4 'Linux root (x86-64)'
    $ sudo sfdisk --part-label /dev/vda 4 'root'
    ```

Post-installation
-----------------

2. Switch shell to `fish`:

    ```shell-session
    $ chsh -s /usr/bin/fish
    ```

5. Fix `/etc/passwd`: <span class=sidenote>If not done, `podman` will
   complain about a mismatched home location.</span>

   Change the home for `max` to `/var/home/max`.

6. Disable `authselect`:

    ```shell-session
    $ sudo authselect opt-out
    ```

7. Temporarily disable SELinux by editing `/etc/selinux/config` and
   setting `SELINUX=permissive`.

7. Set some OSTree settings:

    ```shell-session
    sudo ostree config set ex-fsverity.required true
    sudo ostree config set ex-integrity.composefs yes
    sudo ostree config set sysroot.bootloader none
    ```

8. Switch to `bootc`:

    ```shell-session
    $ cat > /etc/containers/policy.json <<'EOF'
    {
        "default": [
            {
                "type": "reject"
            }
        ],
        "transports": {
            "docker": {
                "maxchernoff.ca": [
                    {
                        "type": "sigstoreSigned",
                        "rekorPublicKeyData": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFMkcyWSsydGFiZFRWNUJjR2lCSXgwYTlmQUZ3cgprQmJtTFNHdGtzNEwzcVg2eVlZMHp1ZkJuaEM4VXIvaXk1NUdoV1AvOUEvYlkyTGhDMzBNOStSWXR3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCgo=",
                        "keyData": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFdU51aWh1SUpOSFhvUUVacTF5SHZPZkZZU1gwYgpYMjlMVUYremQzdWVHS3RKV1Z4WlFJWEJCZVN4YnBxV1djdDQzR1RoUE44QmFHbWpDT0tDTjNrWUp3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCgo="
                    }
                ]
            }
        }
    }
    EOF

    $ cat > /etc/containers/registries.d/default.yaml <<'EOF'
    docker:
        maxchernoff.ca:
            use-sigstore-attachments: true
    EOF

    $ cat > /etc/systemd/network/80-wan.network <<'EOF'
    [Match]
    Name=*

    [Network]
    DHCP=yes
    EOF

    $ sudo bootc switch --enforce-container-sigpolicy maxchernoff.ca/fedora-iot:latest

    $ sudo systemctl reboot
    ```

9. SELinux fixes

    ```shell-session
    $ sudo semanage login --add --seuser staff_u --range 's0-s0:c0.c1023' max
    $ sudo semanage user --modify user_u --range s0-s0:c0.c1023
    $ sudo semanage login --modify --seuser user_u --range 's0-s0:c0.c1023' __default__

    $ echo '%wheel ALL=(ALL) TYPE=sysadm_t ROLE=sysadm_r ALL' | sudo tee /etc/sudoers.d/selinux

    $ sudo restorecon -vR /var/ /etc/
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
    % cat >> .git/config <<'EOF'
    [filter "git-filter-params"]
        process = git-filter-params ./variables.toml
        required
    EOF
    % rm ./.git/index
    % PATH=$HOME/maxchernoff.ca/usrlocal/bin:/usr/bin git reset --hard @
    ```

5. Decrypt the credentials' repository:

    ```shell-session
    % cd ~repo/credentials/
    % echo 'PRIVATE-KEY' > .git/git-encrypt.private-key
    % cat >> .git/config <<'EOF'
    [filter "git-encrypt"]
        clean = git-encrypt encrypt %f
        smudge = git-encrypt decrypt %f
        required
    EOF
    % rm ./.git/index
    % PATH=$HOME/maxchernoff.ca/usrlocal/bin:/usr/bin git reset --hard @
    ```

6. Install the files:

    ```shell-session
    % exit
    $ sudo cp -r ~repo/maxchernoff.ca/usrlocal/{lib,bin} /usr/local/
    $ sudo web-install ~repo/maxchernoff.ca/install-rules.toml
    ```

Installing TeX Live
-------------------

1. Create the `tex` user:

    ```shell-session
    $ sudo useradd --create-home --shell /usr/sbin/nologin tex
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

5. Install the TeX Live gpg keys:

    ```shell-session
    % curl -fsSL https://tug.org/texlive/files/texlive.asc | tlmgr key add -
    % curl -fsSL https://www.preining.info/rsa.asc | tlmgr key add -
    ```

5. Install the extra TeX Live repositories:

    ```shell-session
    % tlmgr repository add https://tug.org/texlive/tlcritical/ tlcritical
    % tlmgr repository add https://ctan.math.utah.edu/ctan/tex-archive/systems/texlive/tlcontrib tlcontrib
    % tlmgr pinning add tlcontrib "*"
    % tlmgr install collection-contrib
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
    ```

18. Reboot to make sure everything starts correctly.


Woodpecker CI
-------------

1. Create the `woodpecker` user:

    ```shell-session
    $ sudo useradd --create-home --shell /usr/sbin/nologin woodpecker
    ```


Container Builders
------------------

Sometimes there aren't any pre-built containers for the software that
you want to run, so we'll need to add a container builder.

1. Create the `builder` user:

    ```shell-session
    $ sudo useradd --create-home --shell /usr/sbin/nologin builder
    ```

2. That's pretty much it.
