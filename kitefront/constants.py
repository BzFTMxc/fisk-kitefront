#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bunch import bunchify

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

O_VARIETY = bunchify({
    "REGULAR": "regular",
    "APO": "amo",
    "BO": "bo",
    "CO": "co"
})

O_TYPE = bunchify({
    "MARKET": "MARKET",
    "LIMIT": "LIMIT",
    "SL": "SL",
    "SLM": "SL-M"
})

O_PRODUCT = bunchify({
    "CNC": "CNC",
    "NRML": "NRML",
    "MIS": "MIS"
})

O_VALIDITY = bunchify({
    "DAY": "DAY",
    "IOC": "IOC"
})

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

CANDLE_TUPLE_FORMAT = ["timestamp", "open", "high", "low", "close", "volume"]
