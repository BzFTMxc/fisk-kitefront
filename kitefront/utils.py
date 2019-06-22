#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
from functools import partial

from secrets import secrets


def random(prefix='', length=10):
    return prefix + ''.join([partial(secrets.choice, string.ascii_uppercase + string.digits)() for _ in range(length)])
