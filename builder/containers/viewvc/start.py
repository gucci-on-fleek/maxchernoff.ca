#!/usr/bin/python3
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

from os import nice
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
    connection_limit=20,
    cleanup_interval=10,
    channel_timeout=10,
    max_request_body_size=10 * 1024,
    channel_request_lookahead=2,
)
