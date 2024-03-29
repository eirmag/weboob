# -*- coding: utf-8 -*-

# Copyright(C) 2010-2011 Nicolas Duhamel
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


from urlparse import urlsplit, parse_qsl
from datetime import datetime

from weboob.tools.browser import BaseBrowser, BrowserIncorrectPassword, BrowserBanned

from .pages import LoginPage, Initident, CheckPassword, repositionnerCheminCourant, BadLoginPage, AccountDesactivate, \
                   AccountList, AccountHistory, \
                   TransferChooseAccounts, CompleteTransfer, TransferConfirm, TransferSummary

from weboob.capabilities.bank import Transfer


__all__ = ['BPBrowser']


class BPBrowser(BaseBrowser):
    DOMAIN = 'voscomptesenligne.labanquepostale.fr'
    PROTOCOL = 'https'
    CERTHASH = '868646b852c989638d4e5bbfab830e2cfbb82f4d2524e28d0251686a44e49163'
    ENCODING = None  # refer to the HTML encoding
    PAGES = {r'.*wsost/OstBrokerWeb/loginform.*'                                         : LoginPage,
             r'.*authentification/repositionnerCheminCourant-identif.ea'                 : repositionnerCheminCourant,
             r'.*authentification/initialiser-identif.ea'                                : Initident,
             r'.*authentification/verifierMotDePasse-identif.ea'                         : CheckPassword,

             r'.*synthese_assurancesEtComptes/afficheSynthese-synthese\.ea'              : AccountList,
             r'.*synthese_assurancesEtComptes/rechercheContratAssurance-synthese.ea'     : AccountList,

             r'.*CCP/releves_ccp/releveCPP-releve_ccp\.ea'                               : AccountHistory,
             r'.*CNE/releveCNE/releveCNE-releve_cne\.ea'                                 : AccountHistory,

             r'.*/virementSafran_aiguillage/init-saisieComptes\.ea'                      : TransferChooseAccounts,
             r'.*/virementSafran_aiguillage/formAiguillage-saisieComptes\.ea'            : CompleteTransfer,
             r'.*/virementSafran_national/validerVirementNational-virementNational.ea'   : TransferConfirm,
             r'.*/virementSafran_national/confirmerVirementNational-virementNational.ea' : TransferSummary,

             r'.*ost/messages\.CVS\.html\?param=0x132120c8.*'                            : BadLoginPage,
             r'.*ost/messages\.CVS\.html\?param=0x132120cb.*'                            : AccountDesactivate,
             }

    def __init__(self, *args, **kwargs):
        kwargs['parser'] = ('lxml',)
        BaseBrowser.__init__(self, *args, **kwargs)

    def home(self):
        self.location('https://voscomptesenligne.labanquepostale.fr/wsost/OstBrokerWeb/loginform?TAM_OP=login&'
            'ERROR_CODE=0x00000000&URL=%2Fvoscomptes%2FcanalXHTML%2Fidentif.ea%3Forigin%3Dparticuliers')

    def is_logged(self):
        return not self.is_on_page(LoginPage)

    def login(self):
        if not self.is_on_page(LoginPage):
            self.location('https://voscomptesenligne.labanquepostale.fr/wsost/OstBrokerWeb/loginform?TAM_OP=login&'
                'ERROR_CODE=0x00000000&URL=%2Fvoscomptes%2FcanalXHTML%2Fidentif.ea%3Forigin%3Dparticuliers',
                no_login=True)

        self.page.login(self.username, self.password)

        if self.is_on_page(BadLoginPage):
            raise BrowserIncorrectPassword()
        if self.is_on_page(AccountDesactivate):
            raise BrowserBanned()

    def get_accounts_list(self):
        self.location("https://voscomptesenligne.labanquepostale.fr/voscomptes/canalXHTML/comptesCommun/synthese_assurancesEtComptes/rechercheContratAssurance-synthese.ea")
        return self.page.get_accounts_list()

    def get_account(self, id):
        if not self.is_on_page(AccountList):
            self.location("https://voscomptesenligne.labanquepostale.fr/voscomptes/canalXHTML/comptesCommun/synthese_assurancesEtComptes/rechercheContratAssurance-synthese.ea")
        return self.page.get_account(id)

    def get_history(self, account):
        v = urlsplit(account._link_id)
        args = dict(parse_qsl(v.query))
        args['typeRecherche'] = 10

        self.location(self.buildurl(v.path, **args))
        if not self.is_on_page(AccountHistory):
            return iter([])
        return self.page.get_history()

    def make_transfer(self, from_account, to_account, amount):
        self.location('https://voscomptesenligne.labanquepostale.fr/voscomptes/canalXHTML/virement/virementSafran_aiguillage/init-saisieComptes.ea')
        self.page.set_accouts(from_account, to_account)

        #TODO: Check
        self.page.complete_transfer(amount)

        self.page.confirm()

        id_transfer = self.page.get_transfer_id()
        transfer = Transfer(id_transfer)
        transfer.amount = amount
        transfer.origin = from_account.label
        transfer.recipient = to_account.label
        transfer.date = datetime.now()
        return transfer
