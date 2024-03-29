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


from __future__ import with_statement

import os
import tempfile
import logging
import yaml

try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader  # NOQA
    from yaml import Dumper  # NOQA

from .iconfig import IConfig, ConfigError


__all__ = ['YamlConfig']


class YamlConfig(IConfig):
    def __init__(self, path):
        self.path = path
        self.values = {}

    def load(self, default={}):
        self.values = default.copy()

        logging.debug(u'Loading application configuration file: %s.' % self.path)
        try:
            with open(self.path, 'r') as f:
                self.values = yaml.load(f, Loader=Loader)
            logging.debug(u'Application configuration file loaded: %s.' % self.path)
        except IOError:
            self.save()
            logging.debug(u'Application configuration file created with default values: %s. Please customize it.' % self.path)

        if self.values is None:
            self.values = {}

    def save(self):
        # write in a temporary file to avoid corruption problems
        fd, path = tempfile.mkstemp(dir=os.path.dirname(self.path))
        with os.fdopen(fd, 'w') as f:
            yaml.dump(self.values, f, Dumper=Dumper)
        os.rename(path, self.path)

    def get(self, *args, **kwargs):
        default = None
        if 'default' in kwargs:
            default = kwargs['default']

        v = self.values
        for a in args[:-1]:
            try:
                v = v[a]
            except KeyError:
                if not default is None:
                    v[a] = {}
                    v = v[a]
                else:
                    raise ConfigError()
            except TypeError:
                raise ConfigError()

        try:
            v = v[args[-1]]
        except KeyError:
            v = default

        return v

    def set(self, *args):
        v = self.values
        for a in args[:-2]:
            try:
                v = v[a]
            except KeyError:
                v[a] = {}
                v = v[a]
            except TypeError:
                raise ConfigError()

        v[args[-2]] = args[-1]

    def delete(self, *args):
        v = self.values
        for a in args[:-1]:
            try:
                v = v[a]
            except KeyError:
                return
            except TypeError:
                raise ConfigError()

        v.pop(args[-1], None)
