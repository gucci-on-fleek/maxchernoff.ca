#!/usr/bin/python3
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

from subprocess import Popen
from waitress import serve
import sapi
import viewvc


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
    ]
)

# Start the Waitress server, which runs the ViewVC application
serve(
    application,
    listen="127.0.0.1:43219",
    threads=4,
)