# -*- coding: utf-8 -*-

# Copyright(C) 2012 Florent Fourcot
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
"backend for http://www.presseurop.eu"

from weboob.capabilities.messages import ICapMessages, Thread
from weboob.tools.capabilities.messages.GenericBackend import GenericNewspaperBackend
from weboob.tools.backend import BackendConfig
from weboob.tools.value import Value
from .browser import NewspaperPresseuropBrowser
from .tools import rssid, url2id
from weboob.tools.newsfeed import Newsfeed


class NewspaperPresseuropBackend(GenericNewspaperBackend, ICapMessages):
    MAINTAINER = u'Florent Fourcot'
    EMAIL = 'weboob@flo.fourcot.fr'
    VERSION = '0.e'
    LICENSE = 'AGPLv3+'
    STORAGE = {'seen': {}}
    NAME = 'presseurop'
    DESCRIPTION = u'Presseurop website'
    BROWSER = NewspaperPresseuropBrowser
    RSSID = staticmethod(rssid)
    URL2ID = staticmethod(url2id)
    RSSSIZE = 140
    CONFIG = BackendConfig(Value('lang', label='Lang of articles',
                           choices={'fr': 'fr', 'de': 'de', 'en': 'en', 'cs': 'cs', 'es': 'es', 'it': 'it', 'nl': 'nl', 'pl': 'pl', 'pt': 'pt', 'ro': 'ro'}, default='fr'))

    def __init__(self, *args, **kwargs):
        GenericNewspaperBackend.__init__(self, *args, **kwargs)
        self.RSS_FEED = 'http://www.presseurop.eu/%s/rss.xml' % (self.config['lang'].get())

    def iter_threads(self):
        for article in Newsfeed(self.RSS_FEED, self.RSSID).iter_entries():
            thread = Thread(article.link)
            thread.title = article.title
            thread.date = article.datetime
            yield(thread)
