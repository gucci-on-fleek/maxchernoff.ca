# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from dataclasses import dataclass, field
from enum import Enum
from io import BufferedReader
from pathlib import Path
from pprint import pprint
from tomllib import load as toml_load
from typing import (
    TYPE_CHECKING,
    Iterator,
    KeysView,
    Literal,
    Protocol,
    ValuesView,
    runtime_checkable,
)

from . import acl, fs_ops, selinux


#################
### Constants ###
#################

OTHER_USER = "other"


#####################
### Configuration ###
#####################

dry_run = False
verbose = False


###############
### Classes ###
###############


class FilePermissions(Enum):
    """The possible file modes that you can set from the configuration."""

    r = acl.Permissions.READ
    w = acl.Permissions.WRITE
    rw = acl.Permissions.READ | acl.Permissions.WRITE
    _ = acl.Permissions.EMPTY


@runtime_checkable
class RuleProtocol(Protocol):
    """The operations that a rule must implement."""

    source: Path
    destination: Path
    operation: str

    def process_once(self, source: Path, destination: Path) -> None:
        """Processes the rule on the top-level paths."""

    def process_recurse(self, source: Path, destination: Path) -> None:
        """Processes the rule on every path below the top-level paths."""


@dataclass(kw_only=True)
class RuleBase(
    fs_ops.OwnerMixin,
    selinux.SELinuxMixin,
    acl.PermissionsMixin,
    RuleProtocol,
):
    """A concrete base class for all the rules."""

    paths: Iterator[tuple[Path, Path]]
    owner: acl.UserIds | None = None
    permissions: dict[acl.UserIds | Literal["other"], FilePermissions] = field(
        default_factory=dict
    )
    selinux_type: selinux.Types | None = None

    def __init__(
        self,
        *,
        paths: list[str],
        owner: str | None = None,
        permissions: dict[str, Literal["r", "w", "rw", ""]] = {},
        selinux_type: str | None = None,
    ):
        """Converts the configuration types to the internal types."""
        self._paths = paths
        self.owner = acl.UserIds[owner] if owner else None
        self.selinux_type = (
            selinux.Types(selinux_type) if selinux_type else None
        )

        self.permissions = {}
        for user, permission in permissions.items():
            user = OTHER_USER if user == OTHER_USER else acl.UserIds[user]
            permission = "_" if permission == "" else permission
            self.permissions[user] = FilePermissions[permission]

    @property
    def paths(self) -> Iterator[tuple[Path, Path]]:
        """Get the source and destination paths for all operations."""
        for path in self._paths:
            looped = False
            sources = self.source.absolute().glob(path)
            for source in sources:
                looped = True
                destination = self.destination / source.relative_to(self.source)
                yield source, destination
            if not looped:
                yield self.source / path, self.destination / path

    def process_all(self) -> None:
        """Execute all of the mixin rule processors."""
        mro = type(self).mro()
        for source, destination in self.paths:
            for cls in mro:
                if TYPE_CHECKING:
                    assert isinstance(cls, RuleProtocol)

                if cls is RuleProtocol:
                    continue
                elif process_once := cls.__dict__.get("process_once"):
                    if verbose:
                        print(cls.operation, source, destination)
                    if not dry_run:
                        process_once(self, source, destination)
                elif process_recurse := cls.__dict__.get("process_recurse"):
                    for root, _, files in source.walk(follow_symlinks=False):
                        for file in files:
                            source = source / root / file
                            destination = destination / root / file
                            if verbose:
                                print(cls.operation, source, destination)
                            if not dry_run:
                                process_recurse(self, source, destination)


@dataclass(kw_only=True)
class FolderRule(fs_ops.FolderMixin, RuleBase):
    """Handles the `folder` rule type."""

    source: Path
    destination: Path

    def __init__(self, *, base: str, **kwargs):
        """Converts the configuration types to the internal types."""
        self.source = Path(base)
        self.destination = Path(base)
        super().__init__(**kwargs)


@dataclass(kw_only=True)
class _InstallRule(RuleBase):
    """A base class for the `link` and `copy` rules ."""

    source: Path
    destination: Path

    def __init__(self, *, source: str, destination: str, **kwargs):
        """Converts the configuration types to the internal types."""
        self.source = Path(source)
        self.destination = Path(destination)
        super().__init__(**kwargs)


class LinkRule(fs_ops.LinkMixin, _InstallRule):
    """Handles the `link` rule type."""

    pass


class CopyRule(fs_ops.CopyMixin, _InstallRule):
    """Handles the `copy` rule type."""

    pass


@dataclass(kw_only=True)
class PermissionsRule(RuleBase):
    """Handles the `permissions` rule type."""

    source: Path
    destination: Path

    def __init__(self, *, base: str, **kwargs):
        """Converts the configuration types to the internal types."""
        self.source = Path(base)
        self.destination = Path(base)
        super().__init__(**kwargs)


#################
### Functions ###
#################


def process_config(file: BufferedReader):
    """Loads the configuration file and processes all of the rules."""

    data = toml_load(file)
    rules: list[RuleBase] = []
    variables = data.get("variables", {})

    def expand_recurse[
        T: list | dict
    ](parent: T, keys: range | KeysView, values: list | ValuesView) -> T:
        """Expands any variables in the configuration."""
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

    # Generate the rules
    for folder in data.get("folder", []):
        rules.append(FolderRule(**folder))

    for link in data.get("link", []):
        rules.append(LinkRule(**link))

    for copy in data.get("copy", []):
        rules.append(CopyRule(**copy))

    for permissions in data.get("permissions", []):
        rules.append(PermissionsRule(**permissions))

    # Process all of the rules
    for rule in rules:
        rule.process_all()
