pkgname=snapper-rollback
pkgver=1.0
pkgrel=1
pkgdesc='Script to rollback to snapper snapshot using the layout proposed in the snapper arch wiki page https://wiki.archlinux.org/index.php/Snapper#Suggested_filesystem_layout'
arch=('any')
license=('GPL3')
url='https://github.com/jrabinow/snapper-rollback'
depends=('coreutils' 'python' 'btrfs-progs')
provides=('snapper-rollback')
conflicts=('rollback-git')
backup=(etc/snapper-rollback.conf)
source=('snapper-rollback.py' 'snapper-rollback.conf')
sha256sums=('af91e983ead5fb5196274114e580bd42385423ddc7653166e288f8f877486348'
            '71b9aebb4f75cd3a26a022aca486b18901ad2bfb5361cd4c07bab8349918256d')

package() {
    install -Dm644  "snapper-rollback.conf" -t "$pkgdir/etc/"
    install -Dm755  "snapper-rollback.py" "$pkgdir/usr/bin/snapper-rollback"
}
