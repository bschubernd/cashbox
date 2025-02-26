#!/usr/bin/python3

# pricelist_widget.py
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

""" pricelist widget """

import sys
import os
import doctest
import gi

dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)

try:
    from cashbox.utils import create_action
    from cashbox.article import Article, Comment, Sale, str2cent
    from cashbox.read_appargs import appargs
    from cashbox.cshbx import Cshbx
    from cashbox.dialog_widget import DialogWidget
    from cashbox.locale_utils import _, f
except ImportError as exc:
    print('Error: cashbox modules not found.', exc)
    sys.exit(1)

if __name__ == '__main__':
    from cashbox.app import App, MinWindow

try:
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import Gtk, Gio
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


@Gtk.Template(filename=f'{dir1}/pricelist_widget.ui')
class PricelistWidget(Gtk.Box):
    """ to edit a list of articles """
    __gtype_name__ = 'PricelistWidget'
    textview = Gtk.Template.Child()
    error = Gtk.Template.Child()
    file_dialog = Gtk.Template.Child()  # Gtk.FileDialog
    cashbox_file_filter = Gtk.Template.Child()
    red_tag = Gtk.Template.Child()
    green_tag = Gtk.Template.Child()
    orange_tag = Gtk.Template.Child()

    class LineInfo():
        "Info and Errors seen in one line"

        def __init__(self):
            self.n = None  # article name
            self.p = None  # article price
            self.c = None  # article count
            self.n_err = None  # seen n errors
            self.p_err = None  # seen p errors
            self.c_err = None  # seen c errors
            self.other_err = {"double_name": None,  # the name, that is double
                              "name_to_long": None}  # how many chars to long

        def line_ok(self):
            """ check if line is ok """
            return (self.p and self.n and self.c
                    and not self.other_err["double_name"]
                    and not self.other_err["name_to_long"])

        def check_name_len(self, name, max_len):
            """ check if name is to long """
            self.other_err["name_to_long"] = len(name) - max_len
            if self.other_err["name_to_long"] <= 0:
                self.other_err["name_to_long"] = None

    @Gtk.Template.Callback()
    def on_unmap_all(self, _widget):
        """ time to check list of articles """
        self.check_buffer()

    @Gtk.Template.Callback()
    def on_map_all(self, _widget):
        """ write sale-variable to widget-buffer """
        self.buffer.set_text(self.sale.text())

    def __init__(self, sale, win, **kwargs):
        super().__init__(**kwargs)

        self.win = win
        self.sale = sale
        self.buffer = self.textview.get_buffer()

        self.buffer.set_enable_undo(True)

        self.table = self.buffer.get_tag_table()
        self.cshbx = Cshbx()

        create_action(win, "undo", self.on_undo_action)
        create_action(win, "redo", self.on_redo_action)
        create_action(win, "save", self.on_save_dialog)
        create_action(win, "load", self.on_load_dialog)
        create_action(win, "append", self.on_append_dialog)
        create_action(win, "help_workflow", self.on_help_workflow)
        create_action(win, "help_syntax", self.on_help_syntax)

        self.table.add(self.red_tag)
        self.table.add(self.green_tag)
        self.table.add(self.orange_tag)

        self.buffer.connect('changed', self.on_buffer_changed)
        self.check_buffer()
        self.buffer.connect('notify::cursor-position', self.on_cursor)

        self.cursor_seen_in_line = (-1, -1)

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(self.cashbox_file_filter)

        self.file_dialog.set_filters(filters)
        self.file_dialog.set_initial_folder(Gio.File.new_for_path(
                                            appargs.user_app_dir))

    def on_undo_action(self, _action, _param):
        """ undo last step """
        self.buffer.undo()

    def on_redo_action(self, _action, _param):
        """ redo last undo """
        self.buffer.redo()

    def on_cursor(self, buffer, pos):
        """ cursor has moved """
        pos = buffer.get_property("cursor-position")
        (a, b) = self.cursor_seen_in_line
        if pos < a or pos > b:
            self.check_buffer()

    def check_buffer_line(self, line):
        """ check for line for syntax errors """
        line_info = self.LineInfo()
        # get the last match of price in a line
        p_iter = list(self.cshbx.re_price.finditer(line))
        if p_iter:
            line_info.p = list(p_iter)[-1]
            a_line = line[:line_info.p.start(0)]
            line_info.n = self.cshbx.re_name.match(a_line)
            if not line_info.n:
                line_info.n_err = self.cshbx.re_some.match(a_line)

            c_line = line[line_info.p.end(0):]
            line_info.c = self.cshbx.re_count.match(c_line)
            if not line_info.c:
                line_info.c_err = self.cshbx.re_some.match(c_line)
        else:
            line_info.p_err = self.cshbx.re_some.match(line)
        return line_info

    def color_text(self, buffer, line_start, li):
        """
        Checks the line in <buffer> starting at <line_start>, that represent
        an article.
        Uses the regex results <n> (name), <p> (price) and <c> (optional count)
        and the corresponding errors if the regex failed.
        Returns a list of hints to fix the errors.

        green: ok
        orange: the marked text could be used if another part would be fixed
        red: the text itself must be fixed
        """
        def apply_tag(start, end, tag):
            iter_start = buffer.get_iter_at_offset(line_start + start)
            iter_end = buffer.get_iter_at_offset(line_start + end)
            buffer.apply_tag(tag, iter_start, iter_end)

        error = []
        if li.line_ok():
            apply_tag(li.n.start(2), li.n.end(2), self.green_tag)
            apply_tag(li.p.start(1), li.p.end(5), self.green_tag)
            apply_tag(li.p.end(5)+li.c.start(2), li.p.end(5)+li.c.end(2),
                      self.green_tag)
        else:
            if li.p:
                apply_tag(li.p.start(0), li.p.end(1), self.orange_tag)
                if li.n:
                    name_to_long = li.other_err["name_to_long"]
                    if name_to_long:
                        error += [f(_("name {name_to_long} chars to long"))]
                        apply_tag(li.n.start(2), li.n.end(2), self.red_tag)
                    elif li.other_err["double_name"]:
                        error += [_("name already exists")]
                        apply_tag(li.n.start(2), li.n.end(2), self.orange_tag)
                    else:
                        apply_tag(li.n.start(2), li.n.end(2), self.orange_tag)
                elif li.n_err:
                    apply_tag(li.n_err.start(2), li.n_err.end(2), self.red_tag)
                    error += [_("no space after article name")]
                else:
                    error += [_("no article name")]
                if li.c:
                    apply_tag(li.c.start(2)+li.p.end(4),
                              li.c.end(2)+li.p.end(4), self.orange_tag)
                elif li.c_err:
                    apply_tag(li.c_err.start(2)+li.p.end(5),
                              li.c_err.end(2)+li.p.end(5), self.red_tag)
                    error += [_("bad optional count")]
            elif li.p_err:
                apply_tag(li.p_err.start(0), li.p_err.end(0), self.red_tag)
                error += [_("no price found")]

        return error

    def on_buffer_changed(self, _buffer):
        """ time to check list of articles """
        self.check_buffer()

    def check_buffer(self):
        """
        check text buffer and return the current sale represented
        by the the buffer.

        if buffer2sale == True:
            write widget-buffer to sale
        """

        def get_text(start, end):
            return line[start:end]

        line = None

        self.sale.clear()

        # clear color tags
        (iter1, iter2) = self.buffer.get_bounds()
        self.buffer.remove_all_tags(iter1, iter2)
        text = self.buffer.get_text(iter1, iter2, False)

        hint = ""
        if text == "":
            hint = _("please add lines with article and price")
        else:
            names = []
            line_start = 0  # start of current line in text
            for (line_nr, line) in enumerate(text.splitlines()):

                cursor = self.buffer.get_property("cursor-position")

                if line_start <= cursor <= line_start+len(line):
                    self.cursor_seen_in_line = (line_start,
                                                line_start+len(line))

                if line.lstrip()[:1] == "#":
                    # comment starting with "#"
                    self.sale.main_list.append(Comment(line))
                else:
                    # n=article name, p=article price, c=article count
                    li = self.check_buffer_line(line)
                    if li.n:
                        name = get_text(li.n.start(2), li.n.end(2))
                        if name in names:
                            li.other_err["double_name"] = name
                        li.check_name_len(name, appargs.max_name_len)
                    error = self.color_text(self.buffer, line_start, li)

                    if li.line_ok():
                        names.append(name)
                        article = Article(
                            name, str2cent(get_text(li.p.start(2), li.p.end(2))
                                           + "." + get_text(li.p.start(4),
                                           li.p.end(4))),
                            int("0" + get_text(li.p.end(5) + li.c.start(2),
                                               li.p.end(5) + li.c.end(2))))
                        # eprint(f"article=<{article}>")
                        self.sale.main_list.append(article)
                    else:
                        # error: give error message, but handled like a comment
                        self.sale.main_list.append(Comment(line))

                    if line_start <= cursor <= line_start+len(line) and error:
                        hint = f"line {line_nr+1}: "+", ".join(error)

                line_start += len(line)+1

        self.error.set_label(hint)

    def on_save_dialog(self, _action, _param):
        """ save start """
        self.file_dialog.save(None, None, self.on_save_dialog_finish)

    def on_save_dialog_finish(self, dialog, task):
        """ save end """
        file = dialog.save_finish(task)

        (iter1, iter2) = self.buffer.get_bounds()
        text = self.buffer.get_text(iter1, iter2, False)

        path = file.get_path()
        if not path.endswith(appargs.conf_suffix):
            path = path+appargs.conf_suffix

        with open(path, 'w', encoding="utf-8") as p:
            p.write(text)

    def on_load_dialog(self, _action, _param):
        """ load start """
        self.file_dialog.open(None, None, self.on_load_dialog_finish)

    def on_load_dialog_finish(self, dialog, task):
        """ load start """
        file = dialog.open_finish(task)
        (iter1, iter2) = self.buffer.get_bounds()
        with open(file.get_path(), 'r', encoding="utf-8") as p:
            data = p.read()
            self.buffer.delete(iter1, iter2)
            self.buffer.insert(iter1, data)

    def on_append_dialog(self, _action, _param):
        """ append start """
        self.file_dialog.open(None, None, self.on_append_dialog_finish)

    def on_help_workflow(self, _action, _param):
        """ help """
        d = DialogWidget()
        win = self
        d.help_dialog(win, _("pricelist workflow"), f(_("""\
{d.As} are listed in a text with {d.n} and {d.p} and an optional {d.c} in \
{d.Pl}. \
This text can be directly edited. It can also contain blank lines and \
comments. \
The text can be saved, loaded and appended with with the hamburger file menu. \
The  hamburger menu has Undo and Redo buttons to return to a previous state.

It is possible to enter all {d.as_} before starting with {d.S}, or to enter \
each {d.a} when it is sold, or a mixture of both methods.

It may also be possible to make a photo of a table of prices, and to use ocr \
software to extract text from the photo, before running {d.C}. The text can \
then be loaded in {d.Pl}. Then {d.ns} and {d.ps} can be copied and pasted \
to the needed syntax.""")))

    def on_help_syntax(self, _action, _param):
        """ help syntax """
        d = DialogWidget()
        win = self
        d.help_dialog(win, _("pricelist syntax"), f(_("""\
{d.Pl} mainly consists of a large text field, where a line can represents an \
{d.a}. Lines can also be empty or contain a comment.

A line with an {d.a} contains a {d.n} and {d.p} and an optional {d.c} \
separated by spaces. Lines starting with '#' are comments.

The {d.p} consists of digits followed by '.' or ',' and 2 additional digits. \
Text before the {d.p} is the {d.n}. The {d.p} may be followed by digits \
that represents a {d.c} to show how often the {d.a} is currently sold.""")))

    def on_append_dialog_finish(self, dialog, task):
        """ append end """
        file = dialog.open_finish(task)
        (_iter1, iter2) = self.buffer.get_bounds()
        with open(file.get_path(), 'r', encoding="utf-8") as p:
            data = p.read()
            self.buffer.insert(iter2, '\n'+data)

    def read_files(self, files):
        """ read """
        if files:
            with open(files[0], 'r', encoding="utf-8") as p:
                data = p.read()
                self.buffer.set_text(data)


if __name__ == '__main__':

    doctest.testmod()

    class PricelistWindow(MinWindow):
        """ Test Class """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            sale = Sale()

            pricelist_widget = PricelistWidget(sale, win=self)
            self.set_content(pricelist_widget)

            # style_manager = app.get_style_manager()
            # style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
            # style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

            if appargs.moreargs:
                # read testdata from file
                pricelist_widget.read_files(appargs.moreargs)
            else:
                # create minimal testdata now
                article = [("Banana", 1.10, 1), ("Apple", 2.0, 0)]
                for a in article:
                    sale.main_list.append(Article(a[0], a[1], a[2]))

    class MyApp(App):
        """ test class App """

        def on_activate(self, app):
            win = PricelistWindow(application=app)
            win.present()

    myapp = MyApp()
    myapp.run(sys.argv)
