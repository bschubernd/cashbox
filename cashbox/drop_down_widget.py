#!/usr/bin/python3

# drop_down_widget.py
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

""" customized DropDown class """

import sys
import os
import gi

dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)

try:
    from cashbox.app import App, MinWindow
    from cashbox.article import Article, DropDownHead, Sale, cent2str
except ImportError as exc:
    print('Error: cashbox modules not found.', exc)
    sys.exit(1)

try:
    gi.require_version('Adw', '1')
    gi.require_version('Gtk', '4.0')
    from gi.repository import GObject, Gtk
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


@Gtk.Template(filename=f'{dir1}/drop_down_widget_row.ui')
class DropDownWidgetRow(Gtk.Box):
    """ row of DropDown """
    __gtype_name__ = 'DropDownWidgetRow'
    w_name = Gtk.Template.Child()
    w_price = Gtk.Template.Child()


@Gtk.Template(filename=f'{dir1}/drop_down_widget.ui')
class DropDownWidget(Gtk.Box):
    """ Widget which displays Rows """
    __gtype_name__ = 'DropDownWidget'
    drop_down = Gtk.Template.Child()

    def __init__(self, data_list, **kwargs):
        super().__init__(**kwargs)

        # Set model
        self.drop_down.set_model(data_list)

        # Set up the factory
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_factory_setup)
        factory.connect("bind", self._on_factory_bind)
        self.drop_down.set_factory(factory)

        data_list.bind_property(
            "n-items",
            self.drop_down, "sensitive",
            GObject.BindingFlags.SYNC_CREATE,
            self._calc_sensitive, None)

    def get_drop_down(self):
        """ return drop_down """
        return self.drop_down

    def _calc_sensitive(self, _a, b):
        ret = False
        if b > 1:
            ret = True
        return ret

    def _on_factory_setup(self, _factory, item):
        drop_down_widget_row = DropDownWidgetRow()
        item.set_child(drop_down_widget_row)

    def _on_factory_bind(self, _factory, list_item):
        box = list_item.get_child()
        w_name = box.get_first_child()
        w_price = w_name.get_next_sibling()
        data = list_item.get_item()
        if isinstance(data, Article):
            w_name.set_text(data.name)
            w_price.set_text(cent2str(data.price))
        else:
            assert isinstance(data, DropDownHead)
            w_name.set_text(data.drop_down_head)
            w_price.set_text("")


if __name__ == '__main__':

    class DropDownWindow(MinWindow):
        """ test Class """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            sale = Sale()

            article = [("Banana", 1.10, 0), ("Apple", 2.0, 0),
                       ("Strawberry", 2.50, 0), ("Pear", 3.35, 4),
                       ("Watermelon", 1.0, 5), ("Blueberry", 2.0, 6)]

            for f in article:
                sale.main_list.append(Article(f[0], f[1], f[2]))

            drop_down_widget = DropDownWidget(sale.drop_unpicked)
            drop_down = drop_down_widget.get_drop_down()
            drop_down.connect("notify::selected-item",
                              self.do_delete_selected_item)
            self.set_content(drop_down_widget)

        def do_delete_selected_item(self, dropdown, _b):
            """ test method """
            print("do_delete_selected_item")
            if dropdown.get_selected() > 0:
                article = dropdown.get_selected_item()
                print(f"do_delete_selected_item: article=<{article}>")
                dropdown.set_selected(0)
                article.count = 1

    class MyApp(App):
        """ test class App """

        def on_activate(self, app):
            win = DropDownWindow(application=app)
            win.present()

    myapp = MyApp()
    myapp.run(sys.argv)
