
'''
Thrift server that creates handler and processor instance for each client.
'''

import Queue
import logging
import os
import sys
import threading
import traceback

from thrift.Thrift import TProcessor
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport


class TInstanceServer:
  """Base interface for a instance server, which must have a serve() method.

  Three constructors for all servers:
  1) (processorFactory, serverTransport)
  2) (processorFactory, serverTransport, transportFactory, protocolFactory)
  3) (processorFactory, serverTransport,
      inputTransportFactory, outputTransportFactory,
      inputProtocolFactory, outputProtocolFactory)
  """
  def __init__(self, *args):
    if (len(args) == 2):
      self.__initArgs__(args[0], args[1],
                        TTransport.TTransportFactoryBase(),
                        TTransport.TTransportFactoryBase(),
                        TBinaryProtocol.TBinaryProtocolFactory(),
                        TBinaryProtocol.TBinaryProtocolFactory())
    elif (len(args) == 4):
      self.__initArgs__(args[0], args[1], args[2], args[2], args[3], args[3])
    elif (len(args) == 6):
      self.__initArgs__(args[0], args[1], args[2], args[3], args[4], args[5])

  def __initArgs__(self, processorFactory, serverTransport,
                   inputTransportFactory, outputTransportFactory,
                   inputProtocolFactory, outputProtocolFactory):
    self.processorFactory = processorFactory
    self.serverTransport = serverTransport
    self.inputTransportFactory = inputTransportFactory
    self.outputTransportFactory = outputTransportFactory
    self.inputProtocolFactory = inputProtocolFactory
    self.outputProtocolFactory = outputProtocolFactory

  def serve(self):
    pass


class TSimpleInstanceServer(TInstanceServer):
  """Simple single-threaded server that just pumps around one transport."""

  def __init__(self, *args):
    TInstanceServer.__init__(self, *args)

  def serve(self):
    self.serverTransport.listen()
    while True:
      client = self.serverTransport.accept()
      processor = self.processorFactory.getProcessor(client)
      itrans = self.inputTransportFactory.getTransport(client)
      otrans = self.outputTransportFactory.getTransport(client)
      iprot = self.inputProtocolFactory.getProtocol(itrans)
      oprot = self.outputProtocolFactory.getProtocol(otrans)
      try:
        while True:
          processor.process(iprot, oprot)
      except TTransport.TTransportException, tx:
        pass
      except Exception as x:
        logging.exception(x)

      processor.processEnd()
      itrans.close()
      otrans.close()


class TThreadedInstanceServer(TInstanceServer):
  """Threaded server that spawns a new thread per each connection."""

  def __init__(self, *args, **kwargs):
    TInstanceServer.__init__(self, *args)
    self.daemon = kwargs.get("daemon", False)

  def serve(self):
    self.serverTransport.listen()
    while True:
      try:
        client = self.serverTransport.accept()
        t = threading.Thread(target=self.handle, args=(client,))
        t.setDaemon(self.daemon)
        t.start()
      except KeyboardInterrupt:
        raise
      except Exception as x:
        logging.exception(x)

  def handle(self, client):
    processor = self.processorFactory.getProcessor(client)
    itrans = self.inputTransportFactory.getTransport(client)
    otrans = self.outputTransportFactory.getTransport(client)
    iprot = self.inputProtocolFactory.getProtocol(itrans)
    oprot = self.outputProtocolFactory.getProtocol(otrans)
    try:
      while True:
        processor.process(iprot, oprot)
    except TTransport.TTransportException, tx:
      pass
    except Exception as x:
      logging.exception(x)

    processor.processEnd()
    itrans.close()
    otrans.close()


class TThreadPoolInstanceServer(TInstanceServer):
  """Server with a fixed size pool of threads which service requests."""

  def __init__(self, *args, **kwargs):
    TInstanceServer.__init__(self, *args)
    self.clients = Queue.Queue()
    self.threads = 10
    self.daemon = kwargs.get("daemon", False)

  def setNumThreads(self, num):
    """Set the number of worker threads that should be created"""
    self.threads = num

  def serveThread(self):
    """Loop around getting clients from the shared queue and process them."""
    while True:
      try:
        client = self.clients.get()
        self.serveClient(client)
      except Exception, x:
        logging.exception(x)

  def serveClient(self, client):
    """Process input/output from a client for as long as possible"""
    
    processor = self.processorFactory.getProcessor(client)
    itrans = self.inputTransportFactory.getTransport(client)
    otrans = self.outputTransportFactory.getTransport(client)
    iprot = self.inputProtocolFactory.getProtocol(itrans)
    oprot = self.outputProtocolFactory.getProtocol(otrans)
    try:
      while True:
        processor.process(iprot, oprot)
    except TTransport.TTransportException, tx:
      pass
    except Exception as x:
      logging.exception(x)

    processor.processEnd()
    itrans.close()
    otrans.close()

  def serve(self):
    """Start a fixed number of worker threads and put client into a queue"""
    for i in range(self.threads):
      try:
        t = threading.Thread(target=self.serveThread)
        t.setDaemon(self.daemon)
        t.start()
      except Exception as x:
        logging.exception(x)

    # Pump the socket for clients
    self.serverTransport.listen()
    while True:
      try:
        client = self.serverTransport.accept()
        self.clients.put(client)
      except Exception as x:
        logging.exception(x)

