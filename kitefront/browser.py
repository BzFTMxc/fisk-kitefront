#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform
import time
import urllib

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.remote.command import Command

from kitefront import chromedriver
from kitefront.exceptions import DuplicateTabError, TabNotExistError, InterfaceError, LocalstorageReadError


class Browser(Chrome):

    _GET_RETRY_MAX = 3

    _tabs = {}
    _local_storage = {}
    
    def __init__(self):
        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = {'performance': 'ALL'}
        driver = chromedriver.CURRENT
        if driver is None:
            raise Exception("No chromedriver available for platform " + platform.system())
        super(Browser, self).__init__(driver, desired_capabilities=capabilities)
        self._tabs["default"] = self.window_handles[0]

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
        if tab_id in self._tabs:
            raise DuplicateTabError
        existing_tabs = set(self.window_handles)
        self.execute_script('''window.open('http://httpstat.us/200')''')
        new_tab = list(set(self.window_handles) - existing_tabs)[0]
        self._tabs[tab_id] = new_tab
        return self

    def on(self, tab_id):
        if tab_id not in self._tabs:
            raise TabNotExistError
        self.switch_to.window(self._tabs[tab_id])
        return self

    def drop(self, tab_id):
        if tab_id not in self._tabs:
            raise TabNotExistError
        if len(self._tabs) == 1:
            self.new("default")
        self.on(tab_id).execute_script('''window.close()''')
        self.switch_to.window(self.window_handles[0])
        del self._tabs[tab_id]
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

    def read_local_storage(self):
        keys = self.execute(Command.GET_LOCAL_STORAGE_KEYS)['value']
        if keys is None:
            raise LocalstorageReadError
        self._local_storage = {}
        for key in keys:
            value = self.execute(Command.GET_LOCAL_STORAGE_ITEM, {'key': urllib.quote(key, safe='')})['value']
            self._local_storage[key] = value
        return self
