#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kitefront.grpc import data_pb2_grpc

class DataService(data_pb2_grpc.DataServicer):

    def __init__(self, kite):
        self.kite = kite

    def Candles(self, request, context):
        pass
