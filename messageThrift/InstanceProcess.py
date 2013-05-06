#!/usr/bin/env python
# -- coding: utf-8 --

'''
Processor and handlers that support run two different services in service and client
side on one double-way transport.
Not only the client side but also the server side can initiatively call the one-way 
service method in the opposite side, at the cost of that services on both side can 
only have one way method.
'''

import logging
import threading
import inspect
import Queue
from thrift import Thrift

class InstanceServiceHandler(object):
    '''
    Handler class with an client object. Server will create an instance for each client
    and add a client reference to the instance. The client reference can be used to call 
    client side one way service back on handling with messages defined in thrift server 
    side one way service.
    '''
    def __init__(self, client):
        self._client = client
        
    def _handleProcessEnd(self):
        ''' override this to handle client drop '''
        pass

class InstanceProcessor(Thrift.TProcessor):
    def __init__(self, innerProcessor, handler):
        self._innerProcessor = innerProcessor
        self._handler = handler

    def process(self, iprot, oprot):
        return self._innerProcessor.process(iprot, oprot)

    def processEnd(self):
        self._handler._handleProcessEnd()

class InstanceProcessorFactory(object):
    '''
    Factory that can generate processor instances for service on server side and add the
    corresponding client side referenece to the handler instance.
    '''
    def __init__(self, innerProcessorClass, handlerFactory, clientClientClass, protocolFactory):
        self._innerProcessorClass = innerProcessorClass
        self._handlerFactory = handlerFactory
        self._clientClientClass = clientClientClass
        self._protocolFactory = protocolFactory

    def getProcessor(self, clientTrans):
        clientProtocol = self._protocolFactory.getProtocol(clientTrans)
        client = self._clientClientClass(clientProtocol)
        handler = self._handlerFactory.getHandler(client)
        innerProcessor = self._innerProcessorClass(handler)
        return InstanceProcessor(innerProcessor, handler)

class EasyInstanceHandlerFactory(object):
    def __init__(self, handlerClass):
        self.handlerClass = handlerClass

    def getHandler(self, client):
        return self.handlerClass(client)

class Task(object):
    def __init__(self, obj, methodName, args):
        self.obj = obj 
        self.methodName = methodName
        self.args = args

class IOSeperatedHandler(object):
    def __init__(self, handlerInterface, taskQueue):
        self.funcNames = set()
        allMembers = inspect.getmembers(handlerInterface)
        for member, memberType in allMembers:
            if memberType.__class__ == IOSeperatedHandler.__init__.__class__:
                self.funcNames.add(member)

        self.taskQueue = taskQueue
        self.logicHandler = None
        self._methodName = None

    def __getattribute__(self, name):
        try:
            # 必须先调用默认的__getattribute__, 否则后面使用任何self.*都会引起无限递归
            return object.__getattribute__(self, name)
        except Exception as ex:
            if name in self.funcNames:
                self._methodName = name 
                #logging.debug("__getattribute__%s" % name) 
                return self._pushQueue
            raise ex

    def setLogicHandler(self, logicHandler):
        self.logicHandler = logicHandler

    def _pushQueue(self, *args):
        # self._methodName should be not None
        #logging.debug("push queue %s%s" % (self._methodName, args))
        t = Task(self.logicHandler, self._methodName, args)
        self.taskQueue.put(t)
        self._methodName = None

    def _handleProcessEnd(self):
        ''' override this to handle client drop '''
        t = Task(self.logicHandler, "_handleProcessEnd", ())
        self.taskQueue.put(t)

class IOSeperatedClient(object):
    def __init__(self, interface, realClient):
        self._iprot = realClient._iprot
        self._oprot = realClient._oprot
        self._methodName = None
        self.realClient = realClient
        #use reflection to construct self
        self.funcNames = set()
        allMembers = inspect.getmembers(interface)
        for member, memberType in allMembers:
            if memberType.__class__ == IOSeperatedClient.__init__.__class__:
                self.funcNames.add(member)

        self.sendQueue = Queue.Queue()

    def __getattribute__(self, name):
        try:
            # must call object.__getattribute__ first, otherwise any self.* would cause infinite recursion.
            return object.__getattribute__(self, name)
        except Exception as ex:
            if name in self.funcNames:
                self._methodName = name 
                return self._pushQueue
            raise ex

    def _pushQueue(self, *args):
        # self._methodName should be not None
        t = Task(self.realClient, self._methodName, args)
        self.sendQueue.put(t)
        self._methodName = None

    def _sendingThreadEntry(self):
        while True:
            task = self.sendQueue.get()
            if task is None:
                return
            getattr(task.obj, task.methodName)(*task.args)

    def startSendingThread(self, daemon=True):
        thread = threading.Thread(target = self._sendingThreadEntry, args = ())
        thread.setDaemon(daemon)
        thread.start()

    def stopSendingThread(self):
        self.sendQueue.put(None)

class IOSeperatedHandlerFactory(object):
    ''' This factory generate handlers that seperated logic handler process, 
        io sending and io receival operation in 3 different thread, and all
        client's tasks are put into one uniform Queue. 
    '''
    def __init__(self, handlerClass, clientInterface, serverInterface):
        self.handlerClass = handlerClass
        self.clientInterface = clientInterface
        self.serverInterface = serverInterface
        self._receviedQueue = Queue.Queue()

    def getHandler(self, client):
        ioClient = IOSeperatedClient(self.clientInterface, client)
        handler = IOSeperatedHandler(self.serverInterface, self._receviedQueue)
        logicHandler = self.handlerClass(ioClient)
        handler.setLogicHandler(logicHandler)
        ioClient.startSendingThread()
        return handler

    def getTaskQueue(self, ):
        return self._receviedQueue

class Worker(object):
    def __init__(self, taskQueue):
        self.taskQueue = taskQueue

    def _workingThreadEntry(self):
        while True:
            task = self.taskQueue.get()
            if task is None:
                return
            task.obj.__getattribute__(task.methodName)(* task.args)

    def startWorkingThread(self, daemon=True):
        thread = threading.Thread(target = self._workingThreadEntry, args = ())
        thread.setDaemon(daemon)
        thread.start()

    def stopWorkingThread(self):
        self.taskQueue.put(None)
