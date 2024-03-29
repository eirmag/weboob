# -*- coding: utf-8 -*-

# Copyright(C) 2009-2012  Jeremy Monnet
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

from weboob.capabilities.library import ICapBook, Book
from weboob.tools.application.repl import ReplApplication
from weboob.tools.application.formatters.iformatter import PrettyFormatter
import sys

__all__ = ['Boobooks']


class RentedListFormatter(PrettyFormatter):
    MANDATORY_FIELDS = ('id', 'date', 'author', 'name', 'late')

    RED   = '[1;31m'

    def get_title(self, obj):
        s = u'%s — %s (%s)' % (obj.author, obj.name, obj.date)
        if obj.late:
            s += u' %sLATE!%s' % (self.RED, self.NC)
        return s

class Boobooks(ReplApplication):
    APPNAME = 'boobooks'
    VERSION = '0.e'
    COPYRIGHT = 'Copyright(C) 2012 Jeremy Monnet'
    CAPS = ICapBook
    DESCRIPTION = "Console application allowing to list your books rented or booked at the library, " \
                  "book and search new ones, get your booking history (if available)."
    EXTRA_FORMATTERS = {'rented_list':   RentedListFormatter,
                        }
    DEFAULT_FORMATTER = 'table'
    COMMANDS_FORMATTERS = {'ls':          'rented_list',
                           'list':        'rented_list',
                          }

    COLLECTION_OBJECTS = (Book, )

    def do_renew(self, id):
        """
        renew ID

        Renew a book
        """

        id, backend_name = self.parse_id(id)
        if not id:
            print >>sys.stderr, 'Error: please give a book ID (hint: use ls command)'
            return 2
        names = (backend_name,) if backend_name is not None else None

        for backend, renew in self.do('renew_book', id, backends=names):
            self.format(renew)
        self.flush()
