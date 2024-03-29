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


from urlparse import urlsplit, parse_qsl, urlparse
from datetime import datetime, timedelta

from weboob.tools.browser import BaseBrowser, BrowserIncorrectPassword
from weboob.capabilities.bank import Transfer, TransferError

from .pages import LoginPage, LoginErrorPage, AccountsPage, UserSpacePage, EmptyPage, \
                   OperationsPage, CardPage, NoOperationsPage, InfoPage, TransfertPage


__all__ = ['CreditMutuelBrowser']


# Browser
class CreditMutuelBrowser(BaseBrowser):
    PROTOCOL = 'https'
    DOMAIN = 'www.creditmutuel.fr'
    CERTHASH = '57beeba81e7a65d5fe15853219bcfcc2b2da27e0e618a78e6d97a689908ea57b'
    ENCODING = 'iso-8859-1'
    USER_AGENT = BaseBrowser.USER_AGENTS['wget']
    PAGES = {'https://www.creditmutuel.fr/groupe/fr/index.html':   LoginPage,
             'https://www.creditmutuel.fr/.*/fr/identification/default.cgi': LoginErrorPage,
             'https://www.creditmutuel.fr/.*/fr/banque/situation_financiere.cgi': AccountsPage,
             'https://www.creditmutuel.fr/.*/fr/banque/espace_personnel.aspx': UserSpacePage,
             'https://www.creditmutuel.fr/.*/fr/banque/mouvements.cgi.*': OperationsPage,
             'https://www.creditmutuel.fr/.*/fr/banque/nr/nr_devbooster.aspx.*': OperationsPage,
             'https://www.creditmutuel.fr/.*/fr/banque/operations_carte\.cgi.*': CardPage,
             'https://www.creditmutuel.fr/.*/fr/banque/CR/arrivee\.asp.*': NoOperationsPage,
             'https://www.creditmutuel.fr/.*/fr/banque/BAD.*': InfoPage,
             'https://www.creditmutuel.fr/.*/fr/banque/.*Vir.*': TransfertPage,
             'https://www.creditmutuel.fr/.*/fr/': EmptyPage,
             'https://www.creditmutuel.fr/.*/fr/banque/paci_beware_of_phishing.html.*': EmptyPage,
             'https://www.creditmutuel.fr/.*/fr/validation/.*': EmptyPage,
            }

    currentSubBank = None

    def is_logged(self):
        return not self.is_on_page(LoginPage) and not self.is_on_page(LoginErrorPage)

    def home(self):
        return self.location('https://www.creditmutuel.fr/groupe/fr/index.html')

    def login(self):
        assert isinstance(self.username, basestring)
        assert isinstance(self.password, basestring)

        if not self.is_on_page(LoginPage):
            self.location('https://www.creditmutuel.fr/', no_login=True)

        self.page.login(self.username, self.password)

        if not self.is_logged() or self.is_on_page(LoginErrorPage):
            raise BrowserIncorrectPassword()

        self.getCurrentSubBank()

    def get_accounts_list(self):
        if not self.is_on_page(AccountsPage):
            self.location('https://www.creditmutuel.fr/%s/fr/banque/situation_financiere.cgi' % self.currentSubBank)
        return self.page.get_list()

    def get_account(self, id):
        assert isinstance(id, basestring)

        l = self.get_accounts_list()
        for a in l:
            if a.id == id:
                return a

        return None

    def getCurrentSubBank(self):
        # the account list and history urls depend on the sub bank of the user
        url = urlparse(self.geturl())
        self.currentSubBank = url.path.lstrip('/').split('/')[0]

    def list_operations(self, page_url):
        l_ret = []
        while page_url:
            if page_url.startswith('/'):
                self.location(page_url)
            else:
                self.location('https://%s/%s/fr/banque/%s' % (self.DOMAIN, self.currentSubBank, page_url))

            if not self.is_on_page(OperationsPage):
                break

            for op in self.page.get_history():
                l_ret.append(op)
            page_url = self.page.next_page_url()

        return l_ret

    def get_history(self, account):
        transactions = []
        last_debit = None
        for tr in self.list_operations(account._link_id):
            # to prevent redundancy with card transactions, we do not
            # store 'RELEVE CARTE' transaction.
            if tr.raw != 'RELEVE CARTE':
                transactions.append(tr)
            elif last_debit is None:
                last_debit = (tr.date - timedelta(days=10)).month

        month = 0
        for card_link in account._card_links:
            v = urlsplit(card_link)
            args = dict(parse_qsl(v.query))
            # useful with 12 -> 1
            if int(args['mois']) < month:
                month = month + 1
            month = int(args['mois'])

            for tr in self.list_operations(card_link):
                if month > last_debit:
                    tr._is_coming = True
                transactions.append(tr)

        transactions.sort(key=lambda tr: tr.rdate, reverse=True)
        return transactions

    def transfer(self, account, to, amount, reason=None):
        # access the transfer page
        transfert_url = 'WI_VPLV_VirUniSaiCpt.asp?RAZ=ALL&Cat=6&PERM=N&CHX=A'
        self.location('https://%s/%s/fr/banque/%s' % (self.DOMAIN, self.currentSubBank, transfert_url))

        # fill the form
        self.select_form(name='FormVirUniSaiCpt')
        self['IDB'] = [account[-1]]
        self['ICR'] = [to[-1]]
        self['MTTVIR'] = '%s' % str(amount).replace('.', ',')
        if reason != None:
            self['LIBDBT'] = reason
            self['LIBCRT'] = reason
        self.submit()

        # look for known errors
        content = unicode(self.response().get_data(), self.ENCODING)
        insufficient_amount_message     = u'Montant insuffisant.'
        maximum_allowed_balance_message = u'Solde maximum autorisé dépassé.'

        if content.find(insufficient_amount_message) != -1:
            raise TransferError('The amount you tried to transfer is too low.')

        if content.find(maximum_allowed_balance_message) != -1:
            raise TransferError('The maximum allowed balance for the target account has been / would be reached.')

        # look for the known "all right" message
        ready_for_transfer_message = u'Confirmez un virement entre vos comptes'
        if not content.find(ready_for_transfer_message):
            raise TransferError('The expected message "%s" was not found.' % ready_for_transfer_message)

        # submit the confirmation form
        self.select_form(name='FormVirUniCnf')
        submit_date = datetime.now()
        self.submit()

        # look for the known "everything went well" message
        content = unicode(self.response().get_data(), self.ENCODING)
        transfer_ok_message = u'Votre virement a été exécuté ce jour'
        if not content.find(transfer_ok_message):
            raise TransferError('The expected message "%s" was not found.' % transfer_ok_message)

        # We now have to return a Transfer object
        transfer = Transfer(submit_date.strftime('%Y%m%d%H%M%S'))
        transfer.amount = amount
        transfer.origin = account
        transfer.recipient = to
        transfer.date = submit_date
        return transfer
