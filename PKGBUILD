pkgname=rollback
pkgver=1.0
pkgrel=1
pkgdesc='Script to rollback to snapper snapshot using the layout proposed in the snapper arch wiki page https://wiki.archlinux.org/index.php/Snapper#Suggested_filesystem_layout'
arch=('any')
license=('GPL3')
url='https://github.com/jrabinow/rollback'
depends=('coreutils' 'python' 'btrfs-progs')
provides=('rollback')
conflicts=('rollback-git')
backup=(etc/rollback.conf)
source=('rollback' 'rollback.conf')
md5sums=('SKIP' 'SKIP')

package() {
    install -Dm644  "rollback.conf" -t "$pkgdir/etc/"
    install -Dm755  "rollback" -t "$pkgdir/usr/bin/"
}

