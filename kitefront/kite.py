#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

import requests
from selenium.webdriver.remote.command import Command

from kitefront.browser import Browser
from kitefront.orders.orders import Orders


class Kite(Orders):
    _b = None

    def __init__(self, username, password, pin):
        self._username = username
        self._password = password
        self._pin = pin
        self._b = Browser()
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
