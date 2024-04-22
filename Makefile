VERSION_BIN = ${shell sed -E -n -e "s/.*application_version.*= \"(\S+)\"$$/\1/p" src/read_appargs.py}
VERSION_DEB = ${shell head -1 src/debian/changelog | sed "s/.*(//" | sed "s/).*//"}

all	: check_version cashbox_*.deb

check_version:
ifneq ($(VERSION_BIN),$(VERSION_DEB))
	@echo "VERSION_BIN=<$(VERSION_BIN)> != VERSION_DEB=<$(VERSION_DEB)>"
	@exit 1
endif

cashbox_*.deb	: \
	Makefile \
	src/cashbox \
	src/Makefile \
	src/debian/rules
	@if [ $(USER) = "root" ]; then echo "Makefile: do not run as root"; exit 1; fi
	#(cd src; debuild -- clean binary)
	(cd src; debuild --lintian-opts -i -- binary)

clean	:
	@(cd src; debuild -- clean)
	@rm -f cashbox_*.dsc
	@rm -f cashbox_*.tar.gz
	@rm -f cashbox_*.tar.xz
	@rm -f cashbox_*.build
	@rm -f cashbox_*.buildinfo
	@rm -f cashbox_*.changes

clobber : clean
	@rm -f cashbox_*.deb

install	: /var/lib/dpkg/info/cashbox.list

/var/lib/dpkg/info/cashbox.list: cashbox_*.deb
	@sudo dpkg --force-confmiss -i cashbox_*.deb
