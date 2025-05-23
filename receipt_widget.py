#!/usr/bin/python3

# receipt_widget.py
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

""" receipt widget """

import sys
import os
import pathlib
from datetime import datetime
import gi

dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir1)

if __name__ == '__main__':
    from cashbox.app import App, MinWindow

try:
    from cashbox.utils import eprint, create_action
    from cashbox.read_appargs import appargs
    from cashbox.article import Article, Sale, cent2str, str2cent
    from cashbox.cshbx import Cshbx
    from cashbox.dialog_widget import DialogWidget
    from cashbox.locale_utils import _, f
except ImportError as exc:
    print('Error: cashbox modules not found.', exc)
    sys.exit(1)

try:
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import Gtk, Gio, GObject
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


@Gtk.Template(filename=f'{dir1}/receipt_widget_row.ui')
class ReceiptWidgetRow(Gtk.Box):
    """ Receipt Widget """
    __gtype_name__ = 'ReceiptWidgetRow'
    action_row = Gtk.Template.Child()
    count_label = Gtk.Template.Child()
    price_label = Gtk.Template.Child()
    sum_label = Gtk.Template.Child()


@Gtk.Template(filename=f'{dir1}/receipt_widget_dialog.ui')
class ReceiptWidgetDialog(Gtk.Box):
    """ ReceiptWidgetDialog """
    __gtype_name__ = 'ReceiptWidgetDialog'
    statistic_dialog = Gtk.Template.Child()  # Adw.Dialog
    session = Gtk.Template.Child()
    sales = Gtk.Template.Child()
    revenue = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_statistic_dialog_end(self, _button):
        """ x """
        self.statistic_dialog.close()


@Gtk.Template(filename=f'{dir1}/receipt_widget.ui')
class ReceiptWidget(Gtk.Box):
    """ x """
    __gtype_name__ = 'ReceiptWidget'
    list_view = Gtk.Template.Child()
    money_sum = Gtk.Template.Child()
    money_in = Gtk.Template.Child()
    money_out = Gtk.Template.Child()
    file_dialog = Gtk.Template.Child()  # Gtk.FileDialog
    ok_button = Gtk.Template.Child()

    def __init__(self, sale, win, **kwargs):
        super().__init__(**kwargs)

        # win
        self.win = win
        self.cshbx = Cshbx()

        # prepare on_money_in
        self.money_in_buffer = self.money_in.get_buffer()
        self.money_in_buffer.connect('notify', self.on_money_in)
        self.money_sum_buffer = self.money_sum.get_buffer()
        self.money_out_buffer = self.money_out.get_buffer()

        # label_sizegroup
        self.sizegroups = {"name": Gtk.SizeGroup(), "count": Gtk.SizeGroup(),
                           "price": Gtk.SizeGroup(), "sum": Gtk.SizeGroup()}
        self.sizegroups["name"].set_mode(Gtk.SizeGroupMode.HORIZONTAL)
        self.sizegroups["count"].set_mode(Gtk.SizeGroupMode.HORIZONTAL)
        self.sizegroups["price"].set_mode(Gtk.SizeGroupMode.HORIZONTAL)
        self.sizegroups["sum"].set_mode(Gtk.SizeGroupMode.HORIZONTAL)

        # SingleSelection
        selection = Gtk.NoSelection()
        self.list_view.set_model(selection)

        # sale
        self.sale = sale
        selection.set_model(self.sale.picked)

        # factory
        factory = Gtk.SignalListItemFactory()
        self.list_view.set_factory(factory)
        factory.connect("setup", self.on_factory_setup)
        factory.connect("bind", self.on_factory_bind)

        # action
        create_action(win, "chng_session_dir", self.on_chng_session_dir)
        create_action(win, "show_statistic", self.on_show_statistic)
        create_action(win, "help_receipt", self.on_help_receipt)

    def on_help_receipt(self, _action, _param):
        """ x """
        d = DialogWidget()
        win = self
        d.help_dialog(win, _("Receipt Help"), f(_("""\
In the {d.R} window the {d.p} to pay is shown. The paid amount can be entered \
and the return will be shown. With 'Ok' the sale will be saved and the \
selected {d.a} {d.cs} will be resetted for the next customer.""")))

    def on_money_in(self, _a, _b):
        """ x """
        money_sum = str2cent(self.money_sum_buffer.get_text())
        money_in_text = self.money_in_buffer.get_text()
        money_out_text = ""
        money_in = str2cent(money_in_text, True)
        if money_in and money_sum:
            if money_in > money_sum:
                money_out_text = cent2str(money_in - money_sum)
        self.money_out_buffer.set_text(money_out_text, len(money_out_text))

    @Gtk.Template.Callback()
    def on_map_sum(self, _widget):
        """ x """
        paysum = 0
        for article in self.sale.picked:
            paysum += article.price * article.count
            print(f"sum=<{sum}>")
        if paysum > 0:
            self.ok_button.set_sensitive(True)
        else:
            self.ok_button.set_sensitive(False)
        s = cent2str(paysum)
        print(f"on_map_sum will set <{s}>")
        self.money_sum_buffer.set_text(s, len(s))

    @Gtk.Template.Callback()
    def on_save_receipt(self, button):
        """ x """
        eprint(f"on_savereceipt: button=<{button}>")
        session_dir = os.path.join(appargs.user_app_dir, appargs.session)
        pathlib.Path(session_dir).mkdir(parents=True, exist_ok=True)
        save_time = datetime.now().strftime('%H-%M-%S')
        sale_file = os.path.join(session_dir, save_time + ".cshbx")
        eprint(f"sale_file=<{sale_file}>")
        eprint(f"txt=<{self.sale.text()}>")
        with open(sale_file, 'w', encoding="utf-8") as file:
            file.write(self.sale.text())
        self.sale.count_zero()
        self.money_in_buffer.delete_text(0, -1)
        self.money_sum_buffer.delete_text(0, -1)
        self.ok_button.set_sensitive(False)

    def on_factory_setup(self, _fact, item):
        """ x """
        receipt_row = ReceiptWidgetRow()
        item.set_child(receipt_row)
        receipt_row.connect('map', self.on_map_row, item)

    def on_factory_bind(self, _fact, item):
        """ x """
        article = item.get_item()
        receipt_row = item.get_child()
        self.sizegroups["price"].add_widget(receipt_row.price_label)
        self.sizegroups["count"].add_widget(receipt_row.count_label)
        self.sizegroups["sum"].add_widget(receipt_row.sum_label)

        article.bind_property("name",
                              receipt_row.action_row, "title",
                              GObject.BindingFlags.SYNC_CREATE)

    def on_map_row(self, receipt_row, item):
        """ x """
        article = item.get_item()
        receipt_row.count_label.set_label(f"{article.count}")
        receipt_row.price_label.set_label(cent2str(article.price))
        receipt_row.sum_label.set_label(cent2str(article.price *
                                        article.count))

    def on_chng_session_dir(self, _action, _param):
        """ x """
        session_dir = os.path.join(appargs.user_app_dir, appargs.session)
        pathlib.Path(session_dir).mkdir(parents=True, exist_ok=True)
        self.file_dialog.set_initial_folder(Gio.File.new_for_path(session_dir))
        self.file_dialog.select_folder(None, None,
                                       self.on_chng_session_dir_finish)

    def on_chng_session_dir_finish(self, dialog, task):
        """ x """
        file = dialog.select_folder_finish(task)
        if file:
            path = file.get_path()
            appargs.session = os.path.basename(path)

    def on_show_statistic(self, _action, _param):
        """ x """
        session_dir = os.path.join(appargs.user_app_dir, appargs.session)
        names = [name for name in os.listdir(session_dir) if
                 os.path.isfile(os.path.join(session_dir, name))]

        revenue = 0
        for name in names:
            with open(os.path.join(session_dir, name), 'r',
                      encoding="utf-8") as file:
                for line in file:
                    revenue += self.cshbx.get_cent_price(line)

        receipt_widget_dialog = ReceiptWidgetDialog()
        receipt_widget_dialog.session.set_label(appargs.session)
        receipt_widget_dialog.sales.set_label(f"{len(names)}")
        receipt_widget_dialog.revenue.set_label(f"{revenue/appargs.cents}")

        statistic_dialog = receipt_widget_dialog.statistic_dialog
        statistic_dialog.present(self.win)


if __name__ == '__main__':

    class ReceiptWindow(MinWindow):
        """ x """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.sale = Sale()

            self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.set_content(self.box)

            list_sale_button = Gtk.Button(label="list")
            self.box.append(list_sale_button)
            list_sale_button.connect('clicked', self.list_sale_clicked)

            self.pick_widget = ReceiptWidget(self.sale, win=self)
            self.box.append(self.pick_widget)

            quit_button = Gtk.Button(label="quit")
            self.box.append(quit_button)
            quit_button.connect('clicked', self.quit_clicked)

            article = [("Banana", 110, 1), ("Apple", 200, 2),
                       ("Strawberry", 250, 3), ("Pear", 335, 4),
                       ("Watermelon", 100, 5), ("Blueberry", 200, 6)]

            for a in article:
                self.sale.main_list.append(Article(a[0], a[1], a[2]))

        def list_sale_clicked(self, _list_button):
            """ x """
            print(f"list_sale_clicked: sale=<{self.sale}>")

        def quit_clicked(self, _list_button):
            """ x """
            self.close()

    class MyApp(App):
        """ x """

        def on_activate(self, app):
            win = ReceiptWindow(application=app)
            win.present()

    # appargs.read_appargs()

    myapp = MyApp()
    myapp.run(sys.argv)
