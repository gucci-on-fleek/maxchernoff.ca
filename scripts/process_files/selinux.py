# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from dataclasses import dataclass
from enum import Enum
from os import getxattr, setxattr
from pathlib import Path
from pprint import pprint
from typing import TYPE_CHECKING

#################
### Constants ###
#################

SELINUX_XATTR_NAME = "security.selinux"
HOME_BASE_DIR = Path("/home/").resolve(strict=True)
USER_RUN_DIR = Path("/run/user/").resolve(strict=True)


###############
### Classes ###
###############


class Users(bytes, Enum):
    """The possible values that the SELinux user can be on typical systems."""

    SYSTEM = b"system_u"
    USER = b"unconfined_u"


class Roles(bytes, Enum):
    """The possible values that the SELinux role can be on typical systems."""

    OBJECT = b"object_r"


class Types(bytes):
    """The possible values that the SELinux type can be."""

    def __new__(cls, value: str | bytes):
        match value:
            case str():
                value = value.encode()
            case bytes():
                pass
            case _:
                raise ValueError("Invalid value")

        if not value.endswith(b"_t"):
            value += b"_t"
        return super().__new__(cls, value)

    def __repr__(self) -> str:
        return f"<Types: {super().__repr__()}>"


class Levels(bytes, Enum):
    """The possible values that the SELinux level can be on typical systems."""

    DEFAULT = b"s0"


@dataclass
class Context:
    """A class to represent a complete SELinux file context."""

    user: Users
    role: Roles
    type: Types
    level: Levels

    def __init__(
        self,
        *args: bytes | tuple[Users, Roles, Types, Levels] | Path,
    ):
        """Creates a context object from either a context byte string, a 4-tuple
        of the components, or by extracting the context from a file."""
        match args:
            case (
                Users(),
                Roles(),
                Types(),
                Levels(),
            ):
                self.user, self.role, self.type, self.level = args
            case (bytes() as context,):
                user, role, type, level = context.removesuffix(b"\0").split(
                    b":"
                )
                self.user, self.role, self.type, self.level = (
                    Users(user),
                    Roles(role),
                    Types(type),
                    Levels(level),
                )
            case (Path() as path,):
                self.__init__(
                    getxattr(path, SELINUX_XATTR_NAME, follow_symlinks=False)
                )
            case _:
                raise ValueError("Invalid arguments")

    def __bytes__(self) -> bytes:
        """Converts the context object to a byte string."""
        return b":".join((self.user, self.role, self.type, self.level))


##############
### Mixins ###
##############

if TYPE_CHECKING:
    from .config import RuleBase, RuleProtocol
else:
    RuleBase = object
    RuleProtocol = object


class SELinuxMixin(RuleProtocol):
    """Processes the `selinux_type` configuration option."""

    operation = "selinux"

    def process_recurse(
        self: RuleBase,  # type: ignore
        source: Path,
        destination: Path,
    ) -> None:
        """Sets the SELinux context type of a file."""
        if self.selinux_type is None:
            return

        # Get the current context of the file
        context = Context(destination)

        # Set the context user
        if destination.is_relative_to(
            HOME_BASE_DIR
        ) or destination.is_relative_to(USER_RUN_DIR):
            context.user = Users.USER
        else:
            context.user = Users.SYSTEM

        # Set the context type
        context.type = self.selinux_type

        # Set the context of the file
        pprint(context)
        # setxattr(destination, SELINUX_XATTR_NAME, bytes(context), follow_symlinks=False)  # TODO