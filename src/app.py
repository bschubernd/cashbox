#!/usr/bin/python3

# app.py
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
from gi.repository import Adw, Gtk, Gio, GLib
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)
from cashbox.utils import reduce_window_size, create_action
from cashbox.read_appargs import read_appargs, appargs
from cashbox.read_css import read_css
from cashbox.dialog_widget import DialogWidget
from cashbox.locale_utils import _, f

class MinWindow(Adw.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(appargs, "t1") and appargs.t1:
            reduce_window_size(self)

class App(Adw.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id=appargs.application_id,
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE |
                         Gio.ApplicationFlags.HANDLES_OPEN, **kwargs)

        application = self
        create_action(application, "about", self.about_action)

        self.connect('activate', self.on_activate)

        self.add_main_option("t1", 0, GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "test_small_display", None)

        self.add_main_option("currency", ord("c"), GLib.OptionFlags.NONE,
                             GLib.OptionArg.STRING, "Euro or Dollar", None)

        self.add_main_option("css-path", 0, GLib.OptionFlags.NONE,
                             GLib.OptionArg.STRING, "Path to css file", None)

        # -v is alredy used by doctests
        self.add_main_option("version", 0, GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "say version", None)

        self.set_option_context_parameter_string("FILE")
        self.set_option_context_summary("price list FILE")
        self.set_option_context_description("the price list FILE should contain lines " +
                                            "with a article name followed by a price")

    def do_command_line(self, command_line):
        opts = command_line.get_options_dict().end().unpack()
        args = command_line.get_arguments()

        read_appargs(opts, args[1:])
        read_css()

        if hasattr(appargs, "version") and appargs.version:
            print(appargs.application_version)
            sys.exit(0)

        self.activate()
        return 0

    def about_action(self, action, param):
        d = DialogWidget()
        win=self.get_active_window()
        d.about_dialog(win, f(_("""\
{d.C} memorises the cost of {d.as_} and calculates the total price and \
change. It is intended for small clubs on a celebration, where members are \
not experienced in memorizing prices and doing mental arithmetic.

{d.C} consists of the 3 windows {d.Pl}, {d.S} and {d.R}, that can be switched \
as needed. {d.Pl} can add, delete or modify {d.as_}, {d.S} picks {d.as_} to \
sell and {d.R} shows the total price of the choosen {d.as_}.""")),
            version=appargs.application_version)

if __name__ == '__main__':
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, Adw

    class MyMainWindow(MinWindow):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            box= Gtk.Box()
            self.set_content(box)

            hamburger = Gtk.MenuButton()
            hamburger.set_icon_name("open-menu-symbolic")
            box.append(hamburger)

            popover = Gtk.PopoverMenu()
            hamburger.set_popover(popover)

            menu = Gio.Menu.new()
            menu.append("Show About Dialog", "app.about")
            popover.set_menu_model(menu)

            button = Gtk.Button(label="click me")
            box.append(button)
            button.connect('clicked', self.clicked)

            print(f"main appargs.digits=<{appargs.digits}>")

            for i in appargs.keys():
                print(f"<{i}>=<{appargs[i]}>")

        def clicked(self, button):
            print("clicked")

    class MyApp(App):

        def on_activate(self, app):
            win = MyMainWindow(application=app)
            win.present()

    app = MyApp()
    app.run(sys.argv)
