#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime

from kitefront.constants import TIMESTAMP_FORMAT
from kitefront.utils import random


class Data:

    def __init__(self, kite):
        self._k = kite
        self._b = kite._b

    def candles(self, instrument, interval, from_date, to_date):
        if to_date.day == from_date.day and to_date.hour == 0 and to_date.minute == 0:
            to_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59)
        tab_id = random("candles")
        self._b.new(tab_id)
        ciqrandom = self._k.ciqrandom()
        # {data: { candles: [[timestamp, open, high, low, close, volume]]}}
        self._b.on(tab_id).open(
            'https://kitecharts-aws.zerodha.com/api/chart/' + instrument + '/' + interval +
            '?from=' + from_date.strftime(TIMESTAMP_FORMAT) + '&to=' + to_date.strftime(TIMESTAMP_FORMAT) +
            '&' + self._k.context_str() + '&ciqrandom=' + ciqrandom)
        page_source = self._b.page_source
        self._b.drop(tab_id)
        page_source = re.sub('<[^<]+?>', '', page_source)
        return json.loads(page_source)
