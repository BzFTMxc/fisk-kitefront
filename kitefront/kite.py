#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

from selenium.webdriver.remote.command import Command

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
        ciqrandom = self._b.execute(Command.GET_LOCAL_STORAGE_ITEM, {'key': 'tabex_default_router_' + str(tabex_master)})['value']
        return str(ciqrandom)

    def admin(self):
        return Admin(self)

    def data(self):
        return Data(self)

    def trade(self):
        return Trade(self)
