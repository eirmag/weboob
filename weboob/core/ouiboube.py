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


from __future__ import with_statement

import os
import shutil

from weboob.core.bcall import BackendsCall
from weboob.core.modules import ModulesLoader, ModuleLoadError
from weboob.core.backendscfg import BackendsConfig
from weboob.core.repositories import Repositories, IProgress
from weboob.core.scheduler import Scheduler
from weboob.tools.backend import BaseBackend
from weboob.tools.log import getLogger


__all__ = ['Weboob']


class Weboob(object):
    """
    The main class of Weboob, used to manage backends and call methods.

    :param workdir: optional parameter to set path of the working directory
    :type workdir: str
    :param backends_filename: name of the *backends* file, where configuration of
                              backends is stored
    :type backends_filename: str
    :param scheduler: what scheduler to use; default is :class:`weboob.core.scheduler.Scheduler`
    :type scheduler: :class:`weboob.core.scheduler.IScheduler`
    :param storage: provide a storage where backends can save data
    :type storage: :class:`weboob.tools.storage.IStorage`
    """
    VERSION = '0.e'
    BACKENDS_FILENAME = 'backends'

    def __init__(self, workdir=None, backends_filename=None, scheduler=None, storage=None):
        self.logger = getLogger('weboob')
        self.backend_instances = {}
        self.callbacks = {'login':   lambda backend_name, value: None,
                          'captcha': lambda backend_name, image: None,
                         }

        # Scheduler
        if scheduler is None:
            scheduler = Scheduler()
        self.scheduler = scheduler

        # Create WORKDIR
        if workdir is not None:
            datadir = workdir
        elif 'WEBOOB_WORKDIR' in os.environ:
            datadir = workdir = os.environ.get('WEBOOB_WORKDIR')
        else:
            old_workdir = os.path.join(os.path.expanduser('~'), '.weboob')
            xdg_config_home = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config')), 'weboob')
            xdg_data_home = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.join(os.path.expanduser('~'), '.local', 'share')), 'weboob')

            if os.path.isdir(old_workdir):
                self.logger.warning('You are using "%s" as working directory. Files are moved into %s and %s.'
                                    % (old_workdir, xdg_config_home, xdg_data_home))
                self._create_dir(xdg_config_home)
                self._create_dir(xdg_data_home)
                for f in os.listdir(old_workdir):
                    if f in Repositories.SHARE_DIRS:
                        dest = xdg_data_home
                    else:
                        dest = xdg_config_home
                    shutil.move(os.path.join(old_workdir, f), dest)
                shutil.rmtree(old_workdir)
            workdir = xdg_config_home
            datadir = xdg_data_home

        self.workdir = os.path.realpath(workdir)
        self._create_dir(workdir)

        # Repositories management
        self.repositories = Repositories(workdir, datadir, self.VERSION)

        # Backends loader
        self.modules_loader = ModulesLoader(self.repositories)

        # Backend instances config
        if not backends_filename:
            backends_filename = os.environ.get('WEBOOB_BACKENDS', os.path.join(self.workdir, self.BACKENDS_FILENAME))
        elif not backends_filename.startswith('/'):
            backends_filename = os.path.join(self.workdir, backends_filename)
        self.backends_config = BackendsConfig(backends_filename)

        # Storage
        self.storage = storage

    def _create_dir(self, name):
        if not os.path.exists(name):
            os.makedirs(name)
        elif not os.path.isdir(name):
            self.logger.error(u'"%s" is not a directory' % name)

    def __deinit__(self):
        self.deinit()

    def deinit(self):
        """
        Call this method when you stop using Weboob, to
        properly unload all correctly.
        """
        self.unload_backends()

    def update(self, progress=IProgress()):
        """
        Update modules from repositories.
        """
        self.repositories.update(progress)

        modules_to_check = set([module_name for name, module_name, params in self.backends_config.iter_backends()])
        for module_name in modules_to_check:
            minfo = self.repositories.get_module_info(module_name)
            if minfo and not minfo.is_installed():
                self.repositories.install(minfo, progress)

    class LoadError(Exception):
        """
        Raised when a backend is unabled to load.

        :param backend_name: name of backend we can't load
        :param exception: exception object
        """
        def __init__(self, backend_name, exception):
            Exception.__init__(self, unicode(exception))
            self.backend_name = backend_name

    def build_backend(self, module_name, params=None, storage=None):
        """
        Create a single backend which is not listed
        in configuration.

        :param module_name: name of module
        :param params: parameters to give to backend
        :type params: :class:`dict`
        :param storage: storage to use
        :type storage: :class:`weboob.tools.storage.IStorage`
        :rtype: :class:`weboob.tools.backend.BaseBackend`
        """
        minfo = self.repositories.get_module_info(module_name)
        if minfo is None:
            raise ModuleLoadError(module_name, 'Module does not exist.')

        if not minfo.is_installed():
            self.repositories.install(minfo)

        module = self.modules_loader.get_or_load_module(module_name)

        backend_instance = module.create_instance(self, module_name, params or {}, storage)
        return backend_instance

    def load_backends(self, caps=None, names=None, modules=None, storage=None, errors=None):
        """
        Load backends listed in config file.

        :param caps: load backends which implement all of specified caps
        :type caps: tuple[:class:`weboob.capabilities.base.ICapBase`]
        :param names: load backends with instance name in list
        :type names: tuple[:class:`str`]
        :param modules: load backends which module is in list
        :type modules: tuple[:class:`str`]
        :param storage: use this storage if specified
        :type storage: :class:`weboob.tools.storage.IStorage`
        :param errors: if specified, store every errors in this list
        :type errors: list[:class:`LoadError`]
        :returns: loaded backends
        :rtype: dict[:class:`str`, :class:`weboob.tools.backend.BaseBackend`]
        """
        loaded = {}
        if storage is None:
            storage = self.storage

        for instance_name, module_name, params in self.backends_config.iter_backends():
            if '_enabled' in params and not params['_enabled'].lower() in ('1', 'y', 'true', 'on', 'yes') or \
               names is not None and instance_name not in names or \
               modules is not None and module_name not in modules:
                continue

            minfo = self.repositories.get_module_info(module_name)
            if minfo is None:
                self.logger.warning(u'Backend "%s" is referenced in %s but was not found. '
                                     'Perhaps a missing repository?' % (module_name, self.backends_config.confpath))
                continue

            if caps is not None and not minfo.has_caps(caps):
                continue

            if not minfo.is_installed():
                self.repositories.install(minfo)

            module = None
            try:
                module = self.modules_loader.get_or_load_module(module_name)
            except ModuleLoadError, e:
                self.logger.error(e)
                continue

            if instance_name in self.backend_instances:
                self.logger.warning(u'Oops, the backend "%s" is already loaded. Unload it before reloading...' % instance_name)
                self.unload_backends(instance_name)

            try:
                backend_instance = module.create_instance(self, instance_name, params, storage)
            except BaseBackend.ConfigError, e:
                if errors is not None:
                    errors.append(self.LoadError(instance_name, e))
            else:
                self.backend_instances[instance_name] = loaded[instance_name] = backend_instance
        return loaded

    def unload_backends(self, names=None):
        """
        Unload backends.

        :param names: if specified, only unload that backends
        :type names: :class:`list`
        """
        unloaded = {}
        if isinstance(names, basestring):
            names = [names]
        elif names is None:
            names = self.backend_instances.keys()

        for name in names:
            backend = self.backend_instances.pop(name)
            with backend:
                backend.deinit()
            unloaded[backend.name] = backend

        return unloaded

    def get_backend(self, name, **kwargs):
        """
        Get a backend from its name.

        :param name: name of backend to get
        :type name: str
        :param default: if specified, get this value when the backend is not found
        :type default: whatever you want
        :raises: :class:`KeyError` if not found.
        """
        try:
            return self.backend_instances[name]
        except KeyError:
            if 'default' in kwargs:
                return kwargs['default']
            else:
                raise

    def count_backends(self):
        """
        Get number of loaded backends.
        """
        return len(self.backend_instances)

    def iter_backends(self, caps=None):
        """
        Iter on each backends.

        Note: each backend is locked when it is returned.

        :param caps: optional list of capabilities to select backends
        :type caps: tuple[:class:`weboob.capabilities.base.IBaseCap`]
        :rtype: iter[:class:`weboob.tools.backend.BaseBackend`]
        """
        for name, backend in sorted(self.backend_instances.iteritems()):
            if caps is None or backend.has_caps(caps):
                with backend:
                    yield backend

    def do(self, function, *args, **kwargs):
        """
        Do calls on loaded backends with specified arguments, in separated
        threads.

        This function has two modes:

        - If *function* is a string, it calls the method with this name on
          each backends with the specified arguments;
        - If *function* is a callable, it calls it in a separated thread with
          the locked backend instance at first arguments, and \*args and
          \*\*kwargs.

        :param function: backend's method name, or a callable object
        :type function: :class:`str`
        :param backends: list of backends to iterate on
        :type backends: list[:class:`str`]
        :param caps: iterate on backends which implement this caps
        :type caps: list[:class:`weboob.capabilities.base.IBaseCap`]
        :param condition: a condition to validate results
        :type condition: :class:`weboob.core.bcall.IResultsCondition`
        :rtype: A :class:`weboob.core.bcall.BackendsCall` object (iterable)
        """
        backends = self.backend_instances.values()
        _backends = kwargs.pop('backends', None)
        if _backends is not None:
            if isinstance(_backends, BaseBackend):
                backends = [_backends]
            elif isinstance(_backends, basestring):
                if len(_backends) > 0:
                    try:
                        backends = [self.backend_instances[_backends]]
                    except (ValueError,KeyError):
                        backends = []
            elif isinstance(_backends, (list, tuple, set)):
                backends = []
                for backend in _backends:
                    if isinstance(backend, basestring):
                        try:
                            backends.append(self.backend_instances[backend])
                        except (ValueError,KeyError):
                            pass
                    else:
                        backends.append(backend)
            else:
                self.logger.warning(u'The "backends" value isn\'t supported: %r' % _backends)

        if 'caps' in kwargs:
            caps = kwargs.pop('caps')
            backends = [backend for backend in backends if backend.has_caps(caps)]
        condition = kwargs.pop('condition', None)

        # The return value MUST BE the BackendsCall instance. Please never iterate
        # here on this object, because caller might want to use other methods, like
        # wait() on callback_thread().
        # Thanks a lot.
        return BackendsCall(backends, condition, function, *args, **kwargs)

    def schedule(self, interval, function, *args):
        """
        Schedule an event.

        :param interval: delay before calling the function
        :type interval: int
        :param function: function to call
        :type function: callabale
        :param args: arguments to give to function
        :returns: an event identificator
        """
        return self.scheduler.schedule(interval, function, *args)

    def repeat(self, interval, function, *args):
        """
        Repeat a call to a function

        :param interval: interval between two calls
        :type interval: int
        :param function: function to call
        :type function: callable
        :param args: arguments to give to function
        :returns: an event identificator
        """
        return self.scheduler.repeat(interval, function, *args)

    def cancel(self, ev):
        """
        Cancel an event

        :param ev: the event identificator
        """
        return self.scheduler.cancel(ev)

    def want_stop(self):
        """
        Plan to stop the scheduler.
        """
        return self.scheduler.want_stop()

    def loop(self):
        """
        Run the scheduler loop
        """
        return self.scheduler.run()
