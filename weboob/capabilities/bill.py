# -*- coding: utf-8 -*-

# Copyright(C) 2012 Romain Bignon, Florent Fourcot
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


from .base import CapBaseObject, StringField, DateField, DecimalField, UserError
from .collection import ICapCollection


__all__ = ['SubscriptionNotFound', 'BillNotFound', 'Detail', 'Bill', 'Subscription', 'ICapBill']


class SubscriptionNotFound(UserError):
    """
    Raised when a subscription is not found.
    """
    def __init__(self, msg='Subscription not found'):
        UserError.__init__(self, msg)


class BillNotFound(UserError):
    """
    Raised when a bill is not found.
    """
    def __init__(self, msg='Bill not found'):
        UserError.__init__(self, msg)


class Detail(CapBaseObject):
    """
    Detail of a subscription
    """
    label =     StringField('label of the detail line')
    infos =     StringField('information')
    datetime =  DateField('date information')
    price =     DecimalField('price')

    def __init__(self):
        CapBaseObject.__init__(self, 0)

class Bill(CapBaseObject):
    """
    Bill.
    """
    date =      DateField('date of the bill')
    format =    StringField('format of the bill')
    label =     StringField('label of bill')
    idparent =  StringField('id of the parent subscription')

    def __init__(self):
        CapBaseObject.__init__(self, 0)

class Subscription(CapBaseObject):
    """
    Subscription to a service.
    """
    label =         StringField('label of subscription')
    subscriber =    StringField('whe has subscribed')

class ICapBill(ICapCollection):
    def iter_resources(self, objs, split_path):
        """
        Iter resources. Will return :func:`iter_subscriptions`.
        """
        if Subscription in objs:
            self._restrict_level(split_path)
            return self.iter_subscription()

    def iter_subscription(self):
        """
        Iter subscriptions.

        :rtype: iter[:class:`Subscription`]
        """
        raise NotImplementedError()

    def get_subscription(self, _id):
        """
        Get a subscription.

        :param _id: ID of subscription
        :rtype: :class:`Subscription`
        :raises: :class:`SubscriptionNotFound`
        """
        raise NotImplementedError()

    def iter_bills_history(self, subscription):
        """
        Iter history of a subscription.

        :param subscription: subscription to get history
        :type subscription: :class:`Subscription`
        :rtype: iter[:class:`Detail`]
        """
        raise NotImplementedError()

    def get_bill(self, id):
        """
        Get a bill.

        :param id: ID of bill
        :rtype: :class:`Bill`
        :raises: :class:`BillNotFound`
        """
        raise NotImplementedError()

    def download_bill(self, id):
        """
        Download a bill.

        :param id: ID of bill
        :rtype: str
        :raises: :class:`BillNotFound`
        """
        raise NotImplementedError()

    def iter_bills(self, subscription):
        """
        Iter bills.

        :param subscription: subscription to get bills
        :type subscription: :class:`Subscription`
        :rtype: iter[:class:`Bill`]
        """
        raise NotImplementedError()

    def get_details(self, subscription):
        """
        Get details of a subscription.

        :param subscription: subscription to get details
        :type subscription: :class:`Subscription`
        :rtype: iter[:class:`Detail`]
        """
        raise NotImplementedError()

    def get_balance(self, subscription):
        """
        Get the balance of a subscription.

        :param subscription: subscription to get balance
        :type subscription: :class:`Subscription`
        :rtype :class:`Detail`
        """
        raise NotImplementedError()
