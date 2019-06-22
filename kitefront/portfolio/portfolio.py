#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kitefront.feature import Feature


class Portfolio(Feature):

    def holdings(self):
        return self.request('GET', '/portfolio/holdings')

    def positions(self):
        return self.request('GET', '/portfolio/positions')
