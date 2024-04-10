#!/usr/bin/python3

# edit_pricelist_widget.py - edit pricelist with Gtk.TextView for cashbox
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

import os, sys, re, gi
gi.require_version(namespace='Adw', version='1')
from gi.repository import Adw, Gtk, GObject, Gio, GLib
#from gi.repository import Gtk, Adw, Gio, Gdk, Graphene, GLib
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)
from cashbox.utils import eprint, print_widget
from cashbox.article import Article, Sale, str2cent
from cashbox.drop_down_widget import DropDownWidget
from cashbox.read_css import read_css
from cashbox.read_appargs import read_appargs, appargs

def article_regex():
    """
    a text line with an article needs an article name and and a price
    optionally it can contain a count
    >>> (re_price, re_name, re_count, re_some) = article_regex()

    a price must not contain Spaces at begin nor at end:
    >>> re_price.match("12,34").groups()
    ('12', ',', '34', '')
    >>> re_price.match("12,34 €").groups()
    ('12', ',', '34', ' €')
    >>> re_price.match("12.34$").groups()
    ('12', '.', '34', '$')
    >>> print(re_price.match("12.3"))
    None

    an article name must end with spaces to be separated from the price:
    >>> re_name.match(" my article ").groups()
    (' ', 'my article', ' ')
    >>> print(re_name.match(" my article"))
    None

    a count is optional
    >>> re_count.match("").groups()
    (None, None, '')

    but must have spaces before and can have spaces after it
    >>> re_count.match(" 42  ").groups()
    (' ', '42', '  ')

    """

    # group(X); X=          1    2    3     4
    re_price = re.compile(r'(\d+)(,|\.)(\d\d)(\s*\$|\s*€|)')
    # group(X); X=          1    2     3
    #re_name = re.compile(r'^(\s*)(.*\S)(\s+|\s*[:=>]+\s*)$')
    re_name = re.compile(r'^(\s*)(.*\S)(\s+)$')
    # group(X); X=              1    2          3
    re_count = re.compile(r'^(?:(\s+)(\d+)){0,1}(\s*)$')
    # group(X); X=        1    2     3
    re_some=re.compile(r'^(\s*)(.*\S)(\s*)$')
    return (re_price, re_name, re_count, re_some)


@Gtk.Template(filename='%s/edit_pricelist_widget.ui' % dir1)
class EditPricelistWidget(Gtk.Box):
    __gtype_name__ = 'EditPricelistWidget'
    textview = Gtk.Template.Child()
    error = Gtk.Template.Child()
    file_dialog = Gtk.Template.Child() # Gtk.FileDialog
    cashbox_file_filter = Gtk.Template.Child()
    red_tag = Gtk.Template.Child()
    green_tag = Gtk.Template.Child()
    orange_tag = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_unmap_all(self, widget):
        self.check_buffer(True)

    @Gtk.Template.Callback()
    def on_map_all(self, widget):
        # write sale-variable to widget-buffer
        self.buffer.set_text(self.sale.text())

    def __init__(self, sale, win, **kwargs):
        super().__init__(**kwargs)

        self.sale=sale
        self.buffer=self.textview.get_buffer()
        self.table=self.buffer.get_tag_table()
        self.prepare_regex()

        for (a,b) in [ ("undo", self.on_undo_action),
                       ("save", self.on_save_dialog),
                       ("load", self.on_load_dialog),
                       ("append", self.on_append_dialog) ]:
            action = Gio.SimpleAction.new(a, None)
            action.connect("activate", b)
            win.add_action(action)

        self.table.add(self.red_tag)
        self.table.add(self.green_tag)
        self.table.add(self.orange_tag)

        self.buffer.connect('changed', self.on_buffer_changed)
        self.check_buffer(False)
        self.buffer.connect('notify::cursor-position', self.on_cursor)

        self.cursor_seen_in_line=(-1,-1)

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(self.cashbox_file_filter)

        self.file_dialog.set_filters(filters)
        self.file_dialog.set_initial_folder(Gio.File.new_for_path(appargs.user_app_dir))


    def on_undo_action(self, action, param):
        #print("undo")
        self.buffer.set_text(self.sale.text())
        #eprint("self.sale=<%s>"% self.sale)

    def on_cursor(self, buffer, pos):
        pos=buffer.get_property("cursor-position")
        (a,b)=self.cursor_seen_in_line
        if pos<a or pos>b:
            self.check_buffer(False)

    def prepare_regex(self):
        (self.re_price, self.re_name, self.re_count, self.re_some) = article_regex()

    def check_buffer_line(self, line):
        # n=article name, p=article price, c=article count
        (n, p, c, n_err, p_err, c_err) = (None, None, None, None, None, None)
        p = self.re_price.search(line)
        if p:
            a_line=line[:p.start(0)]
            n = self.re_name.match(a_line)
            if not n:
                n_err = self.re_some.match(a_line)

            c_line=line[p.end(0):]
            c = self.re_count.match(c_line)
            if not c:
               c_err = self.re_some.match(c_line)
        else:
           p_err = self.re_some.match(line)
        return (n, p, c, n_err, p_err, c_err)


    def color_text(self, buffer, line_start, n, p, c, n_err, p_err, c_err, double_name=None, name_to_long=None):
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
            apply_tag(p.start(1), p.end(4), self.green_tag)
            apply_tag(p.end(4)+c.start(2), p.end(4)+c.end(2), self.green_tag)
        else:
            if p:
                apply_tag(p.start(0), p.end(0), self.orange_tag)
                if n:
                    #print(f"color_text: name_to_long=<{name_to_long}>")
                    if name_to_long:
                        error+=[f"name {name_to_long} chars to long"]
                        apply_tag(n.start(2), n.end(2), self.red_tag)
                    elif double_name:
                        error+=["name already exists"]
                        apply_tag(n.start(2), n.end(2), self.orange_tag)
                    else:
                        apply_tag(n.start(2), n.end(2), self.orange_tag)
                elif n_err:
                    apply_tag(n_err.start(2), n_err.end(2), self.red_tag)
                    error+=["no space after article name"]
                else:
                    error+=["no article name"]
                if c:
                    apply_tag(c.start(2)+p.end(4), c.end(2)+p.end(4), self.orange_tag)
                elif c_err:
                    apply_tag(c_err.start(2)+p.end(4), c_err.end(2)+p.end(4), self.red_tag)
                    error+=["bad optional count"]
            elif p_err:
                apply_tag(p_err.start(0), p_err.end(0), self.red_tag)
                error+=["no price found"]

        return error


    def on_buffer_changed(self, buffer):
        print("on_buffer_changed")
        self.check_buffer(False)


    def check_buffer(self, buffer2sale):
        """
        check text buffer and return the current sale represented
        by the the buffer.

        if buffer2sale == True:
            write widget-buffer to sale
        """

        def get_text(start,end):
            return(line[start:end])

        if buffer2sale:
            self.sale.clear()

        # clear color tags
        (iter1,iter2)=self.buffer.get_bounds()
        self.buffer.remove_all_tags(iter1, iter2)
        text=self.buffer.get_text(iter1, iter2 , False)

        hint=""
        if text == "":
            hint="please add lines with article and price"
        else:
            names=[]
            line_start=0 # start of current line in text
            for (line_nr, line) in enumerate(text.splitlines()):
                # n=article name, p=article price, c=article count
                (n, p, c, n_err, p_err, c_err) = self.check_buffer_line(line)

                cursor=self.buffer.get_property("cursor-position")
                if line_start <= cursor and cursor <= line_start+len(line):
                    self.cursor_seen_in_line=(line_start,line_start+len(line))

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
                    article=Article(name, str2cent(get_text(p.start(1),p.end(1)) + "." + get_text(p.start(3),p.end(3))),
                                    int("0"+get_text(p.end(4)+c.start(2),p.end(4)+c.end(2))) )
                    #eprint(f"article=<{article}>")
                    if buffer2sale:
                        self.sale.main_list.append(article)

                if line_start <= cursor and cursor <= line_start+len(line) and error:
                    hint = f"line {line_nr+1}: "+", ".join(error)

                line_start+=len(line)+1

        self.error.set_label(hint)


    def on_save_dialog(self, action, param):
        #print("on_save_action")
        self.file_dialog.save(None, None, self.on_save_dialog_finish)

    def on_save_dialog_finish(self, dialog, task):
        #print("on_save_dialog_finish: gtk_file_diallog=<%s> gio_task=<%s>" % (dialog, task))
        file=dialog.save_finish(task)

        (iter1,iter2)=self.buffer.get_bounds()
        text=self.buffer.get_text(iter1, iter2 , False)

        path=file.get_path()
        if not path.endswith(appargs.conf_suffix):
            path=path+appargs.conf_suffix

        #print(f"on_save_dialog_finish: file=<{file.get_path()}> text=<{text}>")
        with open(path, 'w') as f:
            f.write(text)

    def on_load_dialog(self, action, param):
        #print("on_load")
        self.file_dialog.open(None, None, self.on_load_dialog_finish)

    def on_load_dialog_finish(self, dialog, task):
        file=dialog.open_finish(task)
        #print(f"on_load_dialog_finish: path=<{file.get_path()}>")
        with open(file.get_path(), 'r') as f:
            data = f.read()
            self.buffer.set_text(data)

    def on_append_dialog(self, action, param):
        #print("on_append")
        self.file_dialog.open(None, None, self.on_append_dialog_finish)

    def on_append_dialog_finish(self, dialog, task):
        file=dialog.open_finish(task)
        (iter1,iter2)=self.buffer.get_bounds()
        text=self.buffer.get_text(iter1, iter2 , False)
        with open(file.get_path(), 'r') as f:
            data = f.read()
            self.buffer.set_text(text+'\n'+data)

    def read_files(self, files):
        if files:
            with open(files[0], 'r') as f:
                data = f.read()
                self.buffer.set_text(data)

if __name__ == '__main__':
    import sys, doctest
    from app import App, MinWindow

    doctest.testmod()

    class EditPricelistWindow(MinWindow):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            app = kwargs["application"]

            sale = Sale()

            edit_pricelist_widget = EditPricelistWidget(sale, win=self)
            self.set_content(edit_pricelist_widget)


            #style_manager = app.get_style_manager()
            #style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
            #style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

            if appargs.moreargs:
                # read testdata from file
                edit_pricelist_widget.read_files(appargs.moreargs)
            else:
                # create minimal testdata now
                article = [("Banana", 1.10, 1), ("Apple", 2.0, 0)]
                for f in article:
                    sale.main_list.append(Article( f[0], f[1], f[2] ))

    class MyApp(App):

        def on_activate(self, app):
            self.win = EditPricelistWindow(application=app)
            self.win.present()

    app = MyApp()
    app.run(sys.argv)
