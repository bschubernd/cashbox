#!/usr/bin/python3
import os, gi, sys

# drop_down_widget.py - handle DropDown for cashbox
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

gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gio, GObject, Gtk
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)
from cashbox.article import Article, Sale, cent2str

@Gtk.Template(filename='%s/drop_down_widget_row.ui' % dir1)
class DropDownWidgetRow(Gtk.Box):
    __gtype_name__ = 'DropDownWidgetRow'
    w_name = Gtk.Template.Child()
    w_price = Gtk.Template.Child()

@Gtk.Template(filename='%s/drop_down_widget.ui' % dir1)
class DropDownWidget(Gtk.Box):
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

        data_list.bind_property("n-items",
            self.drop_down, "sensitive",
            GObject.BindingFlags.SYNC_CREATE,
            self._calc_sensitive, None)

    def get_drop_down(self):
        return self.drop_down

    def _calc_sensitive(self, a, b):
        print(f"transform_to a=<{a}> b=<{b}>")
        ret = False
        if b > 1:
            ret = True
        return ret

    def _on_factory_setup(self, factory, item):
        drop_down_widget_row = DropDownWidgetRow()
        item.set_child(drop_down_widget_row)

    def _on_factory_bind(self, factory, list_item):
        box = list_item.get_child()
        w_name = box.get_first_child()
        w_price = w_name.get_next_sibling()
        article = list_item.get_item()
        w_name.set_text(article.name)
        p=article.price
        if p:
            w_price.set_text(cent2str(article.price))
        else:
            w_price.set_text("")

if __name__ == '__main__':

    import sys
    from cashbox.app import App
    dir1 = os.path.dirname(os.path.realpath(__file__))
    dir2 = os.path.dirname(dir1)
    sys.path.append(dir2)
    from cashbox.read_appargs import read_appargs, appargs
    from app import App, MinWindow

    class DropDownWindow(MinWindow):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            sale=Sale()

            article = [("Banana",1.10,0), ("Apple",2.0,0), ("Strawberry",2.50,0),
                       ("Pear",3.35,4), ("Watermelon",1.0,5), ("Blueberry",2.0,6)]

            for f in article:
                sale.main_list.append(Article( f[0], f[1], f[2] ))

            drop_down_widget = DropDownWidget(sale.drop_unpicked)
            drop_down = drop_down_widget.get_drop_down()
            drop_down.connect("notify::selected-item", self.do_delete_selected_item)
            self.set_content(drop_down_widget)

        def do_delete_selected_item(self, dropdown, b):
            print("do_delete_selected_item")
            if dropdown.get_selected() > 0:
                article = dropdown.get_selected_item()
                print(f"do_delete_selected_item: article=<{article}>")
                dropdown.set_selected(0)
                article.count=1

    class MyApp(App):

        def on_activate(self, app):
            self.win = DropDownWindow(application=app)
            self.win.present()

    read_appargs()
    app = MyApp()
    app.run(sys.argv)
