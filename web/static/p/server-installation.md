---
title: Server Installation Guide
date: "2024-08-26"
---

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

    | Type    | Hostname   | Value                       |
    |---------|------------|-----------------------------|
    | `A`     | —          | `152.53.36.213`             |
    | `A`     | `www`      | `152.53.36.213`             |
    | `A`     | `overleaf` | `152.53.36.213`             |
    | `AAAA`  | —          | `2a0a:4cc0:2000:172::1`     |
    | `AAAA`  | `www`      | `2a0a:4cc0:2000:172::1`     |
    | `AAAA`  | `overleaf` | `2a0a:4cc0:2000:172::1`     |
    | `HTTPS` | —          | `1 . alpn="h3,h2" ipv4hint="152.53.36.213" ipv6hint="2a0a:4cc0:2000:172::1"` |
    | `HTTPS` | `www`      | `1 . alpn="h3,h2" ipv4hint="152.53.36.213" ipv6hint="2a0a:4cc0:2000:172::1"` |
    | `HTTPS` | `overleaf` | `1 . alpn="h3,h2" ipv4hint="152.53.36.213" ipv6hint="2a0a:4cc0:2000:172::1"` |
    | `CAA`   | —          | `0 issue "letsencrypt.org"` |
    | `CAA`   | —          | `0 issue "sectigo.com"`     |
    | `CAA`   | —          | `0 issuewild ";"`           |

    </div>

Installation
------------

1. Start the installer.

2. Disable the `root` account and create an administrator `max`.

3. Partition as follows:

    | Index | Mount Point | Size      | Type   |
    |-------|-------------|-----------|--------|
    | 1     | `/boot/efi` | 500M      | EFI    |
    | 2     | `/boot`     | 4G        | ext4   |
    | 3     | `[SWAP]`    | 8G        | swap   |
    | 4     | `/`         | remaining | btrfs  |
    | 4.1   | `/home/`    | —         | subvol |

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

8. Configure <abbr>SSH</abbr>:

    ```ini
    # /etc/ssh/sshd_config
    PasswordAuthentication no
    PermitRootLogin no
    AllowUsers max
    ```
    ```shell-session
    $ sudo systemctl restart sshd.service  # From the server
    ```

9. Disable `zezere`: <span class=sidenote>`zezere` is a web service for
   the initial configuration of IoT devices, which is unwanted for our
   server.</span>

    ```shell-session
    $ sudo systemctl disable --now zezere_ignition.timer
    ```

10. Enable IPv6:

    ```shell-session
    $ sudo nmcli connection modify ens3 ipv6.method manual ipv6.addresses 2a0a:4cc0:2000:172::1/64 ipv6.gateway fe80::1
    $ sudo nmcli connection up ens3
    ```

11. Fix booting: <span class=sidenote>The server and <abbr>VM</abbr>
    hosts' timezones are different which can make updates fail if
    `greenboot` runs before the times are adjusted..</span>

    ```shell-session
    $ sudo systemctl enable chrony-wait.service
    $ sudo systemctl edit greenboot-healthcheck.service
    ```
    ```ini
    [Unit]
    After=time-sync.target
    Requires=time-sync.target
    ```

12. Reboot.

    ```shell-session
    $ sudo systemctl reboot
    ```

Post-installation
-----------------

1. Install the needed packages:

    ```shell-session
    $ sudo rpm-ostree install btrfs-progs fail2ban fish git htop snapper vim
    ```

2. Switch shell to `fish`:

    ```shell-session
    $ chsh -s /usr/bin/fish
    ```

3. Enable `fail2ban`: <span class=sidenote>`rpm-ostree` sets very strict
   SELinux policies on `/var/`, which prevents `fail2ban` from writing
    to its database and log files.</span>

    ```ini
    # /etc/fail2ban/fail2ban.conf
    logtarget = SYSTEMD-JOURNAL
    dbfile = :memory:
    ```

    ```shell-session
    $ sudo systemctl enable --now fail2ban
    ```

4. Enable automatic updates:

    ```shell-session
    $ sudo systemctl enable --now rpm-ostreed-automatic.timer
    ```
    ```ini
    # /etc/rpm-ostreed.conf
    [Daemon]
    AutomaticUpdatePolicy=apply
    ```

5. Fix `/etc/fstab`:

    Change the options for `/` to `defaults,compress=zstd:1`.

6. Fix `/etc/passwd`: <span class=sidenote>If not done, `podman` will
   complain about a mismatched home location.</span>

    Change the home for `max` to `/var/home/max`.

7. Fix <kbd>Ctrl</kbd>-<kbd>L</kbd>:

    ```fish
    # ~/.config/fish/config.fish
    bind \f 'clear && commandline -f repaint'
    ```

8. Set some kernel network parameters: <span class=sidenote>Needed for
   `caddy`.</span>

    ```ini
    # /etc/sysctl.conf
    net.ipv4.ip_unprivileged_port_start=80
    net.core.wmem_max=7500000
    net.core.rmem_max=7500000
    ```

9. Adjust your home directory permissions: <span class=sidenote>Needed
   for the unprivileged containers to access the Git files.</span>

    ```shell-session
    $ chmod -R g-rX,o-rX ~
    $ chmod a+X ~
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
    % mkdir -p ~/.config/systemd/user
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

6. Set the Unix permissions:

    ```shell-session
    % chmod -R g-rX,o-rX ~
    % chmod a+X ~
    % chmod -R a+rX ~/texlive
    ```

7. Add the SELinux rules: <span class=sidenote>Needed for the containers
   to be able to access the TeX Live installation.</span>

    ```shell-session
    $ sudo semanage fcontext --add -t container_file_t '/var/home/tex/texlive(/.*)?'
    $ sudo restorecon -R /var/home/tex/texlive
    ```

8. Enable the auto-updater:

    ```shell-session
    $ sudo ln -s /var/home/max/maxchernoff.ca/tex/services/* ~tex/.config/systemd/user/
    $ sudo systemctl --user -M tex@ daemon-reload
    $ sudo systemctl --user -M tex@ enable --now update-texlive.{service,timer}
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

4. Add the scripts to your `$PATH`:

    ```shell-session
    $ fish_add_path ~/maxchernoff.ca/scripts/
    $ echo "abbr --add refresh 'sudo --validate && \
    >     web-pull && sudo (type -p web-restart) && \
    >     sudo (type -p web-status)'" >> ~/.config/fish/config.fish
    ```

5. Add the SELinux rules:

    ```shell-session
    $ sudo semanage fcontext --add -t container_file_t \
    >     '/var/home/max/maxchernoff.ca/web/config(/.*)?'
    $ sudo semanage fcontext --add -t container_file_t \
    >     '/var/home/max/maxchernoff.ca/web/static(/.*)?'
    ```

6. Set the Unix permissions:

    ```shell-session
    $ chmod -R a+rX /var/home/max/maxchernoff.ca/web
    $ chmod -R a=,u=rwX /var/home/max/maxchernoff.ca/.git
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

10. Create the necessary directories:

    ```shell-session
    % mkdir -p ~/caddy/{data,config,etc}  # As the `web` user
    % mkdir -p overleaf/{overleaf,mongo,redis}
    ```

11. Create the necessary links:

    ```shell-session
    % ln -s /var/home/max/maxchernoff.ca/web/containers ~/.config/containers
    % ln -s /var/home/max/maxchernoff.ca/web/config ~/caddy/etc
    % ln -s /var/home/max/maxchernoff.ca/web/static ~/caddy/static
    ```

12. Change the owner of the data directories to the container user:

    ```shell-session
    $ uid="$(grep web /etc/subuid | cut -d: -f2 /etc/subuid)"
    $ sudo chown -R $uid:$uid ~web/overleaf/{overleaf,mongo,redis} \
    >     ~web/caddy/{data,config}
    ```

13. Enable the auto-updater:

    ```shell-session
    $ sudo systemctl --user -M web@ enable podman-auto-update.{service,timer}
    ```

14. Start the services:

    ```shell-session
    $ sudo ~/maxchernoff.ca/scripts/web-start
    ```

15. If everything looks good, open the firewall:

    ```shell-session
    $ sudo firewall-cmd --permanent --zone=public \
    >     --add-port=80/tcp --add-port=443/tcp --add-port=443/udp
    $ sudo firewall-cmd --reload
    ```

16. Reboot to make sure everything starts correctly.


Snapshots
---------

1. Initialize snapper for the home directories:

    ```shell-session
    $ sudo snapper --config home create-config /var/home/
    ```

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

3. Enable automatic snapshots:

    ```shell-session
    $ sudo systemctl enable --now snapper-timeline.timer snapper-cleanup.timer
    ```
