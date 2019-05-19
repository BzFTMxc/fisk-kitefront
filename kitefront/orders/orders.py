#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kitefront.feature import Feature


class Orders(Feature):

    def positions(self):
        return self.request('GET', '/portfolio/positions')

    def orders(self):
        return self.request('GET', '/orders')

    def place_order(self, tradingsymbol, exchange, transaction_type, quantity, variety, type, product, validity):
        order = {
            'tradingsymbol': tradingsymbol,
            'exchange': exchange,
            'transaction_type': transaction_type,
            'order_type': type,
            'quantity': quantity,
            'product': product,
            'validity': validity
        }