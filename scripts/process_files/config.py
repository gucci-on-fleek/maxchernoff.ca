# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: MPL-2.0+ OR CC-BY-SA-4.0+
# SPDX-FileCopyrightText: 2024 Max Chernoff

###############
### Imports ###
###############

from io import BufferedReader
from os import chown, symlink
from pathlib import Path
from pprint import pprint
from pwd import getpwnam
from shutil import Error as CopyTreeError
from shutil import SameFileError
from shutil import copy2 as copy_file
from shutil import rmtree, copytree
from subprocess import run as subprocess_run
from tomllib import load as toml_load

from . import acl

#################
### Constants ###
#################

EXECUTABLE_MODE = 0o111
ROOT = 0


######################
### Initialization ###
######################

# Configuration Settings
dry_run: bool = False
verbose: bool = False

# Subuids and Subgids
subuids: dict[int, int] = {}
subgids: dict[int, int] = {}

with open("/etc/subuid") as file:
    for line in file:
        user, start, count = line.strip().split(":")
        subuids[getpwnam(user).pw_uid] = int(start)

with open("/etc/subgid") as file:
    for line in file:
        user, start, count = line.strip().split(":")
        subgids[getpwnam(user).pw_gid] = int(start)

# All path roots used
path_roots: set[Path] = set()


########################
### Helper Functions ###
########################


def x():
    raise NotImplementedError


def _expand_user(user: str) -> tuple[int, int]:
    """Expands a user to their UID and GID."""
    user = x(user)

    try:
        # UID Input
        return int(user), int(user)
    except ValueError:
        # Username Input
        try:
            passwd = getpwnam(user)
            return passwd.pw_uid, passwd.pw_gid
        except KeyError:
            # Try using /etc/subuid
            try:
                parent_name, sub_name = user.split("/")
                parent_uid, parent_gid = _expand_user(parent_name)
                inner_uid, inner_gid = _expand_user(sub_name)

                return (
                    subuids[parent_uid] + inner_uid,
                    subgids[parent_gid] + inner_gid,
                )
            except (ValueError, KeyError):
                raise ValueError(f"Invalid user: {user}")


def _expand_paths(base: str, paths: list[str]) -> list[Path]:
    """Expands a set of paths relative to a base path."""
    # Make sure that we have an absolute path in case we `cd` somewhere
    base: Path = Path(x(base)).absolute()
    out: list[Path] = []

    # Expand the globs for every path in the list
    for path in x(paths):
        out += list(sorted(base.glob(path))) or [base / path]

    # Remove the parent paths
    for path in out[:]:
        for parent in path.parents:
            if parent in out:
                out.remove(parent)

    return out


def _process_permissions(item: dict, path: Path):
    # Get the configuration values
    perms = x(item.get("permissions", {}))
    owner = x(item.get("owner", None))

    # Determine if the file is executable
    everyone_executable = _is_executable(path)

    # Set the owner
    if owner is not None:
        owner_uid, owner_gid = _expand_user(owner)
        chown(path, owner_uid, owner_gid, follow_symlinks=False)

    # If the path is a directory, then "X" adds the executable bit;
    # otherwise, it does nothing. In addition, if the path is a directory
    # and you have read permissions, you also get execute permissions.
    for user, perm in perms.items():
        if path.is_dir():
            perm = perm.replace("X", "x")
            if "r" in perm and "x" not in perm:
                perm = perm + "x"
        else:
            perm = perm.replace("X", "")
        perms[user] = perm

    # Parse the permissions
    acl_perms: dict[int | acl.OtherUser, str] = {}
    acl_perms[acl.OTHER_USER] = perms.pop("other", "")
    for user, perm in perms.items():
        uid, _ = _expand_user(user)
        acl_perms[uid] = perm

    # Set the permissions
    acl.set_path(path, acl_perms, everyone_executable=everyone_executable)

    # Add to the path roots
    path_roots.add(path)


def _is_executable(path: Path) -> bool:
    """Determines if the file is executable."""
    if path.is_file():
        return bool(path.stat().st_mode & EXECUTABLE_MODE)
    elif path.is_dir():
        return True
    else:
        return False


def _get_source_destination(item: dict) -> tuple[list[Path], list[Path]]:
    """Gets the source and destination paths for an item."""
    # Get the path roots
    source = Path(x(item["source"])).absolute()
    destination = Path(x(item["destination"])).absolute()

    # Expand the source globs
    sources = _expand_paths(item["source"], item["paths"])
    # Get the corresponding destination path for each source path
    destinations = [destination / src.relative_to(source) for src in sources]

    # Add the path roots
    path_roots.add(destination)

    return sources, destinations


######################
### Rule Functions ###
######################


def process_permissions(item: dict, paths: list[Path]):
    """Helper function to process the permissions of an item."""

    # Get all the paths
    recursive = item.get("recursive_permissions", False)
    if recursive:
        for path in paths[:]:
            for subpath in path.rglob("*"):
                paths.append(subpath)

    # Process each path
    for path in paths:
        _process_permissions(item, path)


def folder_item(item: dict):
    """Creates the requested folder if it does not already exist."""
    paths = _expand_paths(item["base"], item["paths"])

    for path in paths:
        if path.is_dir() and not path.is_symlink():
            # If the directory already exists, ignore it
            continue
        else:
            # Otherwise, create it
            path.mkdir(parents=True, exist_ok=True)

    process_permissions(item, paths)


def touch_item(item: dict):
    """Touches a path."""
    paths = _expand_paths(item["base"], item["paths"])
    for path in paths:
        path.touch(exist_ok=True)
    process_permissions(item, paths)


def link_item(item: dict):
    """Creates a symlink from the source to the destination."""
    # Get the source and destination paths
    sources, destinations = _get_source_destination(item)

    # Process each target
    for source, destination in zip(sources, destinations):
        # If the symlink is already correct, ignore it
        if destination.is_symlink():
            if destination.resolve() == source:
                continue

        # Otherwise, if there's something else here, remove it
        if destination.exists():
            if destination.is_dir() and not destination.is_symlink():
                rmtree(destination)
            else:
                destination.unlink()

        # Create the symlink
        try:
            symlink(source, destination)
        except FileNotFoundError:
            destination.parent.mkdir(parents=True, exist_ok=True)

    process_permissions(item, destinations)


def copy_item(item: dict):
    """Copies the source files to the destination."""
    # Get the source and destination paths
    sources, destinations = _get_source_destination(item)

    # Process each target
    for source, destination in zip(sources, destinations):
        if not destination.parent.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)

        # Process directories
        if source.is_dir() and not source.is_symlink():
            if destination.is_dir() and not destination.is_symlink():
                # Already a directory here, remove it
                rmtree(destination)
            elif destination.exists():
                # Something else here, remove it
                destination.unlink()

            # Now, remove the directory and copy over the new one
            copytree(source, destination, symlinks=True, dirs_exist_ok=True)

            # Reset the owner
            for path in destination.rglob("*"):
                chown(path, ROOT, ROOT, follow_symlinks=False)

        elif source.is_file() and not source.is_symlink():
            try:
                copy_file(source, destination, follow_symlinks=False)
            except SameFileError:
                pass

        elif source.is_symlink():
            try:
                symlink(source.readlink(), destination)
            except FileExistsError:
                destination.unlink()
                symlink(source.readlink(), destination)
        else:
            raise ValueError(f"Invalid source type: {source}")

        # Reset the owner
        chown(destination, ROOT, ROOT, follow_symlinks=False)

    process_permissions(item, destinations)


def permissions_item(item: dict):
    """Sets the permissions on a path."""
    paths = _expand_paths(item["base"], item["paths"])
    process_permissions(item, paths)


def process_config(file: BufferedReader):
    """Loads the configuration file and processes all of the rules."""
    if dry_run:
        print('"--dry-run" unsupported, sorry!')
        exit(1)

    # Load the configuration file
    data = toml_load(file)

    # Handle the variables
    variables = data.get("variables", {})

    global x

    def x[
        T: str | list[str] | dict[str, str | bool | int] | bool | int | None
    ](value: T) -> T:
        """Expands the variables in the value."""
        match value:
            case dict():
                return {x(k): x(v) for k, v in value.items()}  # type: ignore
            case list():
                return [x(v) for v in value]  # type: ignore
            case str():
                return value.format_map(variables)
            case bool() | int() | None:
                return value  # type: ignore
            case _:
                raise ValueError(f"Invalid value type: {type(value)}")

    # Process the rules
    for folder in data.get("folder", []):
        folder_item(folder)

    for link in data.get("link", []):
        link_item(link)

    for copy in data.get("copy", []):
        copy_item(copy)

    for permissions in data.get("permissions", []):
        permissions_item(permissions)

    for path in data.get("touch", []):
        touch_item(path)

    # Clean up the path roots
    for variable in variables.values():
        try:
            path_roots.remove(Path(variable))
        except (KeyError, ValueError):
            pass

    for path in path_roots.copy():
        for parent in path.parents:
            if parent in path_roots:
                try:
                    path_roots.remove(path)
                except KeyError:
                    pass

    # Process the SELinux rules
    try:
        rules: str = x(data["selinux"]["rules"])
        subprocess_run(
            ["/usr/sbin/semanage", "import"],
            input=rules.encode(),
            check=True,
        )
        subprocess_run(
            # fmt: off
            [
                "/usr/sbin/restorecon",
                "-R",  # Recursive
                "-T", "0",  # Multithreaded
                "-D", # Use hashes, maybe quicker?
                "-e", "/var/home/.snapshots",  # Exclude snapshots
                "-e", "/sysroot",  # Exclude OSTree sysroot
                # Exclude local directories
                "-e", "/var/home/builder/.local/",
                "-e", "/var/home/max/.local/",
                "-e", "/var/home/repo/.local/",
                "-e", "/var/home/tex/.local/",
                "-e", "/var/home/web/.local/",
                "-e", "/var/home/woodpecker/.local/",
                *path_roots, # All path roots
            ],
            # fmt: on
            check=True,
        )
    except KeyError:
        pass
