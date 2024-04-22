#!/usr/bin/python3

# file_widget.py
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

import os, sys, re, gi
gi.require_version(namespace='Adw', version='1')
from gi.repository import Adw, Gtk
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)
from cashbox.utils import eprint
from cashbox.article import Article, Sale
from cashbox.drop_down_widget import DropDownWidget
from cashbox.read_css import read_css
from cashbox.read_appargs import read_appargs, appargs

@Gtk.Template(filename='%s/file_widget.ui' % dir1)
class FileWidget(Gtk.Box):
    __gtype_name__ = 'FileWidget'
    file_dialog = Gtk.Template.Child()

    def __init__(self, sale, **kwargs):
        super().__init__(**kwargs)
        self.sale=sale

    @Gtk.Template.Callback()
    def on_load(self, button):
        self.file_dialog.open(None, None, self.load_callback)

    def load_callback(self, gtk_file_dialog, g_task):
        g_local_file=gtk_file_dialog.open_finish(g_task)
        with open(g_local_file.get_path(), 'r') as file:
            data = file.read()

    @Gtk.Template.Callback()
    def on_save(self, button):
        self.file_dialog.save(None, None, self.save_callback)

    def save_callback(self, gtk_file_dialog, g_task):
        g_local_file=gtk_file_dialog.save_finish(g_task)
        with open(g_local_file.get_path(), 'w') as file:
            file.write(self.sale.text())

if __name__ == '__main__':
    import sys, doctest
    from app import App, MinWindow

    class FileWindow(MinWindow):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            sale = Sale()

            article = [("Banana", 1.10, 1), ("Apple", 2.0, 0)]
            for f in article:
                sale.main_list.append(Article( f[0], f[1], f[2] ))

            file_widget = FileWidget(sale)
            self.set_content(file_widget)

    class MyApp(App):

        def on_activate(self, app):
            self.win = FileWindow(application=app)
            self.win.present()

    app = MyApp()
    app.run(sys.argv)
