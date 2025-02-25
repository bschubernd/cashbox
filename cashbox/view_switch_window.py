#!/usr/bin/python3

# view_switch_window.py
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

"""
switch between main windows in cashbox application
"""

import sys
import os
import gi
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)

try:
    from cashbox.app import App
    from cashbox.utils import reduce_window_size
    from cashbox.read_appargs import appargs
except ImportError as exc:
    print('Error: decision modules not found.', exc)
    sys.exit(1)

try:
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import Adw, Gtk
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


@Gtk.Template(filename=f"{dir1}/view_switch_window.ui")
class ViewSwitchWindow(Adw.ApplicationWindow):
    """ customized Adw.ViewStack """
    __gtype_name__ = 'ViewSwitchWindow'
    stack = Gtk.Template.Child()  # Adw.ViewStack

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # because MinWindow is not known in view_switch_window.blp
        # ViewSwitchWindow(MinWindow) is not possible
        # and the next 2 lines have been copied from MinWindow
        if hasattr(appargs, "t1") and appargs.t1:
            reduce_window_size(self)


if __name__ == '__main__':
    # not possible:
    #   class MyViewSwitchWindow(ViewSwitchWindow):
    # because:
    #   TypeError: Inheritance from classes with @Gtk.Template decorators
    #   is not allowed at this time

    class MyApp(App):
        """ test class App """

        def on_visible_child_name(self, stack, _):
            """ test message if Window switches """
            print(f"on_visible_child_name: <{stack.get_visible_child_name()}>")

        def on_activate(self, app):
            """ start test window """
            win = ViewSwitchWindow(application=app)
            win.stack.connect('notify::visible-child-name',
                              self.on_visible_child_name)
            for i in [1, 2, 3]:
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                              margin_top=12, margin_end=12, margin_bottom=12,
                              margin_start=12, spacing=12)
                win.stack.add_titled(box, f"name-{i}", f"Title {i}")

                lbl = Gtk.Label(label="Label {i}")
                box.append(lbl)
            win.present()

    myapp = MyApp()
    myapp.run(sys.argv)
