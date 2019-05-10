#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kitefront.utils import random


class Data:

    def __init__(self, kite):
        self._k = kite
        self._b = kite._b

    def candles(self, instrument, interval, from_date, to_date):
        tab_id = random("candles")
        self._b.new(tab_id)
        ciqrandom = self._k.ciqrandom()
        # {data: { candles: [[timestamp, open, high, low, close, volume]]}}
        self._b.on(tab_id).open(
            'https://kitecharts-aws.zerodha.com/api/chart/' + instrument + '/' + interval +
            '?from=' + from_date + '&to=' + to_date + '&' + self._k.context_str() + '&ciqrandom=' + ciqrandom)
        self._b.drop(tab_id)
