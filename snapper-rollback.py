#!/usr/bin/env -S python3
# -*- coding: utf-8 -*-

"""
Script to rollback to snapper snapshot using the layout proposed in the snapper
archwiki page
https://wiki.archlinux.org/index.php/Snapper#Suggested_filesystem_layout
"""

from datetime import datetime
import xml.dom.minidom as minidom

import argparse
import btrfsutil
import configparser
import logging
import os
import pathlib
import sys


LOG = logging.getLogger()
LOG.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
LOG.addHandler(ch)


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

def generateXML(fileName,type,num,date,description,cleanup,dry_run=False) :

  #root = xmltree.Element("snapshot")
  info = minidom.parseString("""<?xml version="1.0"?>
  <snapshot/>""")
  root = info.documentElement
  
  xml_type = info.createElement("type")
  xml_type.appendChild(info.createTextNode(type))
  root.appendChild(xml_type)

  xml_num = info.createElement("num")
  xml_num.appendChild(info.createTextNode(num))
  root.appendChild(xml_num)

  xml_date = info.createElement("date")
  xml_date.appendChild(info.createTextNode(date))
  root.appendChild(xml_date)

  xml_description = info.createElement("description")
  xml_description.appendChild(info.createTextNode(description))
  root.appendChild(xml_description)

  xml_cleanup = info.createElement("cleanup")
  xml_cleanup.appendChild(info.createTextNode(cleanup))
  root.appendChild(xml_cleanup)

  if dry_run:
    LOG.info("Writing xml to {}".format(fileName))
  else:
    file = open(fileName, "w")
    file.write(info.toprettyxml(indent="  "))
    file.close

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
    Rename linux root subvolume, then create a snapshot of the subvolume to
    the old linux root location
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
        # Restore old linux root if btrfs utilities fail
        if not os.path.isdir(subvol_main):
            LOG.info(f"Moving {subvol_main_newname} back to {subvol_main}")
            if dry_run:
                LOG.warning("mv {} {}".format(subvol_main_newname, subvol_main))
            else:
                os.rename(subvol_main_newname, subvol_main)

def getNextSubvolumeNumber(mountpoint,config,dry_run=False):
  if dry_run: 
    subvol_main_snapshot_number = "<next_snapshot_number>"
  else:
    subvol_main_snapshot_number = str(int(os.listdir(path= 
                                               mountpoint / config.get("root", "subvol_snapshots")
                                               )[-1])+1
                                )
  return subvol_main_snapshot_number

def createNextSubvolumeNumber(mountpoint,config,dest,dry_run=False):
  if dry_run: 
    LOG.info("Creating directory at {}".format(mountpoint / config.get("root", "subvol_snapshots") / dest))
  else:
    os.mkdir(mountpoint / config.get("root", "subvol_snapshots") / dest )


def main():
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
    subvol_main_newname = pathlib.Path(f"{subvol_main}")
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        mount_subvol_id5(mountpoint, source=dev, dry_run=args.dry_run)
        
        subvol_main_snapshot_number = getNextSubvolumeNumber(mountpoint,config,args.dry_run)
        subvol_rollback_dir = (
                mountpoint / config.get("root", "subvol_snapshots") / subvol_main_snapshot_number
                )
        subvol_main_dst = (
            subvol_rollback_dir / "snapshot"
        )
        createNextSubvolumeNumber(mountpoint,config,subvol_rollback_dir,args.dry_run)
        rollback(
            subvol_main,
            subvol_main_dst,
            subvol_rollback_src,
            dev,
            dry_run=args.dry_run,
        )
        generateXML(subvol_rollback_dir / "info.xml", "single", subvol_main_snapshot_number, date, "snapper-rollback", "number", args.dry_run)
    except PermissionError as e:
        LOG.fatal("Permission denied: {}".format(e))
        exit(1)


if __name__ == "__main__":
    main()
