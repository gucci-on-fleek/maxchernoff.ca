# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from dataclasses import dataclass, field
from enum import IntEnum, IntFlag
from os import getxattr, setxattr
from pathlib import Path
from pprint import pprint
from struct import Struct
from typing import Literal, cast, NewType


#################
### Constants ###
#################

ACL_XATTR_NAME = "system.posix_acl_access"
READ_ONLY_FILESYSTEM = 30
UNKNOWN_ID: "UnknownId" = 2**32 - 1  # == (uint32_t) -1


###############
### Classes ###
###############


class Tags(IntEnum):
    """The possible “types” of ACL entries."""

    USER_OBJ = 0x01  # The standard Unix user octet
    USER = 0x02  # A user identified by UID
    GROUP_OBJ = 0x04  # The standard Unix group octet
    GROUP = 0x08  # A group identified by GID
    MASK = 0x10  # The uppermost permissions available to named users and groups
    OTHER = 0x20  # The standard Unix other octet


class Permissions(IntFlag):
    """The possible permissions that can be granted by an ACL entry."""

    EMPTY = 0x00  # No permissions
    EXEC = 0x01  # Execute a file or search a directory
    WRITE = 0x02  # Write to a file or directory
    READ = 0x04  # Read a file or directory


UserId = NewType("UserId", int)
GroupId = NewType("GroupId", int)

# We need to define these types here to work around a Pyright bug
UnknownId = Literal[4294967295]
TagUserObj = Literal[Tags.USER_OBJ]
TagUser = Literal[Tags.USER]
TagGroupObj = Literal[Tags.GROUP_OBJ]
TagGroup = Literal[Tags.GROUP]
TagMask = Literal[Tags.MASK]
TagOther = Literal[Tags.OTHER]


@dataclass
class Entry[
    T: Tags,
    P: Permissions,
    I: UserId | GroupId | UnknownId,
]:
    """A single ACL entry, which consists of a tag, a set of permissions, and
    an ID. The ID is only used for user and group entries, and is set to
    `UNKNOWN_ID` for all other entry types."""

    tag: T
    perm: P
    id: I

    def __init__(self, tag: T, perm: P, id: I):
        """Create an ACL entry by converting all the parameters to the correct
        subtypes."""
        self.tag = cast(T, Tags(tag))
        self.perm = cast(P, Permissions(perm))
        match self.tag:
            case Tags.USER:
                self.id = UserId(id)  # type: ignore
            case Tags.GROUP:
                self.id = GroupId(id)  # type: ignore
            case _:
                self.id = UNKNOWN_ID  # type: ignore


@dataclass
class Entries:
    """A complete set of ACL entries, which is what is stored in the file's
    extended attribute."""

    # These entries are mandatory, but we make them optional so that we can
    # set them after the object is created if needed.
    user: Entry[TagUserObj, Permissions, UnknownId] = field(init=False)
    group: Entry[TagGroupObj, Permissions, UnknownId] = field(init=False)
    other: Entry[TagOther, Permissions, UnknownId] = field(init=False)
    # The mask will be dynamically created later on.
    mask: Entry[TagMask, Permissions, UnknownId] | None = None
    # The entries above all map to the standard Unix permissions; the entries
    # below are the true ACL entries.
    users: list[Entry[TagUser, Permissions, UserId]] = field(
        default_factory=list
    )
    groups: list[Entry[TagGroup, Permissions, GroupId]] = field(
        default_factory=list
    )

    def __iter__(self):
        """Iterate over all the ACL entries, in the correct order (as required
        by the kernel)."""
        yield self.user
        yield from self.users
        yield self.group
        yield from self.groups
        if self.mask and self.mask.perm != Permissions.EMPTY:
            yield self.mask
        yield self.other


@dataclass
class PermissionsMode:
    """A class to hold the standard (basic) Unix permissions for a file."""

    user: Permissions
    group: Permissions
    other: Permissions

    def __init__(
        self, *args: int | tuple[Permissions, Permissions, Permissions] | None
    ):
        match args:
            # A 3-tuple representing (user, group, other) permissions
            case (Permissions(), Permissions(), Permissions()):
                self.user, self.group, self.other = args

            # An octal integer representing the whole mode
            case (int(),):
                mode = args[0]
                self.user = Permissions((mode >> 6) & 0x07)
                self.group = Permissions((mode >> 3) & 0x07)
                self.other = Permissions((mode >> 0) & 0x07)

            # No arguments, so you'll need to set the permissions later
            case ():
                pass

            # Uh oh, invalid arguments
            case _:
                raise ValueError("Invalid arguments")


class Acl(Entries):
    """Manage the ACL entries for a file."""

    entry_struct = Struct("<HHI")
    header_struct = Struct("<I")
    entry_size = entry_struct.size
    header_size = header_struct.size
    HEADER = 0x02

    def __init__(self, arg: bytes | Path | PermissionsMode | None = None):
        super().__init__()
        match arg:
            # No arguments, so you'll need to set the permissions later
            case None:
                pass

            # Decode the bytestring stored in the extended attribute
            case bytes():
                self._from_bytes(arg)

            # Extract the permissions from a file
            case Path():
                if not arg.exists():
                    raise ValueError("Path does not exist")
                try:
                    data = getxattr(arg, ACL_XATTR_NAME, follow_symlinks=True)
                    self._from_bytes(data)
                except OSError:
                    mode = arg.stat().st_mode
                    self.__init__(PermissionsMode(mode))

            # Initialize the permissions from the standard Unix permission mode
            case PermissionsMode():
                self.user = Entry(
                    Tags.USER_OBJ,
                    arg.user,
                    UNKNOWN_ID,
                )
                self.group = Entry(
                    Tags.GROUP_OBJ,
                    arg.group,
                    UNKNOWN_ID,
                )
                self.other = Entry(
                    Tags.OTHER,
                    arg.other,
                    UNKNOWN_ID,
                )

            # Uh oh, invalid arguments
            case _:
                raise ValueError("Invalid data type")

    @property
    def mask(self) -> Entry[TagMask, Permissions, UnknownId]:
        """The mask entry is a special entry that holds the maximum permissions
        granted by all the named users and groups. We create this dynamically so
        that the user doesn't need to worry about it."""
        mask = Permissions.EMPTY
        for entry in [*self.users, *self.groups]:
            mask |= entry.perm

        return Entry(Tags.MASK, mask, UNKNOWN_ID)

    @mask.setter
    def mask(self, value: Entry[TagMask, Permissions, UnknownId]):
        # We don't need to do anything here, but we need to define the setter
        # to make the dataclass happy.
        pass

    def _from_bytes(self, data: bytes):
        """Decode the bytestring stored in an extended attribute."""
        # Make sure that we have the correct header
        (header,) = self.header_struct.unpack_from(data, 0)
        if header != self.HEADER:
            raise ValueError("Invalid header")

        # Unpack the entries
        for entry in self.entry_struct.iter_unpack(data[self.header_size :]):
            entry = Entry(*entry)
            match entry.tag:
                case Tags.USER_OBJ:
                    self.user = entry
                case Tags.GROUP_OBJ:
                    self.group = entry
                case Tags.OTHER:
                    self.other = entry
                case Tags.MASK:
                    pass
                case Tags.USER:
                    self.users.append(entry)
                case Tags.GROUP:
                    self.groups.append(entry)
                case _:
                    raise ValueError("Invalid tag")

    def _to_bytes(self) -> bytes:
        """Encode the ACL entries into a bytestring suitable for storing in an
        extended attribute."""
        data = bytearray()
        data.extend(self.header_struct.pack(self.HEADER))
        for entry in self:
            data.extend(self.entry_struct.pack(entry.tag, entry.perm, entry.id))
        return bytes(data)

    def __bytes__(self) -> bytes:
        return self._to_bytes()


######################
### User Interface ###
######################
"""Anything from here onwards is part of the public API."""

# Constants
OTHER_USER: "OtherUser" = "other"
PERMISSIONS = {
    "r": Permissions.READ,
    "rw": Permissions.READ | Permissions.WRITE,
    "": Permissions.EMPTY,
}

# Types
OtherUser = Literal["other"]


# Definitions
def set_path(
    path: Path,
    permissions: dict[int | OtherUser, str],
    all_execute: bool,
) -> None:
    """Set the ACL for a file."""
    if not (path.resolve().is_file() or path.resolve().is_dir()):
        return

    # Get the execution permission
    executable = Permissions.EXEC if all_execute else Permissions.EMPTY

    # Get the default permissions for all other users
    other = PERMISSIONS[permissions.pop(OTHER_USER, "")] | executable

    # Set the permissions for the destination file from scratch
    base_permissions = PermissionsMode()

    # Owner can always read and write
    base_permissions.user = Permissions.READ | Permissions.WRITE | executable

    # Group and other depend on the configuration
    base_permissions.group = other
    base_permissions.other = other

    # Create the ACL object and set the extra permissions
    acl = Acl(base_permissions)
    for user, perm_str in permissions.items():
        permission = PERMISSIONS[perm_str]
        assert user != OTHER_USER

        entry: Entry[TagUser, Permissions, UserId] = Entry(
            Tags.USER, permission | executable, UserId(user)
        )
        acl.users.append(entry)

    # Set the ACL for the destination file
    try:
        setxattr(path, ACL_XATTR_NAME, bytes(acl), follow_symlinks=True)
    except OSError as error:
        if error.errno == READ_ONLY_FILESYSTEM:
            pass
        else:
            raise error
