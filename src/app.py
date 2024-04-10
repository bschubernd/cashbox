#!/usr/bin/python3

# app.py - start cashbox application and handle command-line opptions
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
from gi.repository import Adw, Gtk, Gio, GLib, GObject
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)
from cashbox.utils import err, reduce_window_size
from cashbox.read_appargs import read_appargs, appargs
from cashbox.read_css import read_css

class MinWindow(Adw.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(appargs, "t1") and appargs.t1:
            print("MinWindow: t1")
            reduce_window_size(self)

class App(Adw.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id=appargs.application_id,
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE |
                         Gio.ApplicationFlags.HANDLES_OPEN, **kwargs)

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

if __name__ == '__main__':
    import sys
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, Adw

    from app import App, MinWindow

    class MyMainWindow(MinWindow):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            button = Gtk.Button(label="click me")
            self.set_content(button)
            button.connect('clicked', self.clicked)

            print("main appargs.digits=<%s>" % appargs.digits)

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
