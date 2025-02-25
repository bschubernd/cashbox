#!/usr/bin/python3

# data_list.py
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

""" data_list.py provides class DataList """


import sys
import gi

try:
    gi.require_version(namespace='Adw', version='1')
    from gi.repository import GObject, Gio
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


class DataList():
    """
    A DataList consists of DataItems.
    Consists means the DataList has no copy of the DataItem, but points to the
    DataItem.
    The main DataList (main_list) consists of all DataItems in a sorted order
    (sorted by the user).

    Additional DataLists (plus_list), that may be needed in Widgets, can be
    added and may have automatically calculated and updated parts of the
    DataItems have a changed order of the DataItems,
    or have an added first data that represents a text (line1).

    Advantages:
      * If one DataItem is changed in any DataList, it is automatically changed
        in all other DataLists.
    """

    def __init__(self):
        self.main_list = Gio.ListStore()
        self.plus_lists = []

        # needed to find out deleted DataItems
        self.main_list_last = self.add_plus_list()

        self.main_list.connect('items-changed', self.on_data_list_changed)

    def str(self, data_list):
        """ return string of part of data_list """
        return "[" + ",".join([str(data) for data in data_list]) + "]"

    def __str__(self):
        return self.str(self.main_list)

    def add_plus_list(self, pick=None, sort=False, item1=None, selfname=None):
        """
        pick  None: to contain all DataItem
              function: return True if the given DataItem is picked of False
        sort  True: sort added DataItem in the same order as main_list
              False: add new DataItem to the end
        item1   None: No additional first DataItem
              DataItem: The given DataItem should represent a string if printed
        """
        plus = Gio.ListStore()
        if item1:
            plus.append(item1)
        self.plus_lists.append((plus, pick, sort))
        if selfname:
            setattr(self, selfname, plus)
        return plus

    def on_item_changed(self, item, _field):
        """ if an item changed, plus lists have to be updated """
        self.add_item_to_plus_list_where_needed(item)

    def add_item_to_plus_list_where_needed(self, item):
        """ check to which plus list an item belongs and update them """
        for plus_list, pick, sort in self.plus_lists:
            found, pos = plus_list.find(item)
            if pick:
                if pick(item):
                    if not found:
                        if sort:
                            self.add_item_sorted(item, plus_list)
                        else:
                            plus_list.append(item)
                elif found:
                    plus_list.remove(pos)
            elif not found:
                if sort:
                    self.add_item_sorted(item, plus_list)
                else:
                    plus_list.append(item)

    def del_item_from_plus_list_where_needed(self, item):
        """ check if an item is no longer needed in a plus list """
        for plus_list, _, _ in self.plus_lists:
            found, pos = plus_list.find(item)
            if found:
                plus_list.remove(pos)

    def add_item_sorted(self, item, plus_list, order_list=None):
        """
        >>> order_list = [1,2,3,4,5,6,7,8]
        >>> plus_list = [2,4,6,8]
        >>> DataList.add_item_sorted(None, 5, plus_list, order_list)
        >>> DataList.str(None, plus_list)
        '[2,4,5,6,8]'

        >>> plus_list = ["first",2,4,6,8]
        >>> DataList.add_item_sorted(None, 5, plus_list, order_list)
        >>> DataList.str(None, plus_list)
        '[first,2,4,5,6,8]'

        """
        if order_list is None:
            order_list = self.main_list

        is_break = False
        plus_i = 0
        order_i = 0

        if len(plus_list) >= 1 and not plus_list[0] in order_list:
            # special item1 used
            plus_i = 1

        while plus_i < len(plus_list):
            plus_item = plus_list[plus_i]
            while order_i < len(order_list):
                order_item = order_list[order_i]
                if order_item == item:
                    is_break = True
                    break
                if order_item == plus_item:
                    break
                order_i += 1
            if is_break:
                break
            plus_i += 1
        plus_list.insert(plus_i, item)

    def on_data_list_changed(self, _list_store, position, removed, added):
        """ called when items have changed """
        assert added == 1 or removed == 1
        if added == 1:
            item = self.main_list[position]
            item.connect('notify', self.on_item_changed)
            self.add_item_to_plus_list_where_needed(item)
        elif removed == 1:
            item = self.main_list_last[position]
            self.del_item_from_plus_list_where_needed(item)

    def clear(self):
        """ delete items """
        for _ in range(0, len(self.main_list)):
            # currently only deleting one item at once is allowed by
            #  on_data_list_changed
            self.main_list.remove(0)


if __name__ == '__main__':

    import doctest
    doctest.testmod()

    class Data(GObject.Object):
        """ Test Data """
        name = GObject.Property(type=str)
        count = GObject.Property(type=int)

        def __init__(self, name, count=0):
            super().__init__()
            self.name = name
            self.count = count

            self.picklists = []
            self.unpicklists = []

        def __str__(self):
            if self.count >= 0:
                return f"({self.name},{self.count})"
            # used for DataList.plus_lists to display item1 in a drop down box
            return f"{self.name}"

    def is_picked(item):
        """ test selection rule for plus list """
        return item.count > 0

    def is_unpicked(item):
        """ test selection rule for plus list """
        return not is_picked(item)

    data = DataList()
    main_list = data.main_list
    data.add_plus_list(pick=is_picked, selfname="picked1")
    unpicked1 = data.add_plus_list(pick=is_unpicked)
    unpicked2 = data.add_plus_list(pick=is_unpicked, sort=True,
                                   item1=Data("select item", -1))
    assert f"{data}" == "[]"
    assert f"{data.str(data.main_list)}" == "[]"
    assert f"{data.str(data.main_list_last)}" == "[]"
    assert f"{data.str(data.picked1)}" == "[]"

    assert f"{data.str(unpicked1)}" == "[]"
    assert f"{data.str(unpicked2)}" == "[select item]"

    for (a, b) in [("one", 1), ("two", 2), ("three", 3), ("four", 0)]:
        main_list.append(Data(a, b))
    assert f"{data}" == "[(one,1),(two,2),(three,3),(four,0)]"
    assert f"{data.str(data.main_list)}" == ("[(one,1),(two,2),(three,3),"
                                             "(four,0)]")
    assert f"{data.str(data.main_list_last)}" == ("[(one,1),(two,2),"
                                                  "(three,3),(four,0)]")
    assert f"{data.str(data.picked1)}" == "[(one,1),(two,2),(three,3)]"
    assert f"{data.str(unpicked1)}" == "[(four,0)]"
    assert f"{data.str(unpicked2)}" == "[select item,(four,0)]"

    main_list[0].count = 0
    assert f"{data}" == "[(one,0),(two,2),(three,3),(four,0)]"
    assert f"{data.str(data.main_list)}" == ("[(one,0),(two,2),(three,3),"
                                             "(four,0)]")
    assert f"{data.str(data.main_list_last)}" == ("[(one,0),(two,2),"
                                                  "(three,3),(four,0)]")
    assert f"{data.str(data.picked1)}" == "[(two,2),(three,3)]"
    assert f"{data.str(unpicked1)}" == "[(four,0),(one,0)]"
    assert f"{data.str(unpicked2)}" == "[select item,(one,0),(four,0)]"

    main_list.remove(2)
    assert f"{data}" == "[(one,0),(two,2),(four,0)]"
    assert f"{data.str(data.main_list)}" == "[(one,0),(two,2),(four,0)]"
    assert f"{data.str(data.main_list_last)}" == "[(one,0),(two,2),(four,0)]"
    assert f"{data.str(data.picked1)}" == "[(two,2)]"
    assert f"{data.str(unpicked1)}" == "[(four,0),(one,0)]"
    assert f"{data.str(unpicked2)}" == "[select item,(one,0),(four,0)]"

    print("all asserts have been ok")
