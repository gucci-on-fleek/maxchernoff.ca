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


#################
### Constants ###
#################

SELINUX_XATTR_NAME = "security.selinux"


###############
### Classes ###
###############


class SELinuxUsers(bytes, Enum):
    """The possible values that the SELinux user can be on typical systems."""

    SYSTEM = b"system_u"
    USER = b"unconfined_u"


class SELinuxRoles(bytes, Enum):
    """The possible values that the SELinux role can be on typical systems."""

    OBJECT = b"object_r"


class SELinuxTypes(bytes):
    """The possible values that the SELinux type can be."""

    def __new__(cls, value: bytes):
        if not value.endswith(b"_t"):
            value += b"_t"
        return super().__new__(cls, value)

    def __repr__(self) -> str:
        return f"<SELinuxTypes: {super().__repr__()}>"


class SELinuxLevels(bytes, Enum):
    """The possible values that the SELinux level can be on typical systems."""

    DEFAULT = b"s0"


@dataclass
class SELinuxContext:
    """A class to represent a complete SELinux file context."""

    user: SELinuxUsers
    role: SELinuxRoles
    type: SELinuxTypes
    level: SELinuxLevels

    def __init__(
        self,
        *args: bytes
        | tuple[SELinuxUsers, SELinuxRoles, SELinuxTypes, SELinuxLevels]
        | Path,
    ):
        """Creates a context object from either a context byte string, a 4-tuple
        of the components, or by extracting the context from a file."""
        match args:
            case (
                SELinuxUsers(),
                SELinuxRoles(),
                SELinuxTypes(),
                SELinuxLevels(),
            ):
                self.user, self.role, self.type, self.level = args
            case (bytes() as context,):
                user, role, type, level = context.removesuffix(b"\0").split(
                    b":"
                )
                self.user, self.role, self.type, self.level = (
                    SELinuxUsers(user),
                    SELinuxRoles(role),
                    SELinuxTypes(type),
                    SELinuxLevels(level),
                )
            case (Path() as path,):
                self.__init__(getxattr(path, SELINUX_XATTR_NAME))
            case _:
                raise ValueError("Invalid arguments")

    def __bytes__(self) -> bytes:
        """Converts the context object to a byte string."""
        return b":".join((self.user, self.role, self.type, self.level))


#################
### Functions ###
#################


def process_file(path: Path):
    """Sets the SELinux context of a file. Just an example for now."""
    context = SELinuxContext(path)
    context.type = SELinuxTypes(b"user_home")
    setxattr(path, SELINUX_XATTR_NAME, bytes(context))
