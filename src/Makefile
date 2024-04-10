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

all: $(UIS)

clean:

install: install-libs install-bin

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

%.ui : %.blp
	blueprint-compiler compile $< >$@
