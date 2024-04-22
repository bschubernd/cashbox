#!/usr/bin/python3

# utils.py
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
from gi.repository import Gio

def print_widget(w, level=1):
    """ print widgets

    >>> box=Gtk.Box()
    >>> label=Gtk.Label(label="mylabel")
    >>> box.append(label)
    >>> print_widget(box,1)
    - <GtkBox>
    -- <GtkLabel: mylabel>

    """

    if w is None:
        txt=w.get_name()
        if txt == "GtkLabel":
            txt=f"{txt}: {w.get_label()}"
        print("{'-'*level} <{txt}>")
        level=level+1
        w=w.get_first_child()
        while w:
            print_widget(w, level)
            w = w.get_next_sibling()

#def reduce_window_size(window, x=720, y=1440):
def reduce_window_size(window, x=350, y=600):
    window.props.default_width = x
    window.props.default_height = y

if __name__ == '__main__':
    import doctest
    doctest.testmod()

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def err(msg, retcode=1):
    eprint(f"Error: {msg}")
    sys.exit(retcode)

def create_action(window_or_application, name, function):
    action = Gio.SimpleAction.new(name, None)
    action.connect("activate", function)
    window_or_application.add_action(action)
