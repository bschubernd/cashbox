#!/usr/bin/python3

# sale_widget.py
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

import gi, sys, os
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir1)
from cashbox.pick_widget import PickWidget
from cashbox.drop_down_widget import DropDownWidget
from cashbox.utils import create_action
from cashbox.dialog_widget import DialogWidget
from cashbox.locale_utils import _, f


@Gtk.Template(filename=f'{dir1}/sale_widget.ui')
class SaleWidget(Gtk.Box):
    __gtype_name__ = 'SaleWidget'
    sale_widget_menu_box = Gtk.Template.Child()
    sale_widget_box = Gtk.Template.Child()

    def do_pick_item(self, dropdown, b):
        if dropdown.get_selected() > 0:
            article = dropdown.get_selected_item()
            dropdown.set_selected(0)
            article.count=1

    def __init__(self, sale, win, **kwargs):
        super().__init__(**kwargs)

        self.sale=sale
        self.win=win

        drop_down_widget = DropDownWidget(sale.drop_unpicked)
        drop_down = drop_down_widget.get_drop_down()

        drop_down.connect("notify::selected-item", self.do_pick_item)
        self.sale_widget_menu_box.append(drop_down_widget)

        pick = PickWidget(sale)
        self.sale_widget_box.append(pick)

        create_action(win, "help_sale", self.on_help_sale)

    def on_help_sale(self, action, _param):
        d = DialogWidget()
        win=self
        d.help_dialog(win, _("Sale Help"), f(_("""\
To sell {d.as_}, they can be selected from a drop down menu. They will then \
be shown in the order selected in the {d.S} widget, where the {d.c} to be sold \
can be adjusted.

The {d.as_} in the drop down menu always have the same order as in the {d.Pl}. \
If some {d.as_} are sold more often than others, they may be moved to the \
beginning in the {d.Pl}, to be able to find and select them faster in future.
""")))


if __name__ == '__main__':

    from cashbox.app import App, MinWindow
    from cashbox.article import Article, Sale

    class SaleWindow(MinWindow):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            sale=Sale()

            article = [("Banana",110,0), ("Apple",200,0), ("Strawberry",250,0),
                       ("Pear",335,4), ("Watermelon",100,5), ("Blueberry",200,6)]

            for a in article:
                sale.main_list.append(Article( a[0], a[1], a[2] ))

            box = Gtk.Box(spacing=12, hexpand=True, vexpand=True)
            box.props.margin_start = 12
            box.props.margin_end = 12
            box.props.margin_top = 6
            box.props.margin_bottom = 6
            self.set_content(box)

            sale_widget=SaleWidget(sale, win=self)
#           sale_widget=SaleWidget(sale)
            box.append(sale_widget)


    class MyApp(App):

        def on_activate(self, app):
            self.win = SaleWindow(application=app)
            self.win.present()


    app = MyApp()
    app.run(sys.argv)
