# -*- coding: utf-8 -*-

"""
Copyright(C) 2010  Romain Bignon

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""

from weboob.backend import Backend
from weboob.capabilities.messages import ICapMessages, ICapMessagesReply, Message
from weboob.capabilities.updatable import ICapUpdatable
from feeds import ArticlesList

class DLFPBackend(Backend, ICapMessages, ICapMessagesReply, ICapUpdatable):
    MAINTAINER = 'Romain Bignon'
    EMAIL = 'romain@peerfuse.org'
    VERSION = '1.0'
    LICENSE = 'GPLv3'

    def iter_messages(self):
        articles_list = ArticlesList('newspaper')
        for article in articles_list.iter_articles():
            yield Message('threadid', article.id, article.title, article.author, signature='Bite bite bite bite',
                          content='Content content\nContent content.')
