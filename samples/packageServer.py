#!/usr/bin/env python
# -- coding=utf-8 --

import sys
import time
import logging
sys.path.append('gen-py')

from packageProcessor import ServerService
from packageProcessor import ClientService
from packageProcessor.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
sys.path.append('..')
from messageThrift.server import TInstanceServer
from messageThrift import InstanceProcess

gHandlers = {}

class ServerServiceHandler(InstanceProcess.InstanceServiceHandler):
    def __init__(self, client):
        InstanceProcess.InstanceServiceHandler.__init__(self, client)
        self._clientName = None

    def introduce(self, clientName):
        self._clientName = clientName  
        gHandlers[clientName] = self
        print 'New one comes here:', clientName

    def blink(self):
        print time.asctime(), self._clientName, 'blinks.'
        for clientName, handler in gHandlers.items():
            print 'send friendblinks to ', clientName
            handler._client.friendBlinks(self._clientName)

    def _handleProcessEnd(self):
        gHandlers.pop(self._clientName)
        print self._clientName, 'leaved.'

def startServe():
    transport = TSocket.TServerSocket(port=9991)
    transportFactory = TTransport.TBufferedTransportFactory()
    protocolFactory = TBinaryProtocol.TBinaryProtocolFactory()
    handlerFactory = InstanceProcess.IOSeperatedHandlerFactory(ServerServiceHandler, ClientService.Iface, ServerService.Iface)
    processorFactory = InstanceProcess.InstanceProcessorFactory(ServerService.Processor, handlerFactory, ClientService.Client, protocolFactory)
    worker = InstanceProcess.Worker(handlerFactory.getTaskQueue())
    worker.startWorkingThread()
    server = TInstanceServer.TThreadedInstanceServer(processorFactory, transport, transportFactory, protocolFactory, daemon=True)

    print 'Starting the server...'
    server.serve()
    print 'done.'

if __name__ == "__main__":
    startServe()

