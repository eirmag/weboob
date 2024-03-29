"browser for presseurop website"
# -*- coding: utf-8 -*-

# Copyright(C) 2012  Florent Fourcot
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

from .pages.article import PresseuropPage, CartoonPage, DailyTitlesPage
from weboob.tools.browser import BaseBrowser
from weboob.tools.ordereddict import OrderedDict


class NewspaperPresseuropBrowser(BaseBrowser):
    "NewspaperPresseuropBrowser class"
    PAGES = OrderedDict((
             ("http://www.presseurop.eu/.*/todays-front-pages/.*", DailyTitlesPage),
             ("http://www.presseurop.eu/.*/front-page/.*", DailyTitlesPage),
             ("http://www.presseurop.eu/.*/cartoon/.*", CartoonPage),
             ("http://www.presseurop.eu/.*", PresseuropPage),
            ))

    def is_logged(self):
        return False

    def login(self):
        pass

    def fillobj(self, obj, fields):
        pass

    def get_content(self, _id):
        "return page article content"
        self.location(_id)
        return self.page.get_article(_id)
