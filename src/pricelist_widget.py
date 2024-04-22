#!/usr/bin/python3

# pricelist_widget.py
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

import os, sys, gi
gi.require_version(namespace='Adw', version='1')
from gi.repository import Gtk, Gio
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)
from cashbox.utils import eprint, print_widget, create_action
from cashbox.article import Article, Comment, Sale, str2cent
from cashbox.drop_down_widget import DropDownWidget
from cashbox.read_css import read_css
from cashbox.read_appargs import read_appargs, appargs
from cashbox.cshbx import Cshbx
from cashbox.dialog_widget import DialogWidget
from cashbox.locale_utils import _, f

@Gtk.Template(filename='%s/pricelist_widget.ui' % dir1)
class PricelistWidget(Gtk.Box):
    __gtype_name__ = 'PricelistWidget'
    textview = Gtk.Template.Child()
    error = Gtk.Template.Child()
    file_dialog = Gtk.Template.Child() # Gtk.FileDialog
    cashbox_file_filter = Gtk.Template.Child()
    red_tag = Gtk.Template.Child()
    green_tag = Gtk.Template.Child()
    orange_tag = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_unmap_all(self, widget):
        self.check_buffer()

    @Gtk.Template.Callback()
    def on_map_all(self, widget):
        # write sale-variable to widget-buffer
        self.buffer.set_text(self.sale.text())

    def __init__(self, sale, win, **kwargs):
        super().__init__(**kwargs)

        self.win=win
        self.sale=sale
        self.buffer=self.textview.get_buffer()

        self.buffer.set_enable_undo(True)

        self.table=self.buffer.get_tag_table()
        self.cshbx=Cshbx()

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

        self.cursor_seen_in_line=(-1,-1)

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(self.cashbox_file_filter)

        self.file_dialog.set_filters(filters)
        self.file_dialog.set_initial_folder(Gio.File.new_for_path(appargs.user_app_dir))


    def on_undo_action(self, action, param):
        self.buffer.undo()

    def on_redo_action(self, action, param):
        self.buffer.redo()

    def on_cursor(self, buffer, pos):
        pos=buffer.get_property("cursor-position")
        (a,b)=self.cursor_seen_in_line
        if pos<a or pos>b:
            self.check_buffer()

    def check_buffer_line(self, line):
        # n=article name, p=article price, c=article count
        (n, p, c, n_err, p_err, c_err) = (None, None, None, None, None, None)
        # get the last match of price in a line
        p_iter = list( self.cshbx.re_price.finditer(line) )
        if len(p_iter):
            p=list(p_iter)[-1]
            a_line=line[:p.start(0)]
            n = self.cshbx.re_name.match(a_line)
            if not n:
                n_err = self.cshbx.re_some.match(a_line)

            c_line=line[p.end(0):]
            c = self.cshbx.re_count.match(c_line)
            if not c:
                c_err = self.cshbx.re_some.match(c_line)
        else:
            p_err = self.cshbx.re_some.match(line)
        return (n, p, c, n_err, p_err, c_err)


    def color_text(self, buffer, line_start, n, p, c, n_err, p_err, c_err,
                   double_name=None, name_to_long=None):
        """
        Checks the line in <buffer> starting at <line_start>, that represent an article.
        Uses the regex results <n> (name), <p> (price) and <c> (optional count) and
        the corresponding errors if the regex failed.
        Returns a list of hints to fix the errors.

        green: ok
        orange: the marked text could be used if another part would be fixed
        red: the text itself must be fixed
        """
        def apply_tag(start,end,tag):
            iter_start = buffer.get_iter_at_offset(line_start + start)
            iter_end = buffer.get_iter_at_offset(line_start + end)
            buffer.apply_tag(tag, iter_start, iter_end)

        error=[]
        if p and n and c and not double_name and not name_to_long:
            apply_tag(n.start(2), n.end(2), self.green_tag)
            apply_tag(p.start(1), p.end(5), self.green_tag)
            apply_tag(p.end(5)+c.start(2), p.end(5)+c.end(2), self.green_tag)
        else:
            if p:
                apply_tag(p.start(0), p.end(1), self.orange_tag)
                if n:
                    if name_to_long:
                        error+=[f(_("name {name_to_long} chars to long"))]
                        apply_tag(n.start(2), n.end(2), self.red_tag)
                    elif double_name:
                        error+=[_("name already exists")]
                        apply_tag(n.start(2), n.end(2), self.orange_tag)
                    else:
                        apply_tag(n.start(2), n.end(2), self.orange_tag)
                elif n_err:
                    apply_tag(n_err.start(2), n_err.end(2), self.red_tag)
                    error+=[_("no space after article name")]
                else:
                    error+=[_("no article name")]
                if c:
                    apply_tag(c.start(2)+p.end(4), c.end(2)+p.end(4), self.orange_tag)
                elif c_err:
                    apply_tag(c_err.start(2)+p.end(5), c_err.end(2)+p.end(5), self.red_tag)
                    error+=[_("bad optional count")]
            elif p_err:
                apply_tag(p_err.start(0), p_err.end(0), self.red_tag)
                error+=[_("no price found")]

        return error

    def on_buffer_changed(self, buffer):
        self.check_buffer()

    def check_buffer(self):
        """
        check text buffer and return the current sale represented
        by the the buffer.

        if buffer2sale == True:
            write widget-buffer to sale
        """

        def get_text(start,end):
            return line[start:end]

        self.sale.clear()

        # clear color tags
        (iter1,iter2)=self.buffer.get_bounds()
        self.buffer.remove_all_tags(iter1, iter2)
        text=self.buffer.get_text(iter1, iter2 , False)

        hint=""
        if text == "":
            hint=_("please add lines with article and price")
        else:
            names=[]
            line_start=0 # start of current line in text
            for (line_nr, line) in enumerate(text.splitlines()):

                cursor=self.buffer.get_property("cursor-position")

                if line_start <= cursor <= line_start+len(line):
                    self.cursor_seen_in_line=(line_start,line_start+len(line))

                if line.lstrip()[:1] == "#":
                    # comment starting with "#"
                    self.sale.main_list.append( Comment(line) )
                else:
                    # n=article name, p=article price, c=article count
                    (n, p, c, n_err, p_err, c_err) = self.check_buffer_line(line)

                    double_name=None
                    name_to_long=None
                    if n:
                        name=get_text(n.start(2),n.end(2))
                        if name in names:
                            double_name=name
                        name_to_long = len(name) - appargs.max_name_len
                        if name_to_long <= 0:
                            name_to_long=None
                    error = self.color_text(self.buffer, line_start, n, p, c, n_err, p_err, c_err,
                                            double_name=double_name, name_to_long=name_to_long)

                    if p and n and c and not double_name and not name_to_long:
                        names.append(name)
                        article=Article(name, str2cent(get_text(p.start(2), p.end(2)) +
                                        "." + get_text(p.start(4), p.end(4))),
                                        int("0" + get_text(p.end(5) + c.start(2)
                                        ,p.end(5) + c.end(2))))
                        #eprint(f"article=<{article}>")
                        self.sale.main_list.append(article)
                    else:
                        # error: give error message, but handled like a comment
                        self.sale.main_list.append( Comment(line) )

                    if line_start <= cursor <= line_start+len(line) and error:
                        hint = f"line {line_nr+1}: "+", ".join(error)

                line_start+=len(line)+1

        self.error.set_label(hint)


    def on_save_dialog(self, action, param):
        self.file_dialog.save(None, None, self.on_save_dialog_finish)

    def on_save_dialog_finish(self, dialog, task):
        file=dialog.save_finish(task)

        (iter1,iter2)=self.buffer.get_bounds()
        text=self.buffer.get_text(iter1, iter2 , False)

        path=file.get_path()
        if not path.endswith(appargs.conf_suffix):
            path=path+appargs.conf_suffix

        with open(path, 'w') as p:
            p.write(text)

    def on_load_dialog(self, action, param):
        self.file_dialog.open(None, None, self.on_load_dialog_finish)

    def on_load_dialog_finish(self, dialog, task):
        file=dialog.open_finish(task)
        (iter1,iter2)=self.buffer.get_bounds()
        with open(file.get_path(), 'r') as p:
            data = p.read()
            self.buffer.delete(iter1, iter2)
            self.buffer.insert(iter1, data)

    def on_append_dialog(self, action, param):
        self.file_dialog.open(None, None, self.on_append_dialog_finish)

    def on_help_workflow(self, action, _param):
        d = DialogWidget()
        win=self
        d.help_dialog(win, _("pricelist workflow"), f(_("""\
{d.As} are listed in a text with {d.n} and {d.p} and an optional {d.c} in {d.Pl}. \
This text can be directly edited. It can also contain blank lines and comments. \
The text can be saved, loaded and appended with with the hamburger file menu. \
The  hamburger menu has Undo and Redo buttons to return to a previous state.

It is possible to enter all {d.as_} before starting with {d.S}, or to enter \
each {d.a} when it is sold, or a mixture of both methods.

It may also be possible to make a photo of a table of prices, and to use ocr \
software to extract text from the photo, before running {d.C}. The text can \
then be loaded in {d.Pl}. Then {d.ns} and {d.ps} can be copied and pasted \
to the needed syntax.""")))

    def on_help_syntax(self, action, param):
        d = DialogWidget()
        win=self
        d.help_dialog(win, _("pricelist syntax"), f(_("""\
{d.Pl} mainly consists of a large text field, where a line can represents an \
{d.a}. Lines can also be empty or contain a comment.

A line with an {d.a} contains a {d.n} and {d.p} and an optional {d.c} \
separated by spaces. Lines starting with '#' are comments. 

The {d.p} consists of digits followed by '.' or ',' and 2 additional digits. \
Text before the {d.p} is the {d.n}. The {d.p} may be followed by digits \
that represents a {d.c} to show how often the {d.a} is currently sold.""")))

    def on_append_dialog_finish(self, dialog, task):
        file=dialog.open_finish(task)
        (iter1,iter2)=self.buffer.get_bounds()
        with open(file.get_path(), 'r') as p:
            data = p.read()
            self.buffer.insert(iter2, '\n'+data)

    def read_files(self, files):
        if files:
            with open(files[0], 'r') as p:
                data = p.read()
                self.buffer.set_text(data)

if __name__ == '__main__':
    import doctest
    from app import App, MinWindow

    doctest.testmod()

    class PricelistWindow(MinWindow):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            app = kwargs["application"]

            sale = Sale()

            pricelist_widget = PricelistWidget(sale, win=self)
            self.set_content(pricelist_widget)

            #style_manager = app.get_style_manager()
            #style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
            #style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

            if appargs.moreargs:
                # read testdata from file
                pricelist_widget.read_files(appargs.moreargs)
            else:
                # create minimal testdata now
                article = [("Banana", 1.10, 1), ("Apple", 2.0, 0)]
                for a in article:
                    sale.main_list.append(Article( a[0], a[1], a[2] ))

    class MyApp(App):

        def on_activate(self, app):
            self.win = PricelistWindow(application=app)
            self.win.present()

    app = MyApp()
    app.run(sys.argv)
