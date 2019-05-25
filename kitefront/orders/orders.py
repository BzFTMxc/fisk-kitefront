#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kitefront.feature import Feature
from kitefront.orders.order import VARIETY


class Orders(Feature):

    def orders(self, order_id=None):
        if order_id is None:
            return self.request('GET', '/orders')
        else:
            return self.request('GET', '/orders/' + str(order_id))

    def trades(self, order_id=None):
        if order_id is None:
            return self.request('GET', '/trades')
        else:
            return self.request('GET', '/orders/' + str(order_id) + '/trades')

    def place_order(self, order):
        variety = order.variety
        _order = order.copy()
        del _order['variety']
        return self.request('POST', '/orders/' + variety, data=_order)

    def cancel_order(self, order_id, variety=VARIETY.REGULAR, parent_order_id=None):
        return self.request('DELETE', '/orders/' + variety + '/' + str(order_id) + ('?parent_order_id=' + str(
            parent_order_id) if variety == VARIETY.BO else ''))

    def update_order(self, order_id, updates, variety=VARIETY.REGULAR):
        return self.request('PUT', '/orders/' + variety + '/' + str(order_id), data=updates)
