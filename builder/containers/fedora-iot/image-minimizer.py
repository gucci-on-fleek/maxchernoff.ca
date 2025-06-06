#!/usr/bin/python3
# Source Code for maxchernoff.ca
# https://github.com/gucci-on-fleek/maxchernoff.ca
# SPDX-License-Identifier: GPL-2.0-only
# SPDX-FileCopyrightText: Copyright 2007-2016 Red Hat, Inc.
# (Lightly) modified from the original at https://github.com/weldr/lorax/blob/lorax-43.4-1/src/bin/image-minimizer

#
# image-minimizer: removes files and packages on the filesystem
#
# Copyright 2007-2016 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
import glob
import argparse
import os
import sys
# import rpm

class ImageMinimizer:
    filename = ''
    dryrun = False
    verbose = False
    prefix = None
    drops = set()
    visited = set()
    drops_rpm = set()
    ts = None

    def __init__(self, filename, root, dryrun, verbose):
        self.filename = filename
        self.prefix = root
        self.dryrun = dryrun
        self.verbose = verbose
        self.ts = None

    # Recursively adds all files and directories.
    # This is done becuase globbing does not allow
    # ** for arbitrary nesting.
    def add_directory(self, files, dirname):
        self.visited.add(dirname)
        for root, dirs, items in os.walk(dirname):
            for d in dirs:
                self.visited.add(os.path.join(root, d))
            for name in items:
                files.add(os.path.join(root, name))

    def add_pattern(self, files, pattern):
        globs = glob.glob(pattern)
        if self.verbose and len(globs) == 0:
            print("%s file not found" % pattern)
        for g in globs:
            if os.path.isdir(g):
                self.add_directory(files, g)
            else:
                files.add(g)

    def add_pattern_rpm(self, rpms, pattern):
        if self.ts is None:
            if self.prefix is None:
                raise RuntimeError('Must specify installation root for droprpm/keeprpm')
            self.ts = rpm.TransactionSet(self.prefix)
        mi = self.ts.dbMatch()
        mi.pattern('name', rpm.RPMMIRE_GLOB, pattern)
        not_found = True
        for hdr in mi:
            not_found = False
            rpms.add(hdr['name'])
        if self.verbose and not_found:
            print("%s package not found" % pattern)

    # Parses each line in the ifle
    def parse_line(self, line):
        command = ""
        pattern = ""
        tok = line.split(None,1)
        if len(tok) > 0:
            command = tok[0].lower()
            if len(tok) > 1:
                pattern = tok[1].strip()

        # Strip out all the comments and blank lines
        if not (command.startswith('#') or command==''):
            if command == 'keep':
                if self.prefix is not None :
                    pattern = pattern.lstrip('/')
                    pattern = os.path.join(self.prefix, pattern)
                keeps = set()
                self.add_pattern(keeps, pattern)
                self.drops.difference_update(keeps)
                keeps = None
            elif command == 'drop':
                if self.prefix is not None :
                    pattern = pattern.lstrip('/')
                    pattern = os.path.join(self.prefix, pattern)
                self.add_pattern(self.drops, pattern)
            elif command == 'keeprpm':
                keeps_rpm = set()
                self.add_pattern_rpm(keeps_rpm, pattern)
                self.drops_rpm.difference_update(keeps_rpm)
                keeps_rpm = None
            elif command == 'droprpm':
                self.add_pattern_rpm(self.drops_rpm, pattern)
            else:
                raise RuntimeError('Unknown Command: ' + command)

    def remove(self):
        for tag in sorted(self.drops, reverse=True):
            self.visited.add(os.path.split(tag)[0])
            if os.path.isdir(tag):
                self.visited.add(tag)
            else:
                if self.dryrun or self.verbose:
                    print("rm %s" % tag)
                if not self.dryrun:
                    os.remove(tag)

        #remove all empty directory. Every 8k counts!
        for d in sorted(self.visited, reverse=True):
            if len(os.listdir(d)) == 0:
                if self.dryrun or self.verbose:
                    print("rm -rf %s" % d)
                if not self.dryrun:
                    os.rmdir(d)

    def remove_rpm(self):
        def runCallback(reason, amount, total, key, client_data):
            if self.verbose and reason == rpm.RPMCALLBACK_UNINST_STOP:
                print("%s erased" % key)

        if len(self.drops_rpm) == 0:
            return

        for pkg in self.drops_rpm:
            if self.verbose:
                print("erasing: %s " % pkg)
            self.ts.addErase(pkg)
        if not self.dryrun:
            # skip ts.check(), equivalent to --nodeps
            self.ts.run(runCallback, "erase")

    def filter(self):
        if not os.path.isdir(self.prefix):
            raise FileNotFoundError(f"No such directory: '{self.prefix}")

        with open(self.filename) as f:
            for line in f:
                self.parse_line(line.strip())

        self.remove()
        self.remove_rpm()


def parse_options():
    parser = argparse.ArgumentParser(description="Image Minimizer")

    parser.set_defaults(root=os.environ.get('INSTALL_ROOT', '/mnt/sysimage/'), dry_run=False)

    parser.add_argument("-i", "--installroot", metavar="STRING", dest="root",
        help="Root path to prepend to all file patterns and installation root for RPM "
             "operations.  Defaults to INSTALL_ROOT or /mnt/sysimage/")

    parser.add_argument("--dryrun", action="store_true", dest="dryrun",
        help="If set, no filesystem changes are made.")

    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
        help="Display every action as it is performed.")

    parser.add_argument("filename", metavar="STRING", help="Filename to process")

    return parser.parse_args()


def main():
    try:
        args = parse_options()
        minimizer = ImageMinimizer(args.filename, args.root, args.dryrun,
                                   args.verbose)
        minimizer.filter()
    except SystemExit as e:
        sys.exit(e.code)
    except KeyboardInterrupt:
        print("Aborted at user request")

if __name__ == "__main__":
    main()
