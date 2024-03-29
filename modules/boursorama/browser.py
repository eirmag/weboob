# -*- coding: utf-8 -*-

# Copyright(C) 2012      Gabriel Serme
# Copyright(C) 2011      Gabriel Kerneis
# Copyright(C) 2010-2011 Jocelyn Jaubert
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


from weboob.tools.browser import BaseBrowser, BrowserIncorrectPassword
from .pages import LoginPage, AccountsList, AccountHistory, AuthenticationPage

from datetime import date
from dateutil.relativedelta import relativedelta


__all__ = ['Boursorama']

class BrowserIncorrectAuthenticationCode(BrowserIncorrectPassword):
    pass


class Boursorama(BaseBrowser):
    DOMAIN = 'www.boursorama.com'
    PROTOCOL = 'https'
    CERTHASH = '74429081f489cb723a82171a94350913d42727053fc86cf5bf5c3d65d39ec449'
    ENCODING = None  # refer to the HTML encoding
    PAGES = {
             '.*/connexion/securisation/index.phtml': AuthenticationPage,
             '.*connexion.phtml.*': LoginPage,
             '.*/comptes/synthese.phtml': AccountsList,
             '.*/comptes/banque/detail/mouvements.phtml.*': AccountHistory,
            }

    def __init__(self, device="weboob", enable_twofactors=False
                , *args, **kwargs):
        self.device = device
        self.enable_twofactors = enable_twofactors
        BaseBrowser.__init__(self, *args, **kwargs)

    def home(self):
        self.location('https://' + self.DOMAIN + '/connexion.phtml')

    def is_logged(self):
        return not self.is_on_page(LoginPage)

    def handle_authentication(self):
        if self.is_on_page(AuthenticationPage):
            if self.enable_twofactors:
                self.page.authenticate(self.device)
            else:
                print \
                """Boursorama - activate the two factor authentication in boursorama config."""\
                """ You will receive SMS code but are limited in request per day (around 15)"""

    def login(self):
        assert isinstance(self.username, basestring)
        assert isinstance(self.password, basestring)
        assert isinstance(self.device, basestring)
        assert isinstance(self.enable_twofactors, bool)
        assert self.password.isdigit()

        #for debug, save requested pages to tmp dir
        #self.SAVE_RESPONSES = True

        if not self.is_on_page(LoginPage):
            self.location('https://' + self.DOMAIN + '/connexion.phtml')

        self.page.login(self.username, self.password)

        if self.is_on_page(LoginPage):
            raise BrowserIncorrectPassword()

        #after login, we might be redirected to the two factor
        #authentication page
        #print "handle authentication"
        self.handle_authentication()

        self.location('/comptes/synthese.phtml', no_login=True)

        #if the login was correct but authentication code failed,
        #we need to verify if bourso redirect us to login page or authentication page
        if self.is_on_page(LoginPage):
            #print "not correct after handling authentication"
            raise BrowserIncorrectAuthenticationCode()

        #print "login over"


    def get_accounts_list(self):
        if not self.is_on_page(AccountsList):
            self.location('/comptes/synthese.phtml')

        return self.page.get_list()

    def get_account(self, id):
        assert isinstance(id, basestring)

        if not self.is_on_page(AccountsList):
            self.location('/comptes/synthese.phtml')

        l = self.page.get_list()
        for a in l:
            if a.id == id:
                return a

        return None

    def get_history(self, account):
        self.location(account._link_id)
        if not self.is_on_page(AccountHistory):
            raise NotImplementedError()

        operations = self.page.get_operations()
        # load last month as well
        target = date.today() - relativedelta(months=1)
        self.location(account._link_id + ("&month=%d&year=%d" % (target.month, target.year)))
        operations += self.page.get_operations()
        # and the month before, just in case you're greedy
        target = date.today() - relativedelta(months=2)
        self.location(account._link_id + ("&month=%d&year=%d" % (target.month, target.year)))
        operations += self.page.get_operations()
        for index, op in enumerate(operations):
            op.id = index

        return operations

    def transfer(self, from_id, to_id, amount, reason=None):
        raise NotImplementedError()
