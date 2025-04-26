#!/usr/bin/env python3
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from datetime import datetime
from hashlib import sha256
from hmac import compare_digest
from hmac import new as hmac_new
from os import environ as env
from pathlib import Path
from traceback import format_exception

from flask import Flask, Response, request
from waitress import serve
from werkzeug.exceptions import HTTPException as _HTTPException

#################
### Constants ###
#################

app = Flask(__name__)

ZONE = datetime.now().astimezone().tzinfo
UPDATE_TRIGGER = Path("/root/triggers/install-repo-maxchernoff.ca.trigger")


#########################
### Utility Functions ###
#########################


class HTTPException(_HTTPException):
    """Custom HTTPException class for handling errors."""

    def __init__(self, code: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code


@app.errorhandler(Exception)
def error_handler(error: HTTPException) -> Response:
    """Return a minimal response for all errors."""
    if not getattr(error, "code", None):
        error.code = 500

    if 500 <= (error.code or 500) < 600:
        print(f"==== {request.url} ({error.code} {error.name}) ====")
        print("".join(format_exception(error)))

    return Response(
        response=f"{error.code} {error.name}",
        status=error.code,
        mimetype="text/plain",
    )


def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise HTTPException(403)

    hash_object = hmac_new(
        secret_token.encode("utf-8"),
        msg=payload_body,
        digestmod=sha256,
    )
    expected_signature = "sha256=" + hash_object.hexdigest()

    if not compare_digest(expected_signature, signature_header):
        raise HTTPException(403)


##########################
### Endpoint Functions ###
##########################


@app.route("/status")
def status():
    """A basic health check endpoint."""
    now = datetime.now(ZONE)
    return {
        "status": "ok",
        "local_time": now.strftime("%Y-%m-%d %l:%M%P %Z"),
        "unix_time": int(now.timestamp()),
        "service": "flask",
    }


@app.route("/update-server", methods=["POST"])
def update_server():
    """Updates the server with the latest changes."""

    # Verify the request was sent from GitHub
    verify_signature(
        payload_body=request.get_data(),
        secret_token=env["WEBHOOK_SECRET"],
        signature_header=request.headers.get("x-hub-signature-256"),
    )

    # Update the server
    with open(UPDATE_TRIGGER, "wt") as trigger:
        trigger.write(datetime.now().isoformat())

    return {"status": "ok"}


###################
### Entry Point ###
###################

if __name__ == "__main__":
    serve(app, listen="0.0.0.0:8080 [::]:8080")
