#!/usr/bin/python3

# article.py - handle data for cashbox
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
import re
gi.require_version(namespace='Adw', version='1')
from gi.repository import Adw, Gtk, Gio, GLib, GObject
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir2)
from cashbox.read_appargs import read_appargs, appargs
from cashbox.data_list import DataList

def cent2str(cents):
    return f"{cents//appargs.cents}{appargs.separator}{cents%appargs.cents:0{appargs.digits}.0f}"

def str2cent(txt, allow_sloppy=False):
    ret=0
    if allow_sloppy:
        txt=txt
        txt=re.sub(r"[.,]", appargs.separator, txt)
    try:
        price=float(txt)
    except:
        return ret
    number_of_digits=str(txt)[::-1].find(appargs.separator)
    if number_of_digits <= appargs.digits:
        ret = int(price * appargs.cents)
    return ret

class Article(GObject.Object):
    name = GObject.Property(type=str)
    price = GObject.Property(type=int)
    count = GObject.Property(type=int)

    def __init__(self, name, price, count=0):
        super().__init__()
        self.name = name
        self.price = price
        self.count = count

    def __str__(self):
        return (f"({self.name},{cent2str(self.price)},{self.count})")

    def text(self):
        if self.count:
            ret=f"{self.name} {cent2str(self.price)} {self.count}"
        else:
            ret=f"{self.name} {cent2str(self.price)}"
        return ret


class Sale(DataList):

    def __init__(self):
        super().__init__()

        # self.main_list
        self.add_plus_list(pick = self.is_picked, selfname="picked") # self.picked
        self.add_plus_list(pick = self.is_unpicked, selfname="unpicked") # self.unpicked
        self.add_plus_list(pick = self.is_unpicked, sort=True,
                           item1=Article("select article", 0, 0),
                           selfname="drop_unpicked") # self.drop_unpicked

    def is_picked(self, item):
        return item.count > 0

    def is_unpicked(self, item):
        return not self.is_picked(item)

    def text(self):
        """
        This will make Sale ediable as text.
        All relevant information is included.
        """
        return "\n".join([article.text() for article in self.main_list])

    def get_article(self, name, picked=None):
        """
        get article with given name or None.
        picked: 
          None: no matter if picked
          False: not picked
          True: picked
        """
        found=None
        for article in self.main_list:
            if article.name==name:
                if picked==True:
                    if article.count>0:
                        found=article
                elif picked==False:
                    if article.count==0:
                        found=article
                elif picked==None:
                    found=article
                break
        return found

    def count_zero(self):
        """
        e.g. start with a new customer, without picked articles
        """
        for article in self.main_list:
            article.count=0

if __name__ == '__main__':
    read_appargs()

    sale = Sale()

    fruits = [("Banana",110,1), ("Apple",200,2), ("Strawberry",250,3), ("Pear",335,4), ("Watermelon",100,5), ("Blueberry",200,6)]
    for f in fruits:
        sale.main_list.append( Article(f[0], f[1], f[2]) )
    assert f"{sale}" == "[(Banana,1.10,1),(Apple,2.00,2),(Strawberry,2.50,3),(Pear,3.35,4),(Watermelon,1.00,5),(Blueberry,2.00,6)]"
    assert f"{sale.text()}" == """Banana 1.10 1
Apple 2.00 2
Strawberry 2.50 3
Pear 3.35 4
Watermelon 1.00 5
Blueberry 2.00 6"""

    # next 2 lines will normally be done by a widget
    a=sale.get_article("Apple", picked=True)
    a.count=0
    assert f"{sale.get_article('Apple', picked=True)}" == "None"
    assert f"{sale.get_article('Apple', picked=False)}" == "(Apple,2.00,0)"

    a.count=3
    assert f"{sale.get_article('Apple', picked=False)}" == "None"
    assert f"{sale.get_article('Apple', picked=True)}" == "(Apple,2.00,3)"
    assert f"{sale.get_article('Apple')}" == "(Apple,2.00,3)"

    assert a.name == "Apple"
    assert a.price == 200
    assert a.count == 3

    print("all asserts have been ok")
