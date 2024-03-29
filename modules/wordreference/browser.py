# -*- coding: utf-8 -*-

# Copyright(C) 2012 Lucien Loiseau
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


import urllib

from weboob.tools.browser import BaseBrowser

from .pages import TranslatePage


__all__ = ['WordReferenceBrowser']


class WordReferenceBrowser(BaseBrowser):
    DOMAIN = 'www.wordreference.com'
    ENCODING = 'UTF-8'
    USER_AGENT = BaseBrowser.USER_AGENTS['desktop_firefox']
    PAGES = {
        'https?://www\.wordreference\.com/.*/.*': TranslatePage
        }
    
    def __init__(self, *args, **kwargs):
        BaseBrowser.__init__(self, *args, **kwargs)

    def translate(self, source, to, text):
        """
        translate 'text' from 'source' language to 'to' language
        """
        sl   = source.encode('utf-8')
        tl   = to.encode('utf-8')
        text = text.encode('utf-8')
        self.location('http://'+self.DOMAIN+'/'+sl+tl+'/'+urllib.quote(text))
        translation = self.page.get_translation()
        return translation
