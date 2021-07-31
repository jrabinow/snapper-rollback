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
backup=(etc/snapper/snapper-rollback.conf)
source=('snapper-rollback' 'snapper-rollback.conf')
md5sums=('SKIP' 'SKIP')

package() {
    install -Dm644  "snapper-rollback.conf" -t "$pkgdir/etc/snapper/"
    install -Dm755  "snapper-rollback" -t "$pkgdir/usr/bin/"
}

