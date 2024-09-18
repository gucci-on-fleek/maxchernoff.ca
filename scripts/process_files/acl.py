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


class AclTags(IntFlag):
    USER_OBJ = 0x01
    USER = 0x02
    GROUP_OBJ = 0x04
    GROUP = 0x08
    MASK = 0x10
    OTHER = 0x20


class AclPerms(IntFlag):
    EXEC = 0x01
    WRITE = 0x02
    READ = 0x04


class _AclIds(IntEnum):
    @classmethod
    def _missing_(cls, id: int):
        cls._extra_members = getattr(cls, "_extra_members", {})
        try:
            obj = cls._extra_members[id]
        except KeyError:
            obj = object.__new__(cls)
            obj._name_ = f"_{id}"
            obj._value_ = id
            cls._extra_members[id] = obj
        return obj


class AclUnknownIds(IntEnum):
    UNKNOWN = 2**32 - 1


user_ids = {entry.pw_name: entry.pw_uid for entry in getpwall()}
group_ids = {entry.gr_name: entry.gr_gid for entry in getgrall()}

AclUserIds = _AclIds("AclUserIds", user_ids)
AclGroupIds = _AclIds("AclGroupIds", group_ids)
AclUnknownId = AclUnknownIds.UNKNOWN

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
    tag: T
    perm: P
    id: I

    def __init__(self, tag: int, perm: int, id: int):
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
    user: AclEntry[AclTagUserObjType, AclPerms, AclUnknownIdType] = field(
        init=False
    )
    group: AclEntry[AclTagGroupObjType, AclPerms, AclUnknownIdType] = field(
        init=False
    )
    other: AclEntry[AclTagOtherType, AclPerms, AclUnknownIdType] = field(
        init=False
    )
    mask: AclEntry[AclTagMaskType, AclPerms, AclUnknownIdType] | None = None
    users: list[AclEntry[AclTagUserType, AclPerms, AclUserIds]] = field(
        default_factory=list
    )
    groups: list[AclEntry[AclTagGroupType, AclPerms, AclGroupIds]] = field(
        default_factory=list
    )

    def __iter__(self):
        yield self.user
        yield from self.users
        yield self.group
        yield from self.groups
        if self.mask:
            yield self.mask
        yield self.other


class Acl(AclEntries):
    entry_struct = Struct("<HHI")
    header_struct = Struct("<I")
    entry_size = entry_struct.size
    header_size = header_struct.size
    HEADER = 0x02

    def __init__(self, data: bytes | None = None):
        super().__init__()
        match data:
            case None:
                pass
            case bytes():
                self._from_bytes(data)
            case _:
                raise ValueError("Invalid data type")

    def _from_bytes(self, data: bytes):
        (header,) = self.header_struct.unpack_from(data, 0)
        if header != self.HEADER:
            raise ValueError("Invalid header")

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
                    self.mask = entry
                case AclTags.USER:
                    self.users.append(entry)
                case AclTags.GROUP:
                    self.groups.append(entry)

    def _to_bytes(self) -> bytes:
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
    if not path.exists():
        print(f"Path does not exist: {path}")
        exit(1)

    acl = Acl(getxattr(path, ACL_XATTR_NAME))
    pprint(acl)
    setxattr(path, ACL_XATTR_NAME, bytes(acl))
