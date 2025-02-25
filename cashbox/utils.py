#!/usr/bin/python3

# utils.py
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

""" utils """

import sys
import gi

try:
    gi.require_version('Gtk', '4.0')
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import Gio
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


def widget_info(widget, level=1):
    """ widget_info

    >>> from gi.repository import Gtk
    >>> box=Gtk.Box()
    >>> label=Gtk.Label(label="mylabel")
    >>> box.append(label)
    >>> print(widget_info(box))
    - <GtkBox>
    -- <GtkLabel> label=<mylabel>

    """

    ret = ""
    if widget:
        indent = "-"*level
        txt = widget.get_name()
        ret = f"{ret}{indent} <{txt}>"
        blp_id = widget.get_buildable_id()  # id defined in *.blp or *.ui
        if blp_id:
            ret = f"{ret} id=<{blp_id}>"
        if txt == "GtkLabel":
            label = widget.get_label()
            if label:
                ret = f"{ret} label=<{label}>"
    if widget:
        widget = widget.get_first_child()
        while widget:
            ret = f"{ret}\n{widget_info(widget, level+1)}"
            widget = widget.get_next_sibling()
    return ret


def reduce_window_size(window, x=350, y=600):
    """ x """
    window.props.default_width = x
    window.props.default_height = y


if __name__ == '__main__':
    import doctest
    doctest.testmod()


def eprint(*args, **kwargs):
    """ print on stderr """
    print(*args, file=sys.stderr, **kwargs)


def err(msg, retcode=1):
    """ print error and exit """
    eprint(f"Error: {msg}")
    sys.exit(retcode)


def create_action(window_or_application, name, function):
    """ create ancd connect action """
    action = Gio.SimpleAction.new(name, None)
    action.connect("activate", function)
    window_or_application.add_action(action)
