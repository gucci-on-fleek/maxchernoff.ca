# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from os import listxattr, getxattr, setxattr
from pathlib import Path
from struct import Struct
from enum import IntFlag, IntEnum
from pwd import getpwall
from grp import getgrall
from dataclasses import dataclass, field
from typing import Literal, cast
from pprint import pprint


#################
### Constants ###
#################

ACL_XATTR_NAME = "system.posix_acl_access"


###############
### Classes ###
###############


class AclTags(IntEnum):
    """The possible “types” of ACL entries."""

    USER_OBJ = 0x01  # The standard Unix user octet
    USER = 0x02  # A user identified by UID
    GROUP_OBJ = 0x04  # The standard Unix group octet
    GROUP = 0x08  # A group identified by GID
    MASK = 0x10  # The uppermost permissions available to named users and groups
    OTHER = 0x20  # The standard Unix other octet


class AclPerms(IntFlag):
    """The possible permissions that can be granted by an ACL entry."""

    EMPTY = 0x00  # No permissions
    EXEC = 0x01  # Execute a file or search a directory
    WRITE = 0x02  # Write to a file or directory
    READ = 0x04  # Read a file or directory


class _AclIds(IntEnum):
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


class AclUnknownIds(IntEnum):
    """A singleton enum to hold the “Unknown” ID, which is used for all ACL
    entries except for the named user and group entries."""

    UNKNOWN = 2**32 - 1  # == (uint32_t) -1


# Get the user and group IDs from the system and store them in the enums
user_ids = {entry.pw_name: entry.pw_uid for entry in getpwall()}
group_ids = {entry.gr_name: entry.gr_gid for entry in getgrall()}

AclUserIds = _AclIds("AclUserIds", user_ids)
AclGroupIds = _AclIds("AclGroupIds", group_ids)
AclUnknownId = AclUnknownIds.UNKNOWN

# We need to define these types here to work around a Pyright bug
AclUnknownIdType = Literal[AclUnknownId]
AclTagUserObjType = Literal[AclTags.USER_OBJ]
AclTagUserType = Literal[AclTags.USER]
AclTagGroupObjType = Literal[AclTags.GROUP_OBJ]
AclTagGroupType = Literal[AclTags.GROUP]
AclTagMaskType = Literal[AclTags.MASK]
AclTagOtherType = Literal[AclTags.OTHER]


@dataclass
class AclEntry[
    T: AclTags,
    P: AclPerms,
    I: AclUserIds | AclGroupIds | AclUnknownIdType,
]:
    """A single ACL entry, which consists of a tag, a set of permissions, and
    an ID. The ID is only used for user and group entries, and is set to
    `AclUnknownIds.UNKNOWN` for all other entry types."""

    tag: T
    perm: P
    id: I

    def __init__(self, tag: int, perm: int, id: int):
        """Create an ACL entry by converting all the parameters to the correct
        subtypes."""
        self.tag = cast(T, AclTags(tag))
        self.perm = cast(P, AclPerms(perm))
        match self.tag:
            case AclTags.USER:
                self.id = cast(I, AclUserIds(id))
            case AclTags.GROUP:
                self.id = cast(I, AclGroupIds(id))
            case _:
                self.id = cast(I, AclUnknownIds.UNKNOWN)


@dataclass
class AclEntries:
    """A complete set of ACL entries, which is what is stored in the file's
    extended attribute."""

    # These entries are mandatory, but we make them optional so that we can
    # set them after the object is created if needed.
    user: AclEntry[AclTagUserObjType, AclPerms, AclUnknownIdType] = field(
        init=False
    )
    group: AclEntry[AclTagGroupObjType, AclPerms, AclUnknownIdType] = field(
        init=False
    )
    other: AclEntry[AclTagOtherType, AclPerms, AclUnknownIdType] = field(
        init=False
    )
    # The mask will be dynamically created later on.
    mask: AclEntry[AclTagMaskType, AclPerms, AclUnknownIdType] | None = None
    # The entries above all map to the standard Unix permissions; the entries
    # below are the true ACL entries.
    users: list[AclEntry[AclTagUserType, AclPerms, AclUserIds]] = field(
        default_factory=list
    )
    groups: list[AclEntry[AclTagGroupType, AclPerms, AclGroupIds]] = field(
        default_factory=list
    )

    def __iter__(self):
        """Iterate over all the ACL entries, in the correct order (as required
        by the kernel)."""
        yield self.user
        yield from self.users
        yield self.group
        yield from self.groups
        if self.mask and self.mask.perm != AclPerms.EMPTY:
            yield self.mask
        yield self.other


@dataclass
class PermsMode:
    """A class to hold the standard (basic) Unix permissions for a file."""

    user: AclPerms
    group: AclPerms
    other: AclPerms

    def __init__(self, *args: int | tuple[AclPerms, AclPerms, AclPerms] | None):
        match args:
            # A 3-tuple representing (user, group, other) permissions
            case (AclPerms(), AclPerms(), AclPerms()):
                self.user, self.group, self.other = args

            # An octal integer representing the whole mode
            case (int(),):
                mode = args[0]
                self.user = AclPerms((mode >> 6) & 0x07)
                self.group = AclPerms((mode >> 3) & 0x07)
                self.other = AclPerms((mode >> 0) & 0x07)

            # No arguments, so you'll need to set the permissions later
            case ():
                pass

            # Uh oh, invalid arguments
            case _:
                raise ValueError("Invalid arguments")


class Acl(AclEntries):
    """Manage the ACL entries for a file."""

    entry_struct = Struct("<HHI")
    header_struct = Struct("<I")
    entry_size = entry_struct.size
    header_size = header_struct.size
    HEADER = 0x02

    def __init__(self, arg: bytes | Path | PermsMode | None = None):
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
                    data = getxattr(arg, ACL_XATTR_NAME)
                    self._from_bytes(data)
                except OSError:
                    mode = arg.stat().st_mode
                    self.__init__(PermsMode(mode))

            # Initialize the permissions from the standard Unix permission mode
            case PermsMode():
                self.user = AclEntry(
                    AclTags.USER_OBJ,
                    arg.user,
                    AclUnknownIds.UNKNOWN,
                )
                self.group = AclEntry(
                    AclTags.GROUP_OBJ,
                    arg.group,
                    AclUnknownIds.UNKNOWN,
                )
                self.other = AclEntry(
                    AclTags.OTHER,
                    arg.other,
                    AclUnknownIds.UNKNOWN,
                )

            # Uh oh, invalid arguments
            case _:
                raise ValueError("Invalid data type")

    @property
    def mask(self) -> AclEntry[AclTagMaskType, AclPerms, AclUnknownIdType]:
        """The mask entry is a special entry that holds the maximum permissions
        granted by all the named users and groups. We create this dynamically so
        that the user doesn't need to worry about it."""
        mask = AclPerms.EMPTY
        for entry in [*self.users, *self.groups]:
            mask |= entry.perm

        return AclEntry(AclTags.MASK, mask, AclUnknownIds.UNKNOWN)

    @mask.setter
    def mask(self, value: AclEntry[AclTagMaskType, AclPerms, AclUnknownIdType]):
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
            entry = AclEntry(*entry)
            match entry.tag:
                case AclTags.USER_OBJ:
                    self.user = entry
                case AclTags.GROUP_OBJ:
                    self.group = entry
                case AclTags.OTHER:
                    self.other = entry
                case AclTags.MASK:
                    pass
                case AclTags.USER:
                    self.users.append(entry)
                case AclTags.GROUP:
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
    perms = PermsMode()
    perms.user = AclPerms.READ
    perms.group = AclPerms.EXEC
    perms.other = AclPerms.EMPTY
    acl = Acl(perms)
    setxattr(path, ACL_XATTR_NAME, bytes(acl))
