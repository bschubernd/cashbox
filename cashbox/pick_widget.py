#!/usr/bin/python3

# pick_widget.py
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

""" pick_widget.py provides class PickWidget """

import sys
import os
import gi

dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir1)


try:
    from cashbox.utils import reduce_window_size
    from cashbox.article import Article
except ImportError as exc:
    print('Error: cashbox modules not found.', exc)
    sys.exit(1)

if __name__ == '__main__':
    from cashbox.app import App, MinWindow
    from cashbox.article import Sale
    from cashbox.read_appargs import appargs

try:
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import Gtk, GObject
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


@Gtk.Template(filename=f'{dir1}/pick_widget_row.ui')
class PickRow(Gtk.Box):
    """ a row of a Pick Widget """
    __gtype_name__ = 'PickRow'
    action_row = Gtk.Template.Child()
    spin_button = Gtk.Template.Child()


@Gtk.Template(filename=f'{dir1}/pick_widget.ui')
class PickWidget(Gtk.Box):
    """ PickWidget to select articles to buy """
    __gtype_name__ = 'PickWidget'
    list_view = Gtk.Template.Child()

    def __init__(self, sale, **kwargs):
        super().__init__(**kwargs)

        # Selection
        ss = Gtk.NoSelection()
        self.list_view.set_model(ss)

        # sale
        self.sale = sale
        ss.set_model(self.sale.picked)

        # factory
        factory = Gtk.SignalListItemFactory()
        self.list_view.set_factory(factory)
        factory.connect("setup", self.factory_setup)
        factory.connect("bind", self.factory_bind)

    def factory_setup(self, _fact, item):
        """ setup factory """
        pick_row = PickRow()
        item.set_child(pick_row)

    def factory_bind(self, _fact, item):
        """ factory bind """
        article = item.get_item()
        pick_row = item.get_child()

        # make sure count is only editable with + and -
        # to avoid opening virtual keyboard on librem5
        c = pick_row.spin_button.get_first_child()
        c.set_sensitive(False)

        article.bind_property("name",
                              pick_row.action_row, "title",
                              GObject.BindingFlags.SYNC_CREATE)

        article.bind_property(
            "count",
            pick_row.spin_button, "value",
            GObject.BindingFlags.SYNC_CREATE |
            GObject.BindingFlags.BIDIRECTIONAL,
            transform_to=self.transform_count_to_spin_button,
            transform_from=self.transform_spin_button_to_count)

    def transform_count_to_spin_button(self, _binding, val):
        """ transform val for widget """
        print(f"transform_count_to_spin_button val=<{val}> type=<{type(val)}>")
        return val

    def transform_spin_button_to_count(self, _binding, val):
        """ transform val for widget """
        print(f"transform_spin_button_to_count val=<{val}> type=<{type(val)}>")
        return int(val)

    def output(self, spin_row, item):
        """ get count from widget (article.count may not be updated in
        article.count) """
        article = item.get_item()
        adjustment = spin_row.get_adjustment()
        count = int(adjustment.get_value())
        article.count = count
        # print(f"output: name=<{article.name}> count=<{count}>")
        if count > 0:
            # write price to subtitle
            spin_row.set_subtitle(str(article.price))


if __name__ == '__main__':

    class MyMainWindow(MinWindow):
        """ Test Window """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            if appargs.test_small_display:
                reduce_window_size(self)

            self.sale = Sale()

            article = [("Banana", 1.10, 1), ("Apple", 2.0, 2),
                       ("Strawberry", 2.50, 3), ("very long one two three "
                       "four five six seven eight", 9.99, 1),
                       ("Pear", 3.35, 0), ("Watermelon", 1.0, 5),
                       ("Blueberry", 2.0, 6)]
            for f in article:
                self.sale.main_list.append(Article(f[0], f[1], f[2]))

            self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.set_content(self.box)

            list_sale_button = Gtk.Button(label="list")
            self.box.append(list_sale_button)
            list_sale_button.connect('clicked', self.list_sale_clicked)

            self.pick_widget = PickWidget(self.sale)
            self.box.append(self.pick_widget)

            quit_button = Gtk.Button(label="quit")
            self.box.append(quit_button)
            quit_button.connect('clicked', self.quit_clicked)

        def list_sale_clicked(self, _list_button):
            """ test output """
            print(f"list_sale_clicked: sale=<{self.sale}>")

        def quit_clicked(self, _list_button):
            """ end test """
            self.close()

    class MyApp(App):
        """ test class App """

        def on_activate(self, app):
            win = MyMainWindow(application=app)
            win.present()

    myapp = MyApp()
    myapp.run(sys.argv)
