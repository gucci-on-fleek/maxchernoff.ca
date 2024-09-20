# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from dataclasses import dataclass, field
from enum import IntFlag, IntEnum
from grp import getgrall
from os import getxattr, setxattr
from pathlib import Path
from pwd import getpwall
from struct import Struct
from typing import Literal, cast


#################
### Constants ###
#################

ACL_XATTR_NAME = "system.posix_acl_access"


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


class _Ids(IntEnum):
    """Base class for the (user|group) IDs used in ACL entries."""

    @classmethod
    def _missing_(cls, id: int):
        """It's possible to find an ID that doesn't map to any user or group
        name, so we'll name those `_<id>`."""
        # Store the objects so that each ID compares equal to itself
        cls._extra_members = getattr(cls, "_extra_members", {})
        try:
            obj = cls._extra_members[id]
        except KeyError:
            # Make a new object to hold the ID enum instance
            obj = object.__new__(cls)
            obj._name_ = f"_{id}"
            obj._value_ = id
            cls._extra_members[id] = obj
        return obj


class UnknownIds(IntEnum):
    """A singleton enum to hold the “Unknown” ID, which is used for all ACL
    entries except for the named user and group entries."""

    UNKNOWN = 2**32 - 1  # == (uint32_t) -1


# Get the user and group IDs from the system and store them in the enums
user_ids = {entry.pw_name: entry.pw_uid for entry in getpwall()}
group_ids = {entry.gr_name: entry.gr_gid for entry in getgrall()}

UserIds = _Ids("UserIds", user_ids)
GroupIds = _Ids("GroupIds", group_ids)
UnknownId = UnknownIds.UNKNOWN

# We need to define these types here to work around a Pyright bug
UnknownIdType = Literal[UnknownId]
TagUserObjType = Literal[Tags.USER_OBJ]
TagUserType = Literal[Tags.USER]
TagGroupObjType = Literal[Tags.GROUP_OBJ]
TagGroupType = Literal[Tags.GROUP]
TagMaskType = Literal[Tags.MASK]
TagOtherType = Literal[Tags.OTHER]


@dataclass
class Entry[
    T: Tags,
    P: Permissions,
    I: UserIds | GroupIds | UnknownIdType,
]:
    """A single ACL entry, which consists of a tag, a set of permissions, and
    an ID. The ID is only used for user and group entries, and is set to
    `UnknownIds.UNKNOWN` for all other entry types."""

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
                self.id = cast(I, UserIds(id))
            case Tags.GROUP:
                self.id = cast(I, GroupIds(id))
            case _:
                self.id = cast(I, UnknownIds.UNKNOWN)


@dataclass
class Entries:
    """A complete set of ACL entries, which is what is stored in the file's
    extended attribute."""

    # These entries are mandatory, but we make them optional so that we can
    # set them after the object is created if needed.
    user: Entry[TagUserObjType, Permissions, UnknownIdType] = field(init=False)
    group: Entry[TagGroupObjType, Permissions, UnknownIdType] = field(
        init=False
    )
    other: Entry[TagOtherType, Permissions, UnknownIdType] = field(init=False)
    # The mask will be dynamically created later on.
    mask: Entry[TagMaskType, Permissions, UnknownIdType] | None = None
    # The entries above all map to the standard Unix permissions; the entries
    # below are the true ACL entries.
    users: list[Entry[TagUserType, Permissions, UserIds]] = field(
        default_factory=list
    )
    groups: list[Entry[TagGroupType, Permissions, GroupIds]] = field(
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
                    UnknownIds.UNKNOWN,
                )
                self.group = Entry(
                    Tags.GROUP_OBJ,
                    arg.group,
                    UnknownIds.UNKNOWN,
                )
                self.other = Entry(
                    Tags.OTHER,
                    arg.other,
                    UnknownIds.UNKNOWN,
                )

            # Uh oh, invalid arguments
            case _:
                raise ValueError("Invalid data type")

    @property
    def mask(self) -> Entry[TagMaskType, Permissions, UnknownIdType]:
        """The mask entry is a special entry that holds the maximum permissions
        granted by all the named users and groups. We create this dynamically so
        that the user doesn't need to worry about it."""
        mask = Permissions.EMPTY
        for entry in [*self.users, *self.groups]:
            mask |= entry.perm

        return Entry(Tags.MASK, mask, UnknownIds.UNKNOWN)

    @mask.setter
    def mask(self, value: Entry[TagMaskType, Permissions, UnknownIdType]):
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


#################
### Functions ###
#################


def process_file(path: Path):
    """Set the ACL for a file. Just a simple example for now."""
    perms = PermissionsMode()
    perms.user = Permissions.READ
    perms.group = Permissions.EXEC
    perms.other = Permissions.EMPTY
    acl = Acl(perms)
    setxattr(path, ACL_XATTR_NAME, bytes(acl), follow_symlinks=True)
