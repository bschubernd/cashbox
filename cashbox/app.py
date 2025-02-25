#!/usr/bin/python3

# app.py
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

""" app.py features:
 * defines classes MinWindow and App
 * starts GTK4 main window of decision
 * starts tests of python files imported by decision
 * unifies the start of an applicaton
 * provides global variables glo.app, glo.version and glo.application_id
   * provides the current version of decision in App.version
   * allows to start decision multiple times with different app.application_id
   * allows to calculate win with App.app.get_active_window()
 * can reduce the window_size to simulate librem5 on desktop
 * allows caller to have less code
 * enables commandline usage provided by appargs.py
"""

import sys
import os
import gi

dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)

try:
    from cashbox.utils import reduce_window_size, create_action
    from cashbox.read_appargs import appargs
    from cashbox.read_css import read_css
    from cashbox.dialog_widget import DialogWidget
    from cashbox.locale_utils import _, f
except ImportError as exc:
    print('Error: cashbox modules not found.', exc)
    sys.exit(1)

try:
    gi.require_version('Gtk', '4.0')
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import Adw, Gtk, Gio, GLib
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


class MinWindow(Adw.ApplicationWindow):
    """ class MinWindow usage:
    * without class MinWindow:
       0  class MyMainWindow(Adw.ApplicationWindow):
    * with class App:
       0  class MyMainWindow(MinWindow):
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(appargs, "t1") and appargs.t1:
            reduce_window_size(self)


class App(Adw.Application):
    """ class App usage:
    * without class App:
       0  class MyApp(Adw.Application):
       1
       2      def __init__(self, *args, **kwargs):
       3          super().__init__(*args,
       4                           application_id="org.gtk.example",
       5                           **kwargs)
       6          self.connect('activate', self.on_activate)
       7
       8      def on_activate(self, app):
       9          win = MyMainWindow(application=app)
      10          win.present()
      11
      12  app = MyApp()
      13  app.run(sys.argv)
    * with class App:
       0  class MyApp(App):
       1
       2      def on_activate(self, app):
       3          self.win = MyMainWindow(application=app)
       4          self.win.present()
       5
       6  app = MyApp()
       7  app.run(sys.argv)
    * to provide appargs without starting a window
       0  App().run(sys.argv)
    * to calculate win:
       0  win = App.app.get_active_window()
    """

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
        self.set_option_context_description("the price list FILE should "
                                            "contain lines with an article "
                                            "name followed by a price")

    def on_activate(self, app):
        """ this will normally be overwritten """

    def do_command_line(self, *args, **_kwargs):
        """ use gnome command line """
        # To make pylint happy "*args" was used instead of "command_line".
        # Because "*args" was used, instead of "command_line", to have the
        # same argument list as parent class, the next 2 lines are needed
        assert len(args) == 1
        command_line = args[0]

        opts = command_line.get_options_dict().end().unpack()
        args = command_line.get_arguments()

        appargs.read_appargs(opts, args[1:])
        read_css()

        if hasattr(appargs, "version") and appargs.version:
            print(appargs.application_version)
            sys.exit(0)

        self.activate()
        return 0

    def about_action(self, _action, _param):
        """ show cashbox's about dialog """
        d = DialogWidget()
        win = self.get_active_window()
        d.about_dialog(win, f(_("""\
{d.C} memorises the cost of {d.as_} and calculates the total price and \
change. It is intended for small clubs on a celebration, where members are \
not experienced in memorizing prices and doing mental arithmetic.

{d.C} consists of the 3 windows {d.Pl}, {d.S} and {d.R}, that can be switched \
as needed. {d.Pl} can add, delete or modify {d.as_}, {d.S} picks {d.as_} to \
sell and {d.R} shows the total price of the choosen {d.as_}.""")),
                       version=appargs.application_version)


if __name__ == '__main__':

    class MyMainWindow(MinWindow):
        """ test class MinWindow """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            box = Gtk.Box()
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

            for i, j in appargs.items():
                print(f"<{i}>=<{j}>")

        def clicked(self, _button):
            """ print something to test button """
            print("clicked")

    class MyApp(App):
        """ test class App """

        def on_activate(self, app):
            """ start test window """
            win = MyMainWindow(application=app)
            win.present()

    myapp = MyApp()
    myapp.run(sys.argv)
