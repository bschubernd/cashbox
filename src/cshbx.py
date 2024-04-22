#!/usr/bin/python3

# cshbx.py
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

import gi, os, sys, re
gi.require_version(namespace='Adw', version='1')
from gi.repository import Adw
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = os.path.dirname(dir1)
sys.path.append(dir1)
from cashbox.read_appargs import read_appargs, appargs
from cashbox.locale_utils import _, f

class Cshbx():
    """
    a text line with an article needs an article name and and a price
    optionally it can contain a count
    """

    def __init__(self):
        re_price = r'(\$\s*|\€\s*|)(\d+)(,|\.)(\d\d)(\s*\$|\s*€|\s*Dollar|\s*Euro|)'
        re_name = r'(\s*)(.*\S)(\s+)'
        re_count = r'(?:(\s+)(\d+)){0,1}(\s*)$'
        self.re_sale = re.compile(r'^'+re_name+re_price+re_count+r'$')

        self.re_price = re.compile(re_price)
        self.re_name = re.compile(r'^' + re_name + r'$')
        self.re_count = re.compile(r'^' + re_count + r'$')
        self.re_some=re.compile(r'^(\s*)(.*\S)(\s*)$')

    def get_cent_price(self, line):
        res=0
        match = self.re_sale.match(line)
        if match:
            groups=match.groups()
            if groups[9]:
                res+=(int(groups[4])*appargs.cents + int(groups[6])) * int(groups[9])
        return res

if __name__ == '__main__':
    read_appargs("", sys.argv)
    cshbx = Cshbx()

    assert cshbx.re_price.match("1,20").groups() == ('', '1', ',', '20', '')
    assert cshbx.re_price.match("1.20 Dollar").groups() == ('', '1', '.', '20', ' Dollar')
    assert list(cshbx.re_price.finditer("Bier 0,25 Liter 1,10€"))[-1].groups() == ('', '1', ',', '10', '€')
    assert list(cshbx.re_price.finditer("0.25 Dollar"))[-1].groups() == ('', '0', '.', '25', ' Dollar')
    assert list(cshbx.re_price.finditer("$0.25 Dollar"))[-1].groups() == ('$', '0', '.', '25', ' Dollar')

    assert cshbx.get_cent_price("garbage") == 0
    assert cshbx.get_cent_price("a 1,20 5") == 600

    assert cshbx.re_price.match("12,34").groups() == ('', '12', ',', '34', '')
    assert cshbx.re_price.match("12,34 €").groups() == ('', '12', ',', '34', ' €')
    assert cshbx.re_price.match("12.34$").groups() == ('', '12', '.', '34', '$')
    assert cshbx.re_price.match("12.3") is  None

    print("all asserts have been ok")
