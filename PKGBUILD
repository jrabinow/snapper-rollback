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
install=snapper-rollback.install
source=('snapper-rollback.py' 'snapper-rollback.conf')
sha256sums=('b855063200079889c67865445700dd99d76b17f90b2396754cea2adf68d9ba9b'
            '71b9aebb4f75cd3a26a022aca486b18901ad2bfb5361cd4c07bab8349918256d')

package() {
    install -Dm644  "snapper-rollback.conf" -t "$pkgdir/etc/"
    install -Dm755  "snapper-rollback.py" "$pkgdir/usr/bin/snapper-rollback"
}
