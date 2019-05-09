#!/usr/bin/env python
# -*- coding: utf-8 -*-


class DuplicateTabError(Exception):    
    def __init__(self):
        super(DuplicateTabError, self).__init__("Tab already exist")


class TabNotExistError(Exception):
    def __init__(self):
        super(TabNotExistError, self).__init__("No such tab")


class InterfaceError(Exception):
    def __init__(self):
        super(InterfaceError, self).__init__("Interface not as expected")


class LocalstorageReadError(Exception):
    def __init__(self):
        super(LocalstorageReadError, self).__init__("Could not read localStorage")
