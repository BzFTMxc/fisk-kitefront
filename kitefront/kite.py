#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import datetime
import json
import re
import struct
import urllib

import requests
from selenium.webdriver.remote.command import Command

from kitefront.browser import Browser
from kitefront.data.historical_data import HistoricalData
from kitefront.orders.orders import Orders
from kitefront.portfolio.portfolio import Portfolio


class Kite(Orders, Portfolio, HistoricalData):
    _b = None

    EXCHANGE_MAP = {
        "nse": 1,
        "nfo": 2,
        "cds": 3,
        "bse": 4,
        "bfo": 5,
        "bsecds": 6,
        "mcx": 7,
        "mcxsx": 8,
        "indices": 9
    }

    # Default connection timeout
    CONNECT_TIMEOUT = 30
    # Default Reconnect max delay.
    RECONNECT_MAX_DELAY = 60
    # Default reconnect attempts
    RECONNECT_MAX_TRIES = 50
    # Default root API endpoint. It's possible to
    # override this by passing the `root` parameter during initialisation.
    ROOT_URI = "wss://ws.kite.trade"

    # Available streaming modes.
    MODE_FULL = "full"
    MODE_QUOTE = "quote"
    MODE_LTP = "ltp"

    def __init__(self, username, password, pin, headless=False):
        self._username = username
        self._password = password
        self._pin = pin
        self._b = Browser(headless=headless)
        self._b.new("kite")
        self._b.on("kite").open("https://kite.zerodha.com")
        self._b.ensure('//*[@id="container"]/div/div/div/form/div[1]/h2', 'Login to Kite')
        self._b.type_in('//*[@id="container"]/div/div/div/form/div[2]/input', self._username)
        self._b.type_in('//*[@id="container"]/div/div/div/form/div[3]/input', self._password)
        self._b.click_on('//*[@id="container"]/div/div/div/form/div[4]/button').wait()
        self._b.ensure('//*[@id="container"]/div/div/div/form/div[2]/div/label', 'PIN')
        self._b.type_in('//*[@id="container"]/div/div/div/form/div[2]/div/input', self._pin)
        self._b.click_on('//*[@id="container"]/div/div/div/form/div[3]/button').wait()
        self._b.open('https://kite.zerodha.com/dashboard')
        if self._b.current_url != 'https://kite.zerodha.com/dashboard':
            raise Exception("Could not login to Kite")
        self._b.read_local_storage()
        self._b.read_cookies()

    def watch(self, exchange, instrument, instrument_token):
        self._b.watch(
            ''.join([str(i) for i in [exchange, instrument, instrument_token]]),
            'https://kite.zerodha.com/chart/web/ciq/' + '/'.join(
                [str(i) for i in [exchange, instrument, instrument_token]])
        )

    def context(self):
        return {
            'user_id': self._b.ls['__storejs_kite_user_id'],
            'public_token': self._b.ls['__storejs_kite_public_token'],
            'api_key': 'kitefront',
            'access_token': ''
        }

    def context_str(self):
        return urllib.urlencode(self.context())

    def ciqrandom(self):
        tabex_master = self._b.execute(Command.GET_LOCAL_STORAGE_ITEM, {'key': 'tabex_default_master'})['value']
        ciqrandom = \
            self._b.execute(Command.GET_LOCAL_STORAGE_ITEM, {'key': 'tabex_default_router_' + str(tabex_master)})[
                'value']
        return str(ciqrandom)

    def stream(self):
        packets = []
        logs = self._b.get_log('performance')
        for entry in logs:
            log = json.loads(entry['message'])
            method = log['message']['method']
            if re.match('Network.webSocketFrameReceived', method):
                data = base64.decodestring(log['message']['params']['response']['payloadData'])
                for packet in self._parse_binary(data):
                    packets.append(packet)
        return packets

    def _split_packets(self, bin):
        """Split the data to individual packets of ticks."""
        # Ignore heartbeat data.
        if len(bin) < 2:
            return []

        number_of_packets = self._unpack_int(bin, 0, 2, byte_format="H")
        packets = []

        j = 2
        for i in range(number_of_packets):
            packet_length = self._unpack_int(bin, j, j + 2, byte_format="H")
            packets.append(bin[j + 2: j + 2 + packet_length])
            j = j + 2 + packet_length

        return packets

    def _unpack_int(self, bin, start, end, byte_format="I"):
        """Unpack binary data as unsgined interger."""
        return struct.unpack(">" + byte_format, bin[start:end])[0]

    def _parse_binary(self, bin):
        """Parse binary data to a (list of) ticks structure."""
        packets = self._split_packets(bin)  # split data to individual ticks packet
        data = []

        for packet in packets:
            instrument_token = self._unpack_int(packet, 0, 4)
            segment = instrument_token & 0xff  # Retrive segment constant from instrument_token

            divisor = 10000000.0 if segment == self.EXCHANGE_MAP["cds"] else 100.0

            # All indices are not tradable
            tradable = False if segment == self.EXCHANGE_MAP["indices"] else True

            # LTP packets
            if len(packet) == 8:
                data.append({
                    "tradable": tradable,
                    "mode": self.MODE_LTP,
                    "instrument_token": instrument_token,
                    "last_price": self._unpack_int(packet, 4, 8) / divisor
                })
            # Indices quote and full mode
            elif len(packet) == 28 or len(packet) == 32:
                mode = self.MODE_QUOTE if len(packet) == 28 else self.MODE_FULL

                d = {
                    "tradable": tradable,
                    "mode": mode,
                    "instrument_token": instrument_token,
                    "last_price": self._unpack_int(packet, 4, 8) / divisor,
                    "ohlc": {
                        "high": self._unpack_int(packet, 8, 12) / divisor,
                        "low": self._unpack_int(packet, 12, 16) / divisor,
                        "open": self._unpack_int(packet, 16, 20) / divisor,
                        "close": self._unpack_int(packet, 20, 24) / divisor
                    }
                }

                # Compute the change price using close price and last price
                d["change"] = 0
                if (d["ohlc"]["close"] != 0):
                    d["change"] = (d["last_price"] - d["ohlc"]["close"]) * 100 / d["ohlc"]["close"]

                # Full mode with timestamp
                if len(packet) == 32:
                    try:
                        timestamp = datetime.fromtimestamp(self._unpack_int(packet, 28, 32))
                    except Exception:
                        timestamp = None

                    d["timestamp"] = timestamp

                data.append(d)
            # Quote and full mode
            elif len(packet) == 44 or len(packet) == 184:
                mode = self.MODE_QUOTE if len(packet) == 44 else self.MODE_FULL

                d = {
                    "tradable": tradable,
                    "mode": mode,
                    "instrument_token": instrument_token,
                    "last_price": self._unpack_int(packet, 4, 8) / divisor,
                    "last_quantity": self._unpack_int(packet, 8, 12),
                    "average_price": self._unpack_int(packet, 12, 16) / divisor,
                    "volume": self._unpack_int(packet, 16, 20),
                    "buy_quantity": self._unpack_int(packet, 20, 24),
                    "sell_quantity": self._unpack_int(packet, 24, 28),
                    "ohlc": {
                        "open": self._unpack_int(packet, 28, 32) / divisor,
                        "high": self._unpack_int(packet, 32, 36) / divisor,
                        "low": self._unpack_int(packet, 36, 40) / divisor,
                        "close": self._unpack_int(packet, 40, 44) / divisor
                    }
                }

                # Compute the change price using close price and last price
                d["change"] = 0
                if (d["ohlc"]["close"] != 0):
                    d["change"] = (d["last_price"] - d["ohlc"]["close"]) * 100 / d["ohlc"]["close"]

                # Parse full mode
                if len(packet) == 184:
                    try:
                        last_trade_time = datetime.fromtimestamp(self._unpack_int(packet, 44, 48))
                    except Exception:
                        last_trade_time = None

                    try:
                        timestamp = datetime.fromtimestamp(self._unpack_int(packet, 60, 64))
                    except Exception:
                        timestamp = None

                    d["last_trade_time"] = last_trade_time
                    d["oi"] = self._unpack_int(packet, 48, 52)
                    d["oi_day_high"] = self._unpack_int(packet, 52, 56)
                    d["oi_day_low"] = self._unpack_int(packet, 56, 60)
                    d["timestamp"] = timestamp

                    # Market depth entries.
                    depth = {
                        "buy": [],
                        "sell": []
                    }

                    # Compile the market depth lists.
                    for i, p in enumerate(range(64, len(packet), 12)):
                        depth["sell" if i >= 5 else "buy"].append({
                            "quantity": self._unpack_int(packet, p, p + 4),
                            "price": self._unpack_int(packet, p + 4, p + 8) / divisor,
                            "orders": self._unpack_int(packet, p + 8, p + 10, byte_format="H")
                        })

                    d["depth"] = depth

                data.append(d)

        return data

    def request(self, method, endpoint, **kwargs):
        cookies = '; '.join([cookie['name'] + '=' + cookie['value'] for cookie in self._b.cookies])
        headers = {
            'authorization': 'enctoken ' + str(self._b.ls['__storejs_kite_enctoken']).strip('"'),
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'en-US,en;q=0.9,th;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'x-kite-version': '2.1.0',
            'x-kite-userid': str(self._b.ls['__storejs_kite_user_id']).strip('"'),
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://kite.zerodha.com/positions',
            'authority': 'kite.zerodha.com',
            'cookie': cookies
        }
        if method == 'POST':
            headers['content-type'] = 'application/x-www-form-urlencoded'
        response = requests.request(
            method,
            'https://kite.zerodha.com/oms' + endpoint,
            headers=headers,
            **kwargs
        )
        return response.json()
