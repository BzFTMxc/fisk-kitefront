#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Data:

    _b = None

    def __init__(self, browser):
        self._b = browser


    def candles(self, instrument, interval, from, to, ):



'''
curl 'https://kitecharts-aws.zerodha.com/api/chart/2997505/5minute?public_token=UQRQnJPrFxiyxsLEu7WpnblnbcasUpbQ&user_id=ZF1782&api_key=kitefront&access_token=&from=2019-05-04&to=2019-05-09&ciqrandom=1557346479259' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36' -H 'Referer: https://kite.zerodha.com/static/build/chart.html?v=2.1.0' -H 'Origin: https://kite.zerodha.com' --compressed
'''