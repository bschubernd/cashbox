#!/usr/bin/python3

# locale_utils.py
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

""" locale utils """

import os
import gettext
import locale
from copy import copy
from inspect import currentframe


def init_locale():
    """
    Set defaults for global variable "_"
    """
    ret = gettext.gettext  # allow _("...") to mark stings as translateable

    # set locale for all categories as defined in LANG
    locale.setlocale(locale.LC_ALL, "")

    # use local po directory if exists
    locale.bindtextdomain("cashbox", "po/locale" if os.path.isdir("po/locale")
                          else "/usr/share/locale")
    locale.textdomain("cashbox")
    gettext.bindtextdomain("cashbox", "po/locale" if os.path.isdir("po/locale")
                           else "/usr/share/locale")
    gettext.textdomain("cashbox")
    return ret


# init global variable _ to be included by other modules
if "_" not in globals():
    _ = init_locale()


def f(s: str) -> str:
    """
    There are problems when using gettext and f-string:

        name="world"
        _(f"hello {name}")

    This is not possible, because f-string will modify the string.
    And the modified string can not be found in the translation.
    This workaround allows:

        name="world"
        f(_("hello {name}"))

    """
    frame = currentframe().f_back
    kwargs = copy(frame.f_globals)
    kwargs.update(frame.f_locals)
    return s.format(**kwargs)
