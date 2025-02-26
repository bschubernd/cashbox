#!/usr/bin/python3

# read_appargs.py
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

""" read from gtk command line """

import sys
import os
import pathlib
from datetime import datetime
import gi

dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)

try:
    from cashbox.utils import err
except ImportError as exc:
    print('Error: cashbox modules not found.', exc)
    sys.exit(1)

try:
    gi.require_version('Gtk', '4.0')
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import GLib, Adw, Gio
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


class AttrDict(dict):
    """ access dictionary as attributes """
    application_id = "de.bschu.cashbox"
    application_version = "0.3.3"
    max_name_len = 40
    conf_suffix = ".cshbx"

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            # hasattr expects AttributeError instead of KeyError
            # (needed for doctest)
            classname = type(self).__name__
            msg = f'{repr(classname)} object has no attribute {repr(key)}'
            raise AttributeError(msg) from e

    def __setattr__(self, key, value):
        self[key] = value

    def __init__(self):
        """
        Set defaults for global variable "appargs".
        """
        # set default opts
        self.user_app_dir = os.path.join(GLib.get_user_data_dir(),
                                         self.application_id)
        self.system_app_dir = os.path.join("/", "usr", "share", "cashbox")
        self.css_path = os.path.join(self.system_app_dir, "cashbox.css")
        self.dark = None
        self.session = datetime.now().strftime('%Y-%m-%d')

        self.currency = "Dollar"
        self.test_small_display = False

    def read_appargs(self, opts, moreargs):
        """ get args from gnome """

        # set command_line opts
        for i in opts:
            self[i.translate({ord('-'): ord('_')})] = opts[i]

        # set command_line args
        self["moreargs"] = moreargs

        # do opts handling
        if self.currency == "Euro":
            self.update({"separator": ",", "symbol": "€", "digits": 2,
                         "cents": 10**2})
        elif self["currency"] == "Dollar":
            self.update({"separator": ".", "symbol": "$", "digits": 2,
                         "cents": 10**2})
        else:
            err(f"currency option <{appargs['currency']}> not Dollar or Euro")

        pathlib.Path(appargs.user_app_dir).mkdir(parents=True, exist_ok=True)


# init global variable appargs, to be included by other modules
if "appargs" not in globals():
    appargs = AttrDict()


if __name__ == '__main__':
    # to test try with option --help
    # to test try with option --number

    class App(Adw.Application):
        """ test class App """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, application_id="de.bschu.cashbox",
                             flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE |
                             Gio.ApplicationFlags.HANDLES_OPEN, **kwargs)

            self.connect('activate', self.on_activate)

            self.add_main_option("number", ord("n"), GLib.OptionFlags.NONE,
                                 GLib.OptionArg.INT, "Test number", None)

            self.set_option_context_parameter_string("MOREARGS")
            self.set_option_context_summary("More Args")
            self.set_option_context_description("More Args to be used in "
                                                "appargs.moreargs")

        def do_command_line(self, *args, **_kwargs):
            # To make pylint happy "*args" was used instead of "command_line".
            # Because "*args" was used, instead of "command_line", to have the
            # same argument list as parent class, the next 2 lines are needed
            assert len(args) == 1
            command_line = args[0]
            opts = command_line.get_options_dict().end().unpack()
            args = command_line.get_arguments()

            appargs.read_appargs(opts, args[1:])

            self.activate()
            return 0

        def on_activate(self, _app):
            """ start test window """
            for var, val in appargs.items():
                print(f"<{var}>=<{val}>")
            assert appargs.currency == "Dollar"

    myapp = App()
    myapp.run(sys.argv)
