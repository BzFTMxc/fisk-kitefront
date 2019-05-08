#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform

_base = os.path.dirname(__file__)

VERSION = "74.0.3729.6"

DARWIN = os.path.join(_base, "chromedriver_mac64")
LINUX = os.path.join(_base, "chromedriver_linux64")

if platform.system() == 'Darwin':
    CURRENT = DARWIN
elif platform.system() == 'Linux':
    CURRENT = LINUX
else:
    CURRENT = None
