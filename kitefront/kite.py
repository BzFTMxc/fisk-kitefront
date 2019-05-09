#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kitefront.browser import Browser
from kitefront.admin import Admin
from kitefront.data import Data
from kitefront.trade import Trade


class Kite:

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

    def admin(self):
        return Admin(self._b)

    def data(self):
        return Data(self._b)

    def trade(self):
        return Trade(self._b)
