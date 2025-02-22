#!/usr/bin/env python3

# cashbox.py
#
# Copyright:
#   Copyright (C) 2024 Bernd Schumacher <bernd@bschu.de>
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
#   Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".

import sys, gi, os
gi.require_version('Gtk', '4.0')
gi.require_version(namespace='Adw', version='1')
from gi.repository import Gtk

dir1 = os.path.dirname(os.path.realpath(__file__))
dirp = os.path.basename(dir1)
dir2 = os.path.dirname(dir1)
if dirp == "bin":
    sys.path.append(os.path.join(dir2, 'share/cashbox/python3'))
if dirp == "decision":
    sys.path.append(dir2)

from cashbox.pick_widget import PickWidget
from cashbox.article import Article, Sale
from cashbox.sale_widget import SaleWidget
from cashbox.view_switch_window import ViewSwitchWindow
from cashbox.receipt_widget import ReceiptWidget
from cashbox.read_css import read_css
from cashbox.app import App, MinWindow
from cashbox.file_widget import FileWidget
from cashbox.pricelist_widget import PricelistWidget
from cashbox.dialog_widget import DialogWidget
from cashbox.read_appargs import read_appargs, appargs
from cashbox.locale_utils import _, f

class MyApp(App):

    def on_activate(self, app):
        win = ViewSwitchWindow(application=app)

        # sale
        self.last_child_name=None
        self.sale = Sale()

        # PricelistWidget
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=12,
                    margin_end=12, margin_bottom=12,margin_start=12,spacing=12)
        self.pricelist_widget = PricelistWidget(self.sale, win=win)
        box.append(self.pricelist_widget)
        win.stack.add_titled(box, "Pricelist", _("Pricelist"))

        if appargs.moreargs:
            self.pricelist_widget.read_files(appargs.moreargs)

        # SaleWidget
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=12,
                    margin_end=12, margin_bottom=12,margin_start=12,spacing=12)
        win.stack.add_titled(box, "Sale", _("Sale"))
        sale_widget = SaleWidget(self.sale, win=win)
        box.append(sale_widget)

        # ReceiptWidget
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=12,
                    margin_end=12, margin_bottom=12,margin_start=12,spacing=12)
        win.stack.add_titled(box, "Receipt", _("Receipt"))
        receipt_widget = ReceiptWidget(self.sale, win=win)
        box.append(receipt_widget)

        win.present()

app = MyApp()
app.run(sys.argv)
