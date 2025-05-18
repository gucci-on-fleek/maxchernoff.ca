#!/usr/bin/python3
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

from os import environ, nice
from subprocess import Popen

import sapi
import viewvc
from waitress import serve


# Runs the ViewVC application
def application(environ, start_response):
    server = sapi.WsgiServer(environ, start_response)
    cfg = viewvc.load_config("/etc/viewvc/viewvc.conf", server)
    viewvc.main(server, cfg)
    return []


# Start Anubis
Popen(
    [
        "/usr/local/bin/anubis",
    ],
    env={
        **environ,
        "BIND": "127.0.0.1:8923",  # Default value
        "COOKIE_DOMAIN": "tug.org",
        "COOKIE_EXPIRATION_TIME": "720h",  # 30 days, increased from default of 1 week
        "DIFFICULTY": "5",  # Increase from default of 4
        "WEBMASTER_EMAIL": "webmaster@tug.org",
        "TARGET": "http://localhost:43219",
        "REDIRECT_DOMAINS": "svn.tug.org:8369",

        # We'll hardcode the private key here because we're only being targeted
        # by naive bots; anyone who cared enough to find this would be smart
        # enough to simply use the SVN protocol instead of scraping the web
        # interface.
        "ED25519_PRIVATE_KEY_HEX": "3e5fabb2b118e31bbafc2356b7cd39874b1f7ccc1622e45fdd196ed55b9f102b",
    }
)

# Start the Caddy server
Popen(
    [
        "/usr/local/bin/caddy",
        "run",
        "--config",
        "/etc/caddy/Caddyfile",
        "--adapter",
        "caddyfile",
    ],
    pass_fds=[3, 4],  # Socket activation
)

# Renice the Python process to a lower priority
nice(20)

# Start the Waitress server, which runs the ViewVC application
serve(
    application,
    listen="127.0.0.1:43219",
    threads=8,
    backlog=8,
    outbuf_overflow=20 * 1024**2,
    inbuf_overflow=20 * 1024**2,
    expose_tracebacks=True,
    connection_limit=24,
    cleanup_interval=30,
    channel_timeout=30,
)
