#!/usr/bin/env python3
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from traceback import format_exception

from flask import Flask, Response, request
from waitress import serve

######################
### Initialization ###
######################

app = Flask(__name__)


@app.errorhandler(Exception)
def error_handler(error):
    """Return a minimal response for all errors."""
    if 500 <= error.code < 600:
        print(f"==== {request.url} ({error.code} {error.name}) ====")
        print("".join(format_exception(error)))

    return Response(
        response=f"{error.code} {error.name}",
        status=error.code,
        mimetype="text/plain",
    )


@app.route("/status")
def status():
    """A basic health check endpoint."""
    return Response(
        response="ok",
        status=200,
        mimetype="text/plain",
    )


##########################
### Endpoint Functions ###
##########################

# Nothing here yet


###################
### Entry Point ###
###################

if __name__ == "__main__":
    serve(app, listen="0.0.0.0:8080 [::]:8080")
