# Snapper-Rollback

Python script to rollback BTRFS systems using the [ArchWiki suggested subvolume layout](https://wiki.archlinux.org/index.php/Snapper#Suggested_filesystem_layout)

## Installation
### ArchLinux
Install through the AUR, or download the [PKGBUILD file](https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=snapper-rollback) and run `makepkg -sri` while in the same directory

### Other
```
git clone 'https://github.com/jrabinow/snapper-rollback.git'
cd snapper-rollback
sudo cp snapper-rollback.py /usr/local/sbin/snapper-rollback
sudo cp snapper-rollback.conf /etc/
```

## Config file
Edit `/etc/snapper-rollback.conf` and make sure all the settings have the right
values. You don't have to do this, but if you don't, you'll have to manually
mount your btrfs root subvolume to `/btrfsroot` before running the script.

## Usage
```
usage: snapper-rollback.py [-h] [--dry-run] [-c CONFIG] SNAPID

Rollback to snapper snapshot based on snapshot ID

positional arguments:
  SNAPID                ID of snapper snapshot

optional arguments:
  -h, --help            show this help message and exit
  --dry-run             don't actually do anything, just print the actions out
  -c CONFIG, --config CONFIG
                        configuration file to use (default: /etc/snapper-
                        rollback.conf)
```

### Example usage
```
$ snapper list
 # | Type   | Pre # | Date                            | User | Cleanup  | Description  | Userdata
 ---+--------+-------+---------------------------------+------+----------+--------------+---------------------
 0  | single |       |                                 | root |          | current      |
 1  | single |       | Mon 19 Jul 2021 08:59:01 PM PDT | root |          | base_install |
 2  | single |       | Fri 30 Jul 2021 10:00:08 PM PDT | root | timeline | timeline     |
 3  | single |       | Fri 30 Jul 2021 11:00:08 PM PDT | root | timeline | timeline     |
$ snapper-rollback 1        # let's revert back to the snapshot whos description is `base_install`
Are you SURE you want to rollback? Type 'CONFIRM' to continue: CONFIRM
2021-10-17 23:25:47,889 - INFO - Rollback to /btrfsroot/@snapshots/1/snapshot complete. Reboot to finish
```

## Credits
[@GabTheBab](https://github.com/GabTheBab) for creating the first iteration of this script and for sharing it on the AUR.  
Original repo here: https://gitlab.freedesktop.org/Gabby/rollback
