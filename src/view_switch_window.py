#!/usr/bin/python3

# view_switch_window.py - handle Adw.ViewStack for cashbox
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

import gi, os, sys
gi.require_version(namespace='Adw', version='1')
from gi.repository import Adw, Gtk
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)
from cashbox.app import App
from cashbox.utils import print_widget, reduce_window_size
from cashbox.read_appargs import read_appargs, appargs

@Gtk.Template(filename=f"{dir1}/view_switch_window.ui")
class ViewSwitchWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ViewSwitchWindow'
    stack = Gtk.Template.Child() # Adw.ViewStack

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # because MinWindow is not known in view_switch_window.blp
        # ViewSwitchWindow(MinWindow) is not possible
        # and the next 2 lines have been copied from MinWindow
        if hasattr(appargs, "t1") and appargs.t1:
            reduce_window_size(self)

if __name__ == '__main__':
    import sys

    # not possible:
    #   class MyViewSwitchWindow(ViewSwitchWindow):
    # because:
    #   TypeError: Inheritance from classes with @Gtk.Template decorators is not allowed at this time

    class MyApp(App):

        def on_visible_child_name(self, stack, b):
            print("on_visible_child_name: <%s>" % (stack.get_visible_child_name()))

        def on_activate(self, app):
            win = ViewSwitchWindow(application=app)
            win.stack.connect('notify::visible-child-name', self.on_visible_child_name)
            for i in [1,2,3]:
                box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=12,
                            margin_end=12, margin_bottom=12,margin_start=12,spacing=12)
                win.stack.add_titled(box, "name-%s"%i, "Title %s"%i)

                l=Gtk.Label(label="Label %s"%i)
                box.append(l)
            win.present()

    app = MyApp()
    app.run(sys.argv)
