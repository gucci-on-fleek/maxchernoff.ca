# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from pathlib import Path
from typing import TYPE_CHECKING

#################
### Constants ###
#################


###############
### Classes ###
###############


##############
### Mixins ###
##############

if TYPE_CHECKING:
    from .config import RuleProtocol
else:
    RuleProtocol = object


class OwnerMixin(RuleProtocol):
    """Processes the `owner` configuration option."""

    operation = "owner"

    def process(self, source: Path, destination: Path) -> None:
        """Changes the owner of the file."""
        return NotImplemented


class CopyMixin(RuleProtocol):
    """Processes the `copy` rule type."""

    operation = "copy"

    def process(self, source: Path, destination: Path) -> None:
        """Copies the file from the source to the destination."""
        return NotImplemented


class LinkMixin(RuleProtocol):
    """Processes the `link` rule type."""

    operation = "link"

    def process(self, source: Path, destination: Path) -> None:
        """Creates a symbolic at the destination pointing to the source."""
        return NotImplemented
