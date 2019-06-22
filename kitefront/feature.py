#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Feature:

    def request(self, *args, **kwargs):
        raise NotImplementedError

    def watch(self, id, url):
        raise NotImplementedError
