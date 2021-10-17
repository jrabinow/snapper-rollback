#!/usr/bin/env -S python3
# -*- coding: utf-8 -*-

"""
Script to rollback to snapper snapshot using the layout proposed in the snapper
archwiki page
https://wiki.archlinux.org/index.php/Snapper#Suggested_filesystem_layout
"""

from datetime import datetime

import argparse
import btrfsutil
import configparser
import logging
import os
import pathlib
import stat
import sys
import tempfile


LOG = logging.getLogger()
LOG.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
LOG.addHandler(ch)


def verify_migration():
    """this function handles migrating from legacy to new config file"""

    # this package conflicts with rollback-git, so rollback-git should be
    # uninstalled when we run this. However, pacman appends `.pacsave` to config
    # files so we should be checking for /etc/rollback.conf.pacsave, NOT
    # /etc/rollback.conf
    if os.path.isfile("/etc/rollback.conf.pacsave"):

        try:
            legacy_config = read_config("/etc/rollback.conf.pacsave")
            subvolroot = legacy_config.get("subvolumes", "subvolroot")
            subvolsnap = legacy_config.get("subvolumes", "subvolsnap")
            subvolid5 = legacy_config.get("subvolumes", "subvolid5")
        except configparser.NoOptionError as e:
            LOG.error("invalid legacy config, falling back to default values")
            subvolroot = "@"
            subvolsnap = "@snapshots"
            subvolid5 = "/btrfsroot"

        with tempfile.NamedTemporaryFile(
            prefix="migrate_cfg_", suffix=".sh", delete=False, mode="w"
        ) as f:
            f.write(
                f"""#!/bin/sh
set -e -u -o pipefail

cat > /tmp/snapper-rollback.conf << EOF
# Rollback to snapper snapshot
#
# Requires a flat subvolume layout like specified here:
# https://wiki.archlinux.org/index.php/Snapper#Suggested_filesystem_layout
#
# Run with snapshot number as an argument like "snapper-rollback 642"
# This can be run either from your installed system or from a live arch ISO if
# you adjust the variables accordingly

[root]
# Name of your root subvolume
subvol_main = {subvolroot}
# Name of your snapper snapshot subvolume
subvol_snapshots = {subvolsnap}
# If you haven't already mounted it there yourself, your btrfs partition with
# subvolid=5 will automatically be mounted to this mountpoint
mountpoint = {subvolid5}
# if btrfs subvol id 5 isn't mounted, then mount this device to \\`mountpoint\\`
# directory. This setting is optional, but if unset, you'll have to mount the
# partition manually!
#dev = /dev/sda42
EOF
mv /tmp/snapper-rollback.conf /etc/

cat << EOF
Success! You can now delete /etc/rollback.conf.pacsave if you wish. You can also
save this script and run it again once you've rebooted into your rolled-back
system.

To continue rolling back your system, simply rerun \\`snapper-rollback\\`
EOF
"""
            )
        st = os.stat(f.name)
        os.chmod(f.name, st.st_mode | stat.S_IEXEC)

        print(
            """
Hey there, sorry for the interruption! A few things have changed since you installed this script.
Let's migrate your config and you'll be good to go!
Please run the following command from a shell:

$ sudo {}
""".format(
                f.name
            )
        )
        sys.exit(0)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Rollback to snapper snapshot based on snapshot ID",
    )
    parser.add_argument(
        "snap_id", metavar="SNAPID", type=str, help="ID of snapper snapshot"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="don't actually do anything, just print the actions out",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="/etc/snapper-rollback.conf",
        help="configuration file to use (default: /etc/snapper-rollback.conf)",
    )
    args = parser.parse_args()
    return args


def read_config(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    return config


def ensure_dir(dirpath, dry_run=False):
    if not os.path.isdir(dirpath):
        try:
            if dry_run:
                LOG.info("mkdir -p '{}'".format(dirpath))
            else:
                os.makedirs(dirpath)
        except OSError as e:
            LOG.fatal("error creating dir '{}': {}".format(dirpath, e))
            raise


def mount_subvol_id5(target, source=None, dry_run=False):
    """
    There is no built-in `mount` function in python, let's shell out to an `os.system` call
    Also see https://stackoverflow.com/a/29156997 for a cleaner alternative
    """

    ensure_dir(target, dry_run=dry_run)

    if not os.path.ismount(target):
        shellcmd = "mount -o subvolid=5 {} {}".format(source or "", target)
        if dry_run:
            LOG.info(shellcmd)
            ret = 0
        else:
            ret = os.system(shellcmd)
        if ret != 0:
            raise OSError("unable to mount {}".format(target))


def rollback(subvol_main, subvol_main_newname, subvol_rollback_src, dev, dry_run=False):
    """
    Rename root subvolume, then create a snapshot of the subvolume to
    the old root location
    """
    try:
        if dry_run:
            LOG.info("mv {} {}".format(subvol_main, subvol_main_newname))
            LOG.info(
                "btrfs subvolume snapshot {} {}".format(
                    subvol_rollback_src, subvol_main
                )
            )
            LOG.info("btrfs subvolume set-default {}".format(subvol_main))
        else:
            os.rename(subvol_main, subvol_main_newname)
            btrfsutil.create_snapshot(subvol_rollback_src, subvol_main)
            btrfsutil.set_default_subvolume(subvol_main)
        LOG.info(
            "{}Rollback to {} complete. Reboot to finish".format(
                dry_run and "[DRY-RUN MODE] ", subvol_rollback_src
            )
        )
    except FileNotFoundError as e:
        LOG.fatal(
            f"Missing {subvol_main}: Is {dev} mounted with the option subvolid=5?"
        )
    except btrfsutil.BtrfsUtilError as e:
        # Handle errors from btrfs utilities
        LOG.error("{e}")
        # Move old root back if btrfs utilities fail
        if not os.path.isdir(subvol_main):
            LOG.info(f"Moving {subvol_main_newname} back to {subvol_main}")
            if dry_run:
                LOG.warning("mv {} {}".format(subvol_main_newname, subvol_main))
            else:
                os.rename(subvol_main_newname, subvol_main)


def main():
    verify_migration()

    args = parse_args()
    config = read_config(args.config)

    mountpoint = pathlib.Path(config.get("root", "mountpoint"))
    subvol_main = mountpoint / config.get("root", "subvol_main")
    subvol_rollback_src = (
        mountpoint / config.get("root", "subvol_snapshots") / args.snap_id / "snapshot"
    )
    try:
        dev = config.get("root", "dev")
    except configparser.NoOptionError as e:
        dev = None

    confirm_typed_value = "CONFIRM"
    try:
        confirmation = input(
            f"Are you SURE you want to rollback? Type '{confirm_typed_value}' to continue: "
        )
        if confirmation != confirm_typed_value:
            LOG.fatal("Bad confirmation, exiting...")
            sys.exit(0)
    except KeyboardInterrupt as e:
        sys.exit(1)

    date = datetime.now().strftime("%Y-%m-%dT%H:%M")
    subvol_main_newname = pathlib.Path(f"{subvol_main}{date}")
    try:
        mount_subvol_id5(mountpoint, source=dev, dry_run=args.dry_run)
        rollback(
            subvol_main,
            subvol_main_newname,
            subvol_rollback_src,
            dev,
            dry_run=args.dry_run,
        )
    except PermissionError as e:
        LOG.fatal("Permission denied: {}".format(e))
        exit(1)


if __name__ == "__main__":
    main()
