# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from enum import Enum, StrEnum
from typing import Literal, KeysView, ValuesView
from dataclasses import dataclass, field
from pathlib import Path
from tomllib import load as toml_load
from pprint import pprint
from abc import abstractmethod

from . import acl, selinux

#################
### Constants ###
#################


###############
### Classes ###
###############


class FilePermissions(Enum):
    r = acl.Permissions.READ
    w = acl.Permissions.WRITE
    rw = acl.Permissions.READ | acl.Permissions.WRITE


class OtherUsers(StrEnum):
    OTHER = "other"


OtherUser = OtherUsers.OTHER


@dataclass(kw_only=True)
class Rule:
    paths: list[Path]
    owner: acl.UserIds | None = None
    permissions: dict[acl.UserIds | OtherUsers, FilePermissions] = field(
        default_factory=dict
    )
    selinux_type: selinux.Types | None = None

    def __init__(
        self,
        *,
        paths: list[str],
        owner: str | None = None,
        permissions: dict[str, Literal["r", "w", "rw"]] = {},
        selinux_type: str | None = None,
    ):
        self.paths = self.make_paths(paths)
        self.owner = acl.UserIds[owner] if owner else None
        self.selinux_type = (
            selinux.Types(selinux_type) if selinux_type else None
        )

        self.permissions = {}
        for user, permission in permissions.items():
            user = OtherUser if user == OtherUser else acl.UserIds[user]
            self.permissions[user] = FilePermissions[permission]

    def make_paths(self, paths: list[str]) -> list[Path]:
        base = self.path_base
        out = []
        for path in paths:
            out.extend(sorted(Path(base).glob(path)))
        return out

    def process(self) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def path_base(self) -> Path: ...


@dataclass(kw_only=True)
class _InstallRule(Rule):
    source: Path
    destination: Path

    def __init__(self, *, source: str, destination: str, **kwargs):
        self.source = Path(source)
        self.destination = Path(destination)
        super().__init__(**kwargs)

    @property
    def path_base(self) -> Path:
        return self.source


class LinkRule(_InstallRule):
    def process(self) -> None:
        raise NotImplementedError
        super().process()


class CopyRule(_InstallRule):
    def process(self) -> None:
        raise NotImplementedError
        super().process()


@dataclass(kw_only=True)
class PermissionsRule(Rule):
    base: Path

    def __init__(self, *, base: str, **kwargs):
        self.base = Path(base)
        super().__init__(**kwargs)

    @property
    def path_base(self) -> Path:
        return self.base


#################
### Functions ###
#################


def process_file(path: Path):
    with open(path, "rb") as file:
        data = toml_load(file)

    rules: list[Rule] = []
    variables = data.get("variables", {})

    def expand_recurse[
        T: list | dict
    ](parent: T, keys: range | KeysView, values: list | ValuesView) -> T:
        for key, value in zip(keys, values):
            match value:
                case dict():
                    value = expand_recurse(value, value.keys(), value.values())
                case list():
                    value = expand_recurse(value, range(len(value)), value)
                case str():
                    value = value.format(**variables)
                case _:
                    pass
            parent[key] = value
        return parent

    data = expand_recurse(data, data.keys(), data.values())

    for link in data.get("link", []):
        rules.append(LinkRule(**link))

    for copy in data.get("copy", []):
        rules.append(CopyRule(**copy))

    for permissions in data.get("permissions", []):
        rules.append(PermissionsRule(**permissions))

    pprint(rules)

    for rule in rules:
        rule.process()
