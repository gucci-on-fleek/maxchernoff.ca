# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from os import chown, symlink
from pathlib import Path
from pprint import pprint
from shutil import Error as CopyTreeError
from shutil import copy2 as copy_file
from shutil import copytree
from typing import TYPE_CHECKING

##############
### Mixins ###
##############

if TYPE_CHECKING:
    from .config import RuleBase, RuleProtocol
else:
    RuleBase = object
    RuleProtocol = object


class OwnerMixin(RuleProtocol):
    """Processes the `owner` configuration option."""

    operation = "owner"

    def process_recurse(
        self: RuleBase,  # type: ignore
        source: Path,
        destination: Path,
    ) -> None:
        """Changes the owner of the file."""
        if self.owner is None:
            return

        chown(
            path=destination,
            uid=self.owner,
            gid=self.owner,
            follow_symlinks=False,
        )


class FolderMixin(RuleProtocol):
    """Processes the `folder` rule type."""

    operation = "folder"

    def process_once(self, source: Path, destination: Path) -> None:
        """Creates a folder at the destination."""
        destination.mkdir(parents=True, exist_ok=True)


class CopyMixin(RuleProtocol):
    """Processes the `copy` rule type."""

    operation = "copy"

    def process_once(self, source: Path, destination: Path) -> None:
        """Copies the file from the source to the destination."""
        if source.is_dir():
            try:
                copytree(source, destination, symlinks=True, dirs_exist_ok=True)
            except CopyTreeError as errors:
                for source, destination, message in errors.args[0]:
                    if "File exists" not in message:
                        raise

                    source, destination = Path(source), Path(destination)
                    if destination.is_symlink():
                        destination.unlink()
                        symlink(source.readlink(), destination)
        elif source.is_file():
            copy_file(source, destination, follow_symlinks=False)
        else:
            raise ValueError(f"Invalid source type: {source}")


class LinkMixin(RuleProtocol):
    """Processes the `link` rule type."""

    operation = "link"

    def process_once(self, source: Path, destination: Path) -> None:
        """Creates a symbolic at the destination pointing to the source."""
        try:
            symlink(source, destination)
        except FileExistsError:
            if destination.is_symlink():
                destination.unlink()
                symlink(source, destination)
            else:
                raise
