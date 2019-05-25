#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform
import time
import urllib

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.command import Command

from kitefront import chromedriver
from kitefront.exceptions import DuplicateTabError, TabNotExistError, InterfaceError, LocalstorageReadError


class Browser(Chrome):
    _GET_RETRY_MAX = 3

    tabs = {}
    ls = {}
    cookies = []
    watchers = []

    def __init__(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = {'performance': 'ALL'}
        driver = chromedriver.CURRENT
        if driver is None:
            raise Exception("No chromedriver available for platform " + platform.system())
        super(Browser, self).__init__(driver, chrome_options=chrome_options, desired_capabilities=capabilities)
        self.tabs["default"] = self.window_handles[0]

    def wait(self, timeout=1):
        time.sleep(timeout)
        return self

    def open(self, url, retry_count=0):
        try:
            self.get(url)
            self.wait()
            return self
        except WebDriverException as e:
            if retry_count > self._GET_RETRY_MAX:
                raise e
            else:
                return self.open(url, retry_count + 1)

    def new(self, tab_id):
        if tab_id in self.tabs:
            raise DuplicateTabError
        existingtabs = set(self.window_handles)
        self.execute_script('''window.open('http://httpstat.us/200')''')
        new_tab = list(set(self.window_handles) - existingtabs)[0]
        self.tabs[tab_id] = new_tab
        return self

    def on(self, tab_id):
        if tab_id not in self.tabs:
            raise TabNotExistError
        self.switch_to.window(self.tabs[tab_id])
        return self

    def watch(self, id, url):
        if id in self.watchers:
            return self
        self.new('watcher_' + id).on('watcher_' + id).open(url)
        return self

    def drop(self, tab_id):
        if tab_id not in self.tabs:
            raise TabNotExistError
        if len(self.tabs) == 1:
            self.new("default")
        self.on(tab_id).execute_script('''window.close()''')
        self.switch_to.window(self.window_handles[0])
        del self.tabs[tab_id]
        return self

    def ensure(self, xpath, innerHTML):
        element = self.find_element_by_xpath(xpath)
        if element is None:
            raise InterfaceError
        if element.get_property('innerHTML') != innerHTML:
            raise InterfaceError
        return self

    def type_in(self, xpath, keys):
        element = self.find_element_by_xpath(xpath)
        if element is None:
            raise InterfaceError
        element.send_keys(keys)
        return self

    def click_on(self, xpath):
        element = self.find_element_by_xpath(xpath)
        if element is None:
            raise InterfaceError
        element.click()
        return self

    def read_cookies(self):
        cookies = self.execute(Command.GET_ALL_COOKIES)['value']
        if cookies is None:
            self.cookies = []
        else:
            self.cookies = cookies

    def read_local_storage(self):
        keys = self.execute(Command.GET_LOCAL_STORAGE_KEYS)['value']
        if keys is None:
            raise LocalstorageReadError
        self.ls = {}
        for key in keys:
            value = self.execute(Command.GET_LOCAL_STORAGE_ITEM, {'key': urllib.quote(key, safe='')})['value']
            self.ls[key] = value
        return self
