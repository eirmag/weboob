# -*- coding: utf-8 -*-

# Copyright(C) 2010-2011 Clément Schreiner
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

import datetime
import feedparser
if feedparser.__version__ >= '5.0':
    # feedparser >= 5.0 replaces this regexp on sgmllib and mechanize < 2.0
    # fails with malformated webpages.
    import sgmllib
    import re
    sgmllib.endbracket = re.compile('[<>]')

__all__ = ['Entry', 'Newsfeed']


class Entry(object):
    def __init__(self, entry, rssid_func=None):
        if hasattr(entry, 'id'):
            self.id = entry.id
        else:
            self.id = None

        if "link" in entry:
            self.link = entry["link"]
        else:
            self.link = None

        if "title" in entry:
            self.title = entry["title"]
        else:
            self.title = None

        if "author" in entry:
            self.author = entry["author"]
        else:
            self.author = None

        if "updated_parsed" in entry:
            self.datetime = datetime.datetime(*entry['updated_parsed'][:7])
        elif "published_parsed" in entry:
            self.datetime = datetime.datetime(*entry['published_parsed'][:7])
        else:
            self.datetime = None

        if "summary" in entry:
            self.summary = entry["summary"]
        else:
            self.summary = None

        self.content = []
        if "content" in entry:
            for i in entry["content"]:
                self.content.append(i.value)
        elif self.summary:
            self.content.append(self.summary)

        if "wfw_commentrss" in entry:
            self.rsscomment = entry["wfw_commentrss"]
        else:
            self.rsscomment = None

        if rssid_func:
            self.id = rssid_func(self)


class Newsfeed(object):
    def __init__(self, url, rssid_func=None):
        self.feed = feedparser.parse(url)
        self.rssid_func = rssid_func

    def iter_entries(self):
        for entry in self.feed['entries']:
            yield Entry(entry, self.rssid_func)

    def get_entry(self, id):
        for entry in self.feed['entries']:
            if entry.id == id:
                return Entry(entry, self.rssid_func)
