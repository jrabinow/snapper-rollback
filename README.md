# Snapper-Rollback

Python  script to rollback BTRFS systems using the subvolume layout specified here: https://wiki.archlinux.org/index.php/Snapper#Suggested_filesystem_layout

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

# Credits
@GabTheBab for creating the first iteration of this script and for sharing it on the AUR.
Original repo here: https://gitlab.freedesktop.org/Gabby/rollback/-/blob/master/rollback
