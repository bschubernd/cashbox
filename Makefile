#        file: Makefile
#   copyright: Bernd Schumacher <bernd@bschu.de> (2024)
#     license: GNU General Public License, version 3
# description: build cashbox package

ROOT    = $(shell [ "$(FLATPAK_DEST)" ] && echo $(shell whoami) || echo root)
USR     = $(shell [ "$(FLATPAK_DEST)" ] && echo $(FLATPAK_DEST) || echo /usr)
LIBS    = $(shell ls *py | grep -v cashbox.py)
UIS     = $(shell ls *blp | sed -e "s/blp$$/ui/")
SHARE   = $(DESTDIR)$(USR)/share/cashbox
PYTHON  = $(DESTDIR)$(USR)/share/cashbox/python3/cashbox
BIN     = $(DESTDIR)$(USR)/bin
APPL    = $(DESTDIR)$(USR)/share/applications
SVG     = $(DESTDIR)$(USR)/share/icons/hicolor/scalable/apps
MIME    = $(DESTDIR)$(USR)/share/mime/packages
MODIR   = $(DESTDIR)$(USR)/share/locale
MO      = de
UTF     = "de_DE.UTF-8 us_US.UTF-8"
MO1	= $(shell for i in $(MO); do echo "$${i}/LC_MESSAGES/cashbox.mo"; done)
MO2	= $(shell for i in $(MO1); do echo "po/locale/$${i}"; done)
META    = $(DESTDIR)$(USR)/share/metainfo
VERSION_BIN = ${shell sed -E -n -e "s/.*application_version.*= \"(\S+)\"$$/\1/p" read_appargs.py}
VERSION_DEB = ${shell head -1 debian/changelog | sed "s/.*(//" | sed "s/).*//"}
VERSION_FLATPAK = ${shell sed -E -n -e "s/^ *<release version=\"(\S+)\".*/\1/p" de.bschu.cashbox.metainfo.xml}

all: check_version $(UIS) $(MO2)

dbg:
	@echo "USR=<$(USR)> VERSION_BIN=<$(VERSION_BIN)> \
VERSION_DEB=<$(VERSION_DEB)> VERSION_FLATPAK=<$(VERSION_FLATPAK)>"

check_version:
ifneq ($(VERSION_BIN),$(VERSION_DEB))
	@echo "VERSION_BIN=<$(VERSION_BIN)> != VERSION_DEB=<$(VERSION_DEB)>"
	@exit 1
endif
ifneq ($(VERSION_FLATPAK),$(VERSION_DEB))
	@echo "VERSION_FLATPAK=<$(VERSION_FLATPAK)> != VERSION_DEB=<$(VERSION_DEB)>"
	@exit 1
endif

clean:

install: install-libs install-bin install-mo

install-libs: $(LIBS) $(UIS)
	@mkdir -p $(PYTHON); \
	for i in $^; do \
	    install -o $(ROOT) -g $(ROOT) -m 0644 $$i $(PYTHON)/; \
	done

install-bin: cashbox.py
	@mkdir -p $(BIN) $(APPL) $(SVG) $(MIME) $(SHARE) $(META)
	@install -o $(ROOT) -g $(ROOT) -m 0755 cashbox.py $(BIN)/cashbox
	@install -o $(ROOT) -g $(ROOT) -m 0644 de.bschu.cashbox.desktop $(APPL)
	@install -o $(ROOT) -g $(ROOT) -m 0644 de.bschu.cashbox.svg $(SVG)
	@install -o $(ROOT) -g $(ROOT) -m 0644 de.bschu.cashbox.xml $(MIME)
	@install -o $(ROOT) -g $(ROOT) -m 0644 cashbox.css $(SHARE)
	@install -o $(ROOT) -g $(ROOT) -m 0644 de.bschu.cashbox.metainfo.xml $(META)

install-mo: $(MO2)
	@for i in $(MO1); do \
	   mkdir -p $$(dirname $(MODIR)/$${i}); \
	   install -o $(ROOT) -g $(ROOT) -m 0644 po/locale/$${i} $(MODIR)/$${i}; \
	done

po/cashbox.pot: cashbox.py $(LIBS) $(UIS)
	@mkdir -p po
	@echo $^ | tr " " "\n" | xgettext --output=po/cashbox.pot -f -

po/de.po: po/cashbox.pot
	@l="$$(basename "$@" .po)"; \
	u="$$(echo " $(UTF) " | tr " " "\n" | grep "^$${l}")"; \
	[ -f $@ ] && msgmerge -o $@.new $@ $< || msginit -i $< -o $@ -l de_DE.UTF-8; \
	[ -f $@.new ] && mv $@.new $@

po/locale/%/LC_MESSAGES/cashbox.mo: po/%.po
	mkdir -p $$(dirname $@)
	msgfmt $< -o $@

p: $(UIS)
	mkdir -p po
	#xgettext --files-from=po/POTFILES --output=po/cashbox.pot
	mkdir -p po/locale/de/LC_MESSAGES
	msgfmt po/de.po -o po/locale/de/LC_MESSAGES/cashbox.mo

# temporarily disabled: (see changelog 0.3.1)
# %.ui : %.blp
#	blueprint-compiler compile $< >$@
