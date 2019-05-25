#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bunch import bunchify, Bunch

# Features disabled for security

VARIETY = bunchify({
    "REGULAR": "regular",
    # "APO": "amo",
    "BO": "bo",
    # "CO": "co"
})

TYPE = bunchify({
    "MARKET": "MARKET",
    "LIMIT": "LIMIT",
    # "SL": "SL",
    # "SLM": "SL-M"
})

PRODUCT = bunchify({
    # "CNC": "CNC",
    # "NRML": "NRML",
    "MIS": "MIS"
})

VALIDITY = bunchify({
    "DAY": "DAY",
    "IOC": "IOC"
})


class Order(Bunch):

    def __init__(self, tradingsymbol, exchange, transaction_type, quantity, validity):
        self.variety = VARIETY.REGULAR
        self.tradingsymbol = tradingsymbol
        self.exchange = exchange
        self.transaction_type = transaction_type
        self.order_type = TYPE.MARKET
        self.quantity = quantity
        self.product = PRODUCT.MIS
        self.validity = validity

    def limit(self, limit_price):
        self.order_type = TYPE.LIMIT
        self.price = limit_price

    def market(self):
        self.order_type = TYPE.MARKET
        del self.price

    def bracket(self, stoploss, target, trailing_stoploss=None):
        self.variety = VARIETY.BO
        self.stoploss = stoploss
        self.squareoff = target
        self.trailing_stoploss = trailing_stoploss
