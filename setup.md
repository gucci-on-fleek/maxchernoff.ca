About
=====

- All commands are ran from the `max` user on the server unless
  otherwise specified.

Pre-installation
================

1. Download the Fedora IoT `.iso` installer from the Fedora website.

2. Upload and attach the `.iso` installer to the virtual machine.

3. Configure the VM for UEFI boot.

4. Set the following DNS records:

    | Type  | Hostname   | Value                   |
    |-------|------------|-------------------------|
    | A     | —          | `152.53.36.213`         |
    | A     | `www`      | `152.53.36.213`         |
    | A     | `overleaf` | `152.53.36.213`         |
    | AAAA  | —          | `2a0a:4cc0:2000:172::1` |
    | AAAA  | `www`      | `2a0a:4cc0:2000:172::1` |
    | AAAA  | `overleaf` | `2a0a:4cc0:2000:172::1` |
    | HTTPS | —          | `1 . alpn="h3,h2" ipv4hint="152.53.36.213" ipv6hint="2a0a:4cc0:2000:172::1"` |
    | HTTPS | `www`      | `1 . alpn="h3,h2" ipv4hint="152.53.36.213" ipv6hint="2a0a:4cc0:2000:172::1"` |
    | HTTPS | `overleaf` | `1 . alpn="h3,h2" ipv4hint="152.53.36.213" ipv6hint="2a0a:4cc0:2000:172::1"` |



Installation
============

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

6. Install your SSH key:

    ```sh
    # From the host
    ssh-copy-id max@maxchernoff.ca
    ```

7. Log in to the server:

    ```sh
    # From the host
    ssh max@maxchernoff.ca
    ```

8. Configure `ssh`:

    ```conf
    # /etc/ssh/sshd_config
    PasswordAuthentication no
    PermitRootLogin no
    AllowUsers max
    ```
    ``` sh
    sudo systemctl restart sshd.service
    ```

9. Disable zezere:

    ``` sh
    sudo systemctl disable --now zezere_ignition.timer
    ```

10. Enable IPv6:

    ```sh
    sudo nmcli connection modify ens3 ipv6.method manual ipv6.addresses 2a0a:4cc0:2000:172::1/64 ipv6.gateway fe80::1
    sudo nmcli connection up ens3
    ```

11. Fix booting:

    ```sh
    sudo systemctl enable chrony-wait.service
    sudo systemctl edit greenboot-healthcheck.service
    ```
    ```conf
    [Unit]
    After=time-sync.target
    Requires=time-sync.target
    ```

12. Reboot.

    ```sh
    sudo systemctl reboot
    ```

Post-installation
=================

1. Install the needed packages:

    ```sh
    sudo rpm-ostree install borgbackup btrfs-progs fail2ban fish git htop snapper vim
    ```

2. Switch shell to `fish`:

    ```sh
    chsh -s /usr/bin/fish
    ```

3. Enable `fail2ban`:

    ```sh
    sudo systemctl enable --now fail2ban
    ```

4. Enable automatic updates:

    ```sh
    sudo systemctl enable --now rpm-ostreed-automatic.timer
    ```
    ```conf
    # /etc/rpm-ostreed.conf
    [Daemon]
    AutomaticUpdatePolicy=apply
    ```

5. Fix `/etc/fstab`:

    Change the options for `/` to `defaults,compress=zstd:1`.

6. Fix `/etc/passwd`:

    Change the home for `max` to `/var/home/max`.

7. Fix <kbd>Ctrl</kbd>-<kbd>L</kbd>:

    ```fish
    # ~/.config/fish/config.fish
    bind \f 'clear && commandline -f repaint'
    ```

8. Allow all users to bind to privileged ports:

    ```conf
    # /etc/sysctl.conf
    net.ipv4.ip_unprivileged_port_start=80
    ```

9. Adjust your home directory permissions:

    ```sh
    chmod -R g-rX,o-rX ~
    chmod a+X ~
    ```


Web Server
==========

1. Generate a new SSH key:

    ```sh
    ssh-keygen -t ed25519
    ```

2. Add this new key as a single-repo deploy key on GitHub.

3. Clone the repository:

    ```sh
    git clone git@github.com:gucci-on-fleek/maxchernoff.ca.git
    ```

4. Add the scripts to your `$PATH`:

    ```sh
    fish_add_path ~/maxchernoff.ca/scripts/
    echo "abbr --add refresh 'web-pull && sudo (type -p web-restart) && sudo (type -p web-status)'" >> ~/.config/fish/config.fish
    ```

5. Add the SELinux rules:

    ```sh
    sudo semanage fcontext --add -t container_file_t '/var/home/max/maxchernoff.ca/web/Caddyfile'
    sudo semanage fcontext --add -t container_file_t '/var/home/max/maxchernoff.ca/web/static(/.*)?'
    ```

6. Set the Unix permissions:

    ```sh
    chmod -R a+rX /var/home/max/maxchernoff.ca/web
    chmod -R a=,u=rwX /var/home/max/maxchernoff.ca/.git
    ```

7. Create the `web` user:

    ```sh
    sudo useradd --create-home --shell /usr/sbin/nologin web
    ```

8. Allow the `web` user to run services:

    ```sh
    sudo loginctl enable-linger web
    ```

9. Switch to the `web` user:

    ```sh
    sudo -u web fish
    ```

10. Create the necessary directories:

    ```sh
    # As the `web` user
    mkdir -p ~/caddy/{static,data,config}
    mkdir -p overleaf/{overleaf,mongo,redis}
    ```

11. Create the necessary links:

    ```sh
    # As the `web` user
    ln -s /var/home/max/maxchernoff.ca/web/containers ~/.config/containers
    ln -s /var/home/max/maxchernoff.ca/web/Caddyfile ~/caddy/Caddyfile
    ln -s /var/home/max/maxchernoff.ca/web/static ~/caddy/static
    ```

12. Enable the auto-updater:

    ```sh
    # Back to the `max` user
    sudo systemctl --user -M web@ enable podman-auto-update.{service,timer}
    ```

13. Start the services:

    ```sh
    sudo ~/maxchernoff.ca/scripts/web-start
    ```

14. If everything looks good, open the firewall:

    ```sh
    sudo firewall-cmd --permanent --zone=public --add-port=80/tcp --add-port=443/tcp --add-port=443/udp
    sudo firewall-cmd --reload
    ```

15. Reboot to make sure everything starts correctly.


Updating
========

Just run `refresh` to pull the latest changes and restart the services.