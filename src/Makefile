#        file: Makefile
#   copyright: Bernd Schumacher <bernd@bschu.de> (2024)
#     license: GNU General Public License, version 3
# description: build cashbox package

LIBS   = $(shell ls *py | grep -v cashbox.py)
UIS    = $(shell ls *blp | sed -e "s/blp$$/ui/")
SHARE  = $(DESTDIR)/usr/share/cashbox
PYTHON = $(DESTDIR)/usr/share/cashbox/python3/cashbox
BIN    = $(DESTDIR)/usr/bin
APPL   = $(DESTDIR)/usr/share/applications
SVG    = $(DESTDIR)/usr/share/icons/hicolor/scalable/apps
MIME   = $(DESTDIR)/usr/share/mime/packages
MODIR  = $(DESTDIR)/usr/share/locale
MO     = de
UTF    = "de_DE.UTF-8 us_US.UTF-8"
MO1	   = $(shell for i in $(MO); do echo "$${i}/LC_MESSAGES/cashbox.mo"; done)
MO2	   = $(shell for i in $(MO1); do echo "po/locale/$${i}"; done)


all: $(UIS) $(MO2)

clean:

install: install-libs install-bin install-mo

install-libs: $(LIBS) $(UIS)
	@mkdir -p $(PYTHON); \
	for i in $^; do \
	    install -o root -g root -m 0644 $$i $(PYTHON)/; \
	done

install-bin: cashbox.py
	@mkdir -p $(BIN) $(APPL) $(SVG) $(MIME) $(SHARE)
	@install -o root -g root -m 0755 cashbox.py $(BIN)/cashbox
	@install -o root -g root -m 0644 de.bschu.cashbox.desktop $(APPL)
	@install -o root -g root -m 0644 de.bschu.cashbox.svg $(SVG)
	@install -o root -g root -m 0644 cashbox.xml $(MIME)
	@install -o root -g root -m 0644 cashbox.css $(SHARE)

install-mo: $(MO2)
	@for i in $(MO1); do \
	   mkdir -p $$(dirname $(MODIR)/$${i}); \
	   install -o root -g root -m 0644 po/locale/$${i} $(MODIR)/$${i}; \
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
