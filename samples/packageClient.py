#!/usr/bin/env python

import sys
import time
import threading
import logging
sys.path.append('gen-py')

from packageProcessor import ClientService
from packageProcessor import ServerService
from packageProcessor.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class ClientServiceHandler:
  def __init__(self):
      pass

  def hello(self, helloPackage):
    print 'Server said:', helloPackage.word

  def friendBlinks(self, friendName):
    print friendName, 'blinks'

def runClientService(protocol, processor):
    try:
        while protocol.trans.isOpen():
            processor.process(protocol, protocol)
    except TTransport.TTransportException, tx:
        pass
    except Exception as x:
        logging.exception(x)

    protocol.trans.close()

def runClientCall(client):
    try:
        client.introduce(sys.argv[1])
        while client._oprot.trans.isOpen():
            time.sleep(1)
            client.blink()
            print 'send blink'
    except TTransport.TTransportException, tx:
        pass
    except Exception as x:
        logging.exception(x)

def startClientService(protocol, processor):
    try:
        t = threading.Thread(target=runClientService, args=(protocol, processor,))
        #t.setDaemon(daemon)
        t.start()
        return t
    except KeyboardInterrupt:
        raise
    except Exception as x:
         logging.exception(x)
    return None

def startClientCall(client):
    try:
        t = threading.Thread(target=runClientCall, args=(client,))
        t.start()
        return t
    except KeyboardInterrupt:
        raise
    except Exception as x:
         logging.exception(x)
    return None

def startClient():
    transport = None
    callThread = None
    try:
        transport = TSocket.TSocket('localhost', 9991)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = ServerService.Client(protocol)
        transport.open()

        callThread = startClientCall(client)
        if callThread is None:
            print 'start client call thread failed.'
            return
    
        handler = ClientServiceHandler()
        processor = ClientService.Processor(handler)
        runClientService(protocol, processor)

    except Thrift.TException, tx:
        print '%s' % (tx.message)
    finally:
        if transport is not None:
            print 'try close service'
            transport.close()

if __name__ == "__main__":
    startClient()

