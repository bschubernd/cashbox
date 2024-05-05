#!/usr/bin/python3

# read_appargs.py
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

import sys, os, pathlib, gi
from datetime import datetime
gi.require_version(namespace='Adw', version='1')
from gi.repository import GLib
dir1=os.path.dirname(os.path.realpath(__file__))
dir2=os.path.dirname(dir1)
sys.path.append(dir2)
from cashbox.utils import eprint

class AttrDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # hasattr expects AttributeError instead of KeyError
            # (needed for doctest)
            classname = type(self).__name__
            msg = f'{repr(classname)} object has no attribute {repr(key)}'
            raise AttributeError(msg)

    def __setattr__(self, key, value):
        self[key] = value

def init_appargs():
    """
    Set defaults for global variable "appargs".
    """
    global appargs
    appargs=AttrDict()

    # set default opts
    appargs["application_id"] = "de.bschu.cashbox"
    appargs["application_version"] = "0.3"
    appargs["user_app_dir"] = os.path.join(GLib.get_user_data_dir(), appargs.application_id)
    appargs["system_app_dir"] = os.path.join("/", "usr", "share", "cashbox")
    appargs["csspath"] = os.path.join(appargs.system_app_dir, "cashbox.css")
    appargs["dark"] = None
    appargs["session"] = datetime.now().strftime('%Y-%m-%d')

    appargs["currency"] = "Dollar"
    appargs["test_small_display"] = False
    appargs["max_name_len"] = 40
    appargs["conf_suffix"] = ".cshbx"

    # overwrite with dev opts
    if dir1.endswith("/src"):
        eprint(f"WARNING: using dev opts, because running in <{dir1}>")
        appargs["csspath"] = f"{dir1}/cashbox.css"

def read_appargs(opts={}, moreargs=[]):
    global appargs

    # set command_line opts
    for i in opts:
        appargs[i] = opts[i]

    # set command_line args
    appargs["moreargs"] = moreargs

    # do opts handling
    if appargs["currency"] == "Euro":
        appargs.update({"separator":",", "symbol":"€", "digits":2, "cents":10**2})
    elif appargs["currency"] == "Dollar":
        appargs.update({"separator":".", "symbol":"$", "digits":2, "cents":10**2})
    else:
        err(f"currency option <{appargs['currency']}> not Dollar or Euro")

    pathlib.Path(appargs.user_app_dir).mkdir(parents=True, exist_ok=True)

# init global variable appargs, to be included by other modules
if "appargs" not in globals():
    init_appargs()

if __name__ == '__main__':

    # try with option --help
    # try with option --number

    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import Adw, Gio
    import cashbox.read_appargs

    class App(Adw.Application):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, application_id="de.bschu.cashbox",
                             flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE |
                             Gio.ApplicationFlags.HANDLES_OPEN, **kwargs)

            self.connect('activate', self.on_activate)

            self.add_main_option("number", ord("n"), GLib.OptionFlags.NONE,
                                 GLib.OptionArg.INT, "Test number", None)

            self.set_option_context_parameter_string("MOREARGS")
            self.set_option_context_summary("More Args")
            self.set_option_context_description("More Args to be used in appargs.moreargs")

        def do_command_line(self, command_line):
            opts = command_line.get_options_dict().end().unpack()
            args = command_line.get_arguments()

            read_appargs(opts, args[1:])

            self.activate()
            return 0

        def on_activate(self, app):
            for i in appargs.keys():
                print(f"appargs[{i}]=<{appargs[i]}>")
            print(f"appargs.csspath=<{appargs.csspath}>")
            assert appargs.currency == "Dollar"

    app = App()
    app.run(sys.argv)
