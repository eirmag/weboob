"browser for lefigaro website"
# -*- coding: utf-8 -*-

# Copyright(C) 2011  Julien Hebert
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

from .pages.article import ArticlePage
from .pages.flashactu import FlashActuPage
from .pages.special import SpecialPage
from weboob.tools.browser import BaseBrowser, BasePage

class IndexPage(BasePage):
    pass


class NewspaperFigaroBrowser(BaseBrowser):
    "NewspaperFigaroBrowser class"
    PAGES = {
             "http://\w+.lefigaro.fr/flash-.*/(\d{4})/(\d{2})/(\d{2})/(.*$)": FlashActuPage,
             "http://\w+.lefigaro.fr/bd/(\d{4})/(\d{2})/(\d{2})/(.*$)": FlashActuPage,
             "http://\w+.lefigaro.fr/actualite/(\d{4})/(\d{2})/(\d{2})/(.*$)": SpecialPage,
             "http://\w+.lefigaro.fr/(?!flash-|bd|actualite).+/(\d{4})/(\d{2})/(\d{2})/(.*$)": ArticlePage,
             "http://\w+.lefigaro.fr/actualite-.*/(\d{4})/(\d{2})/(\d{2})/(.*$)": ArticlePage,
             "http://\w+.lefigaro.fr/": IndexPage,
            }

    def is_logged(self):
        return False

    def login(self):
        pass

    def fillobj(self, obj, fields):
        pass

    def get_content(self, _id):
        "return page article content"
        self.location(_id)
        if self.is_on_page(IndexPage):
            return None
        return self.page.get_article(_id)
