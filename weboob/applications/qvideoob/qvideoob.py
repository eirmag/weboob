# -*- coding: utf-8 -*-

# Copyright(C) 2010-2011 Romain Bignon
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


from weboob.capabilities.video import ICapVideo
from weboob.tools.application.qt import QtApplication

from .main_window import MainWindow

class QVideoob(QtApplication):
    APPNAME = 'qvideoob'
    VERSION = '0.e'
    COPYRIGHT = 'Copyright(C) 2010-2011 Romain Bignon'
    DESCRIPTION = 'Qt application allowing to search videos on various websites and play them.'
    CAPS = ICapVideo
    CONFIG = {'settings': {'nsfw': 1,
                           'sfw': 1,
                           'sortby': 0,
                           'backend': ''
                          }
             }
    def main(self, argv):
        self.load_backends(ICapVideo)
        self.load_config()

        self.main_window = MainWindow(self.config, self.weboob)
        self.main_window.show()
        return self.weboob.loop()
