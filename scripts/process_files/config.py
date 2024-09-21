# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from dataclasses import dataclass, field
from enum import Enum, StrEnum
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


class OtherUsers(StrEnum):
    """A sentinel value representing all other users."""

    OTHER = "other"


OtherUser = OtherUsers.OTHER


@runtime_checkable
class RuleProtocol(Protocol):
    """The operations that a rule must implement."""

    source: Path
    destination: Path
    operation: str

    def process(self, source: Path, destination: Path) -> None: ...


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
        """Converts the configuration types to the internal types."""
        self._paths = paths
        self.owner = acl.UserIds[owner] if owner else None
        self.selinux_type = (
            selinux.Types(selinux_type) if selinux_type else None
        )

        self.permissions = {}
        for user, permission in permissions.items():
            user = OtherUser if user == OtherUser else acl.UserIds[user]
            self.permissions[user] = FilePermissions[permission]

    @property
    def paths(self) -> Iterator[tuple[Path, Path]]:
        """Get the source and destination paths for all operations."""
        for path in self._paths:
            sources = Path(self.source).resolve(strict=True).glob(path)
            for source in sources:
                destination = self.destination / source.relative_to(self.source)
                yield source, destination

    def process_all(self) -> None:
        """Execute all of the mixin rule processors."""
        mro = type(self).mro()
        for source, destination in self.paths:
            for cls in mro:
                if TYPE_CHECKING:
                    assert isinstance(cls, RuleProtocol)

                if cls is not RuleProtocol and (
                    process := cls.__dict__.get("process")
                ):
                    if verbose:
                        print(cls.operation, source, destination)
                    if not dry_run:
                        process(self, source, destination)


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


def load_and_process_config(path: Path):
    """Loads the configuration file and processes all of the rules."""

    # Load the configuration file
    with open(path, "rb") as file:
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
    for link in data.get("link", []):
        rules.append(LinkRule(**link))

    for copy in data.get("copy", []):
        rules.append(CopyRule(**copy))

    for permissions in data.get("permissions", []):
        rules.append(PermissionsRule(**permissions))

    # Process all of the rules
    for rule in rules:
        rule.process_all()
