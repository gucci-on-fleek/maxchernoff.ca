#!/usr/bin/bash
# Based off of https://github.com/containers/composefs-rs/blob/0f636031/examples/uki/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh

check() {
    return 0
}

depends() {
    return 0
}

install() {
    inst \
        "/usr/local/bin/composefs-setup-root" /bin/composefs-setup-root
    inst \
        "${moddir}/composefs-setup-root.service" \
        "${systemdsystemunitdir}/composefs-setup-root.service"

    $SYSTEMCTL -q --root "${initdir}" add-wants \
        'initrd-root-fs.target' 'composefs-setup-root.service'
}
