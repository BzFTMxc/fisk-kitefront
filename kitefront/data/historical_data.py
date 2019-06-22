#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from bunch import bunchify

from kitefront.feature import Feature

INTERVAL = bunchify({
    "x1m": "minute",
    "x1d": "day",
    "x3m": "3minute",
    "x5m": "5minute",
    "x10m": "10minute",
    "x15m": "15minute",
    "x30m": "30minute",
    "x1h": "60minute"
})


class HistoricalData(Feature):

    def candles(self, instrument_token, interval, from_date, to_date):
        if to_date.hour == 0:
            to_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59)
        return self.request('GET', '/instruments/historical/' + str(
            instrument_token) + '/' + interval + '?from=' + str(from_date) + '&to=' + str(to_date))
