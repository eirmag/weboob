# -*- coding: utf-8 -*-

# Copyright(C) 2010-2011 Christophe Benz
#
# This file is part of weboob.
#
# weboob is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# weboob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with weboob. If not, see <http://www.gnu.org/licenses/>.


try:
    from collections import OrderedDict
except ImportError:
    try:
        from simplejson import OrderedDict  # NOQA
    except ImportError:
        try:
            from ordereddict import OrderedDict  # NOQA
        except ImportError:
            ## {{{ http://code.activestate.com/recipes/576693/ (r6)
            from UserDict import DictMixin

            class OrderedDict(dict, DictMixin):  # NOQA
                def __init__(self, *args, **kwds):
                    if len(args) > 1:
                        raise TypeError('expected at most 1 arguments, got %d' % len(args))
                    try:
                        self.__end
                    except AttributeError:
                        self.clear()
                    self.update(*args, **kwds)

                def clear(self):
                    self.__end = end = []
                    end += [None, end, end]         # sentinel node for doubly linked list
                    self.__map = {}                 # key --> [key, prev, next]
                    dict.clear(self)

                def __setitem__(self, key, value):
                    if key not in self:
                        end = self.__end
                        curr = end[1]
                        curr[2] = end[1] = self.__map[key] = [key, curr, end]
                    dict.__setitem__(self, key, value)

                def __delitem__(self, key):
                    dict.__delitem__(self, key)
                    key, prev, next = self.__map.pop(key)
                    prev[2] = next
                    next[1] = prev

                def __iter__(self):
                    end = self.__end
                    curr = end[2]
                    while curr is not end:
                        yield curr[0]
                        curr = curr[2]

                def __reversed__(self):
                    end = self.__end
                    curr = end[1]
                    while curr is not end:
                        yield curr[0]
                        curr = curr[1]

                def popitem(self, last=True):
                    if not self:
                        raise KeyError('dictionary is empty')
                    if last:
                        key = reversed(self).next()
                    else:
                        key = iter(self).next()
                    value = self.pop(key)
                    return key, value

                def __reduce__(self):
                    items = [[k, self[k]] for k in self]
                    tmp = self.__map, self.__end
                    del self.__map, self.__end
                    inst_dict = vars(self).copy()
                    self.__map, self.__end = tmp
                    if inst_dict:
                        return (self.__class__, (items,), inst_dict)
                    return self.__class__, (items,)

                def keys(self):
                    return list(self)

                setdefault = DictMixin.setdefault
                update = DictMixin.update
                pop = DictMixin.pop
                values = DictMixin.values
                items = DictMixin.items
                iterkeys = DictMixin.iterkeys
                itervalues = DictMixin.itervalues
                iteritems = DictMixin.iteritems

                def __repr__(self):
                    if not self:
                        return '%s()' % (self.__class__.__name__,)
                    return '%s(%r)' % (self.__class__.__name__, self.items())

                def copy(self):
                    return self.__class__(self)

                @classmethod
                def fromkeys(cls, iterable, value=None):
                    d = cls()
                    for key in iterable:
                        d[key] = value
                    return d

                def __eq__(self, other):
                    if isinstance(other, OrderedDict):
                        return len(self) == len(other) and self.items() == other.items()
                    return dict.__eq__(self, other)

                def __ne__(self, other):
                    return not self == other
            ## end of http://code.activestate.com/recipes/576693/ }}}
