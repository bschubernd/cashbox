#!/usr/bin/env python3

# cashbox.py
#
# Copyright:
#   Copyright (C) 2024-2025 Bernd Schumacher <bernd@bschu.de>
#
# License: GPL-3.0+
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   .
#   This package is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   .
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <https://www.gnu.org/licenses/>.
# Comment:
#   On Debian systems, the complete text of the GNU General
#   Public License version 3 can be found in
#   "/usr/share/common-licenses/GPL-3".

""" cashbox Application """

import sys
import os
import gi

dir1 = os.path.dirname(os.path.realpath(__file__))
dirp = os.path.basename(dir1)
dir2 = os.path.dirname(dir1)
if dirp == "bin":
    sys.path.append(os.path.join(dir2, 'share/cashbox/python3'))
if dirp == "decision":
    sys.path.append(dir2)

try:
    from cashbox.article import Sale
    from cashbox.sale_widget import SaleWidget
    from cashbox.view_switch_window import ViewSwitchWindow
    from cashbox.receipt_widget import ReceiptWidget
    from cashbox.app import App
    from cashbox.pricelist_widget import PricelistWidget
    from cashbox.read_appargs import appargs
    from cashbox.locale_utils import _
except ImportError as exc:
    print('Error: cashbox modules not found.', exc)
    sys.exit(1)

try:
    gi.require_version('Gtk', '4.0')
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import Gtk
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


class MyApp(App):
    """ cashbox App """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_child_name = None

        # sale
        self.sale = Sale()

        self.pricelist_widget = None

    def on_activate(self, app):
        win = ViewSwitchWindow(application=app)

        # PricelistWidget
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=12,
                      margin_end=12, margin_bottom=12, margin_start=12,
                      spacing=12)
        self.pricelist_widget = PricelistWidget(self.sale, win=win)
        box.append(self.pricelist_widget)
        win.stack.add_titled(box, "Pricelist", _("Pricelist"))

        if appargs.moreargs:
            self.pricelist_widget.read_files(appargs.moreargs)

        # SaleWidget
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=12,
                      margin_end=12, margin_bottom=12, margin_start=12,
                      spacing=12)
        win.stack.add_titled(box, "Sale", _("Sale"))
        sale_widget = SaleWidget(self.sale, win=win)
        box.append(sale_widget)

        # ReceiptWidget
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=12,
                      margin_end=12, margin_bottom=12, margin_start=12,
                      spacing=12)
        win.stack.add_titled(box, "Receipt", _("Receipt"))
        receipt_widget = ReceiptWidget(self.sale, win=win)
        box.append(receipt_widget)

        win.present()


myapp = MyApp()
myapp.run(sys.argv)
