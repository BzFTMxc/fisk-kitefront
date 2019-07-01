#!/usr/bin/env python
# -*- coding: utf-8 -*-

from concurrent import futures
import grpc

from kitefront.grpc.data_pb2_grpc import DataServicer
from kitefront.grpc.data_pb2_grpc import add_DataServicer_to_server

grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
add_DataServicer_to_server(DataServicer(), grpc_server)
