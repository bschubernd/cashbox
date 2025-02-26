#!/usr/bin/python3

# dialog_widget.py
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

""" dialog_widget.py contains classes to display dialogs """

import sys
import os
import gi

dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)

try:
    from cashbox.locale_utils import _, f
except ImportError as exc:
    print('Error: cashbox modules not found.', exc)
    sys.exit(1)

try:
    gi.require_version('Adw', '1')
    gi.require_version('Gtk', '4.0')
    from gi.repository import Adw, Gtk
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


@Gtk.Template(filename=f'{dir1}/dialog_widget.ui')
class DialogWidget(Gtk.Box):
    """ present dialogs """
    __gtype_name__ = 'DialogWidget'
    help_widget_dialog = Gtk.Template.Child()
    help_widget_label = Gtk.Template.Child()
    about_widget_dialog = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, val in self.abbreviations().items():
            setattr(self, key, val)

    def abbreviations(self):
        """
        this method should be overwritten, if DialogWidged class
        is used outside of cashbox.
        """
        return {"a": self.data(_("article")),
                "as_": self.data(_("articles")),
                "As": self.data(_("Articles")),
                "C": self.widget(_("Cashbox")),
                "c": self.data(_("count")),
                "cs": self.data(_("counts")),
                "n": self.data(_("name")),
                "ns": self.data(_("names")),
                "p": self.data(_("price")),
                "ps": self.data(_("prices")),
                "Pl": self.widget(_("Pricelist")),
                "R": self.widget(_("Receipt")),
                "S": self.widget(_("Sale"))}

    def widget(self, txt):
        """ text about widget will be blue """
        return f"<b><span foreground='blue'>{txt}</span></b>"

    def data(self, txt):
        """ text about data will be green """
        return f"<b><span foreground='green'>{txt}</span></b>"

    def help_dialog(self, win, title, txt):
        """ show help """
        dialog = self.help_widget_dialog
        label = self.help_widget_label
        dialog.set_title(title)
        label.set_label(txt)
        dialog.present(win)

    def about_dialog(self, win, txt, version="0.0"):
        """ show info about cashbox """
        about = self.about_widget_dialog
        about.set_comments(txt)
        about.set_developers(["Bernd Schumacher"])
        about.set_version(version)
        about.present(win)


if __name__ == '__main__':

    a1 = _("hallo")

    class DialogWindow(Adw.ApplicationWindow):
        """ Test Dialog Window """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.props.default_width = 350
            self.props.default_height = 600

            box = Gtk.Box()
            box.set_orientation(Gtk.Orientation.VERTICAL)
            self.set_content(box)

            button = Gtk.Button(label=_("test_help_dialog"))
            box.append(button)
            button.connect('clicked', self.on_test_help_dialog)

            button = Gtk.Button(label=_("test_about"))
            box.append(button)
            button.connect('clicked', self.on_test_about)

        def on_test_about(self, _button):
            """ show about widget """
            d = DialogWidget()
            win = self
            d.about_dialog(win, f(_("""\
one two three {d.As}""")))

        def on_test_help_dialog(self, _button):
            """ show dialog widget """
            d = DialogWidget()
            win = self
            d.help_dialog(win, _("test_title"), f(_("""\
one two three
{d.As} can be listed with {d.n} and {d.p} in {d.Pl}.""")))

    class MyApp(Adw.Application):
        """ test class App """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.connect('activate', self.on_activate)

        def on_activate(self, app):
            """ start test window """
            win = DialogWindow(application=app)
            win.present()

    myapp = MyApp()
    myapp.run(sys.argv)
