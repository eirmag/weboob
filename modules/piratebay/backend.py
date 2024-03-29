# -*- coding: utf-8 -*-

# Copyright(C) 2010-2011 Julien Veyssier
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

from weboob.capabilities.torrent import ICapTorrent, MagnetOnly
from weboob.tools.backend import BaseBackend
from weboob.capabilities.base import NotAvailable

from .browser import PiratebayBrowser


__all__ = ['PiratebayBackend']

class PiratebayBackend(BaseBackend, ICapTorrent):
    NAME = 'piratebay'
    MAINTAINER = u'Julien Veyssier'
    EMAIL = 'julien.veyssier@aiur.fr'
    VERSION = '0.e'
    DESCRIPTION = 'The Pirate Bay BitTorrent tracker'
    LICENSE = 'AGPLv3+'
    BROWSER = PiratebayBrowser

    def create_default_browser(self):
        return self.create_browser()

    def get_torrent(self, id):
        return self.browser.get_torrent(id)

    def get_torrent_file(self, id):
        torrent = self.browser.get_torrent(id)
        if not torrent:
            return None

        if torrent.url is NotAvailable and torrent.magnet:
            raise MagnetOnly(torrent.magnet)
        return self.browser.openurl(torrent.url.encode('utf-8')).read()

    def iter_torrents(self, pattern):
        return self.browser.iter_torrents(pattern.replace(' ', '+'))
