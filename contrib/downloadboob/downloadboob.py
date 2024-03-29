#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright(C) 2012 Alexandre Flament
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

import subprocess
import os
import re

import ConfigParser

from weboob.core import Weboob
from weboob.capabilities.video import ICapVideo

# hack to workaround bash redirection and encoding problem
import sys, codecs, locale

if sys.stdout.encoding is None:
    (lang, enc) = locale.getdefaultlocale()
    if enc is not None:
        (e, d, sr, sw) = codecs.lookup(enc)
        # sw will encode Unicode data to the locale-specific character set.
        sys.stdout = sw(sys.stdout)

# end of hack

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

rx = re.compile(u'[ \\/\\?\\:\\>\\<\\!\\\\\\*]+', re.UNICODE)
def removeSpecial(s):
    return rx.sub(u' ', u'%s' % s)

DOWNLOAD_DIRECTORY=".files"

class Downloadboob:

    def __init__(self, backend_name, download_directory, links_directory):
        self.download_directory = download_directory
        self.links_directory = links_directory
        self.backend_name = backend_name
        self.backend = None
        self.weboob = Weboob()
        self.weboob.load_backends(modules=[self.backend_name])
        self.backend=self.weboob.get_backend(self.backend_name)

    def purge(self):
        if not os.path.isdir(self.links_directory):
            return
        dirList=os.listdir(self.links_directory)
        for local_link_name in dirList:
            link_name = self.links_directory + "/" + local_link_name
            if not self.check_link(link_name):
                print u"Remove %s" % link_name
                os.remove(link_name)
            else:
                print u"Keep %s" % link_name

    def check_link(self, link_name):
        if os.path.islink(link_name):
            file_name = os.readlink(link_name)
            absolute_file_name = os.path.join(self.links_directory, file_name)
            if os.path.isfile(absolute_file_name):
                return True
            return False
        else:
            return True

    def download(self, pattern=None, sortby=ICapVideo.SEARCH_RELEVANCE, nsfw=False, max_results=None, title_exclude=[]):

        print "For backend %s, search for '%s'" % (backend_name, pattern)

        # create directory for links
        print "  create link to %s" % self.links_directory
        if not os.path.isdir(self.links_directory):
            os.makedirs(self.links_directory)

        # search for videos
        count = 0
        videos = []
        l = list(self.backend.search_videos(pattern, sortby, nsfw, max_results))
        for video in l:
            if not self.is_downloaded(video):
                self.backend.fill_video(video, ('url','title', 'url', 'duration'))
                if not(self.is_excluded(video.title, title_exclude)):
                    print "  %s\n    Id:%s\n    Duration:%s" % (video.title, video.id, video.duration)
                    videos.append(video)
            else:
                print "Already downloaded, check %s" % video.id
                self.backend.fill_video(video, ('url','title', 'url', 'duration'))
                self.set_linkname(video)

            count=count+1
            if count == max_results:
                break

        # download videos
        print "Downloading..."
        for video in videos:
            self.do_download(video)

    def is_excluded(self, title, title_exclude):
        for exclude in title_exclude:
            if title.find(exclude) > -1:
                return True
        return False

    def get_filename(self, video, relative=False):
        if relative:
            directory = os.path.join("..", DOWNLOAD_DIRECTORY, self.backend_name)
        else:
            directory = os.path.join(self.download_directory, self.backend_name)

        if not os.path.exists(directory):
            os.makedirs(directory)

        ext = video.ext
        if not ext:
            ext = 'avi'

        return u"%s/%s.%s" % (directory, removeNonAscii(video.id), ext)


    def get_linkname(self, video):
        if not os.path.exists(self.links_directory):
            os.makedirs(self.links_directory)

        ext = video.ext
        if not ext:
            ext = 'avi'

        misc = video.date
        if not misc:
            misc = video.id

        return u"%s/%s (%s).%s" % (self.links_directory, removeSpecial(video.title), removeSpecial(misc), ext)


    def is_downloaded(self, video):
        # check if the file is 0 byte
        return os.path.isfile(self.get_filename(video))


    def set_linkname(self, video):
        linkname = self.get_linkname(video)
        idname = self.get_filename(video, relative=True)
        absolute_idname = self.get_filename(video, relative=False)
        if not os.path.islink(linkname) and os.path.isfile(absolute_idname):
            print "%s -> %s" % (linkname, idname)
            os.symlink(idname, linkname)


    def do_download(self, video):
        if not video:
            print >>sys.stderr, 'Video not found: %s' %  video
            return 3

        if not video.url:
            print >>sys.stderr, 'Error: the direct URL is not available.'
            return 4

        def check_exec(executable):
            with open('/dev/null', 'w') as devnull:
                process = subprocess.Popen(['which', executable], stdout=devnull)
                if process.wait() != 0:
                    print >>sys.stderr, 'Please install "%s"' % executable
                    return False
            return True

        dest = self.get_filename(video)

        if video.url.startswith('rtmp'):
            if not check_exec('rtmpdump'):
                return 1
            args = ('rtmpdump', '-e', '-r', video.url, '-o', dest)
        elif video.url.startswith('mms'):
            if not check_exec('mimms'):
                return 1
            args = ('mimms', video.url, dest)
        else:
            if not check_exec('wget'):
                return 1
            args = ('wget', video.url, '-O', dest)

        os.spawnlp(os.P_WAIT, args[0], *args)


config = ConfigParser.ConfigParser()
config.read(['/etc/downloadboob.conf', os.path.expanduser('~/downloadboob.conf'), 'downloadboob.conf'])

links_directory=os.path.expanduser(config.get('main','directory', '.'))
links_directory=links_directory.decode('utf-8')

download_directory=os.path.join(links_directory, DOWNLOAD_DIRECTORY)

print "Downloading to %s" % (links_directory)

for section in config.sections():
    if section != "main":
        backend_name=config.get(section, "backend")
        pattern=config.get(section, "pattern")
        if config.has_option(section, "title_exclude"):
            title_exclude=config.get(section, "title_exclude").split('|')
        else:
            title_exclude=[]
        max_result=config.getint(section, "max_results")
        section_sublinks_directory=config.get(section,"directory")
        section_links_directory=os.path.join(links_directory, section_sublinks_directory)

        downloadboob = Downloadboob(backend_name, download_directory, section_links_directory)
        downloadboob.purge()
        # FIXME sortBy, title.match
        downloadboob.download(pattern, ICapVideo.SEARCH_DATE, False, max_result, title_exclude)
