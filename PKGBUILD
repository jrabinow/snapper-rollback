pkgname=rollback
pkgver=1.0
pkgrel=1
pkgdesc='Script to rollback to snapper snapshot using the layout proposed in the snapper arch wiki page https://wiki.archlinux.org/index.php/Snapper#Suggested_filesystem_layout'
arch=('any')
license=('GPL3')
depends=('bash' 'coreutils' 'python')
optdepends=('doas: Automatic priv escalation'
            'sudo: Automatic priv escalation'
)
provides=('rollback')
conflicts=('rollback')
source=("$pkgname" "$pkgname.conf")
md5sums=('97791303b770ceb178aaf87785e9d1c8'
         '7661b5047b5a5ae2bb85283416544fe8')

package() {
    install -Dm644  "$pkgname.conf" -t "$pkgdir/etc/"
    install -Dm755  "$pkgname" -t "$pkgdir/usr/bin/"
}

