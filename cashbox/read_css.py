#!/usr/bin/python3

# read_css.py
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

""" read_css.py reads .css file """

import sys
import os
import gi

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

if __name__ == '__main__':
    from cashbox.app import App

try:
    from cashbox.read_appargs import appargs
except ImportError as exc:
    print('Error: cashbox modules not found.', exc)
    sys.exit(1)

try:
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Adw, Gtk, Gdk
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


def read_css():
    """ reads .css file """
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(appargs.css_path)

    styleContext = Gtk.StyleContext
    display = Gdk.Display.get_default()
    styleContext.add_provider_for_display(display, css_provider,
                                          Gtk.STYLE_PROVIDER_PRIORITY_USER)


if __name__ == '__main__':

    # test button
    #   should change color of label to red -
    #   defined in cashbox.css as "#invalid"
    HINT = """
Hint: to see color of label change, when pressing the button, run:

cat <<END >/tmp/read_css.css
#invalid {
  background: @error_color;
}
END
./read_css.py --css-path /tmp/read_css.css
"""

    print(HINT)

    class CssWindow(Adw.Window):
        """ test window using .css file """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            box = Gtk.Box()
            self.set_content(box)

            button = Gtk.Button(label="button")
            box.append(button)

            label = Gtk.Label(label="label")
            box.append(label)

            button.connect('clicked', self.clicked, label)

            for i, j in appargs.items():
                print(f"<{i}>=<{j}>")

        def clicked(self, _button, label):
            """ test calback for button """
            if label.get_name() == "invalid":
                label.set_name("normal")
            else:
                label.set_name("invalid")

    class MyApp(App):
        """ test class App """

        def on_activate(self, app):
            """ start test window """
            win = CssWindow(application=app)
            win.present()

    myapp = MyApp()
    myapp.run(sys.argv)
