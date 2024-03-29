# -*- coding: utf-8 -*-

# Copyright(C) 2010-2012 Romain Bignon
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


from weboob.capabilities.dating import ICapDating
from weboob.tools.application.qt import QtApplication

from .main_window import MainWindow

class QHaveDate(QtApplication):
    APPNAME = 'qhavedate'
    VERSION = '0.e'
    COPYRIGHT = 'Copyright(C) 2010-2012 Romain Bignon'
    DESCRIPTION = 'Qt application allowing to interact with various dating websites.'
    CAPS = ICapDating
    STORAGE_FILENAME = 'dating.storage'

    def main(self, argv):
        self.create_storage(self.STORAGE_FILENAME)
        self.load_backends(ICapDating)

        self.main_window = MainWindow(self.config, self.weboob)
        self.main_window.show()
        return self.weboob.loop()
