#!/usr/bin/python3

# read_css.py
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

import sys, os

import gi
gi.require_version(namespace='Adw', version='1')
gi.require_version(namespace='Adw', version='1')
from gi.repository import Adw, Gtk, Gdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from cashbox.read_appargs import read_appargs, appargs

def read_css():

    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(appargs.csspath)

    styleContext = Gtk.StyleContext
    display=Gdk.Display.get_default()
    styleContext.add_provider_for_display(display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

if __name__ == '__main__':

    # test button
    #   should change color of label to red - defined in cashbox.css as "#invalid"

    gi.require_version(namespace='Adw', version='1')
    from gi.repository import Adw, Gtk
    from app import App

    class CssWindow(Adw.Window):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            box = Gtk.Box()
            self.set_content(box)

            button = Gtk.Button(label="button")
            box.append(button)

            label = Gtk.Label(label="label")
            box.append(label)

            button.connect('clicked', self.clicked, label)

        def clicked(self, _button, label):
            if label.get_name()=="invalid":
                label.set_name("normal")
            else:
                label.set_name("invalid")

    class MyApp(App):

        def on_activate(self, app):
            self.win = CssWindow(application=app)
            self.win.present()

    app = MyApp()
    app.run(sys.argv)
