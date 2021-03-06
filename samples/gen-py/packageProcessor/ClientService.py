#
# Autogenerated by Thrift Compiler (0.9.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class Iface:
  def hello(self, helloPackage):
    """
    Parameters:
     - helloPackage
    """
    pass

  def friendBlinks(self, friendName):
    """
    Parameters:
     - friendName
    """
    pass


class Client(Iface):
  def __init__(self, iprot, oprot=None):
    self._iprot = self._oprot = iprot
    if oprot is not None:
      self._oprot = oprot
    self._seqid = 0

  def hello(self, helloPackage):
    """
    Parameters:
     - helloPackage
    """
    self.send_hello(helloPackage)

  def send_hello(self, helloPackage):
    self._oprot.writeMessageBegin('hello', TMessageType.CALL, self._seqid)
    args = hello_args()
    args.helloPackage = helloPackage
    args.write(self._oprot)
    self._oprot.writeMessageEnd()
    self._oprot.trans.flush()
  def friendBlinks(self, friendName):
    """
    Parameters:
     - friendName
    """
    self.send_friendBlinks(friendName)

  def send_friendBlinks(self, friendName):
    self._oprot.writeMessageBegin('friendBlinks', TMessageType.CALL, self._seqid)
    args = friendBlinks_args()
    args.friendName = friendName
    args.write(self._oprot)
    self._oprot.writeMessageEnd()
    self._oprot.trans.flush()

class Processor(Iface, TProcessor):
  def __init__(self, handler):
    self._handler = handler
    self._processMap = {}
    self._processMap["hello"] = Processor.process_hello
    self._processMap["friendBlinks"] = Processor.process_friendBlinks

  def process(self, iprot, oprot):
    (name, type, seqid) = iprot.readMessageBegin()
    if name not in self._processMap:
      iprot.skip(TType.STRUCT)
      iprot.readMessageEnd()
      x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
      oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
      x.write(oprot)
      oprot.writeMessageEnd()
      oprot.trans.flush()
      return
    else:
      self._processMap[name](self, seqid, iprot, oprot)
    return True

  def process_hello(self, seqid, iprot, oprot):
    args = hello_args()
    args.read(iprot)
    iprot.readMessageEnd()
    self._handler.hello(args.helloPackage)
    return

  def process_friendBlinks(self, seqid, iprot, oprot):
    args = friendBlinks_args()
    args.read(iprot)
    iprot.readMessageEnd()
    self._handler.friendBlinks(args.friendName)
    return


# HELPER FUNCTIONS AND STRUCTURES

class hello_args:
  """
  Attributes:
   - helloPackage
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'helloPackage', (PPHelloPackage, PPHelloPackage.thrift_spec), None, ), # 1
  )

  def __init__(self, helloPackage=None,):
    self.helloPackage = helloPackage

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.helloPackage = PPHelloPackage()
          self.helloPackage.read(iprot)
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('hello_args')
    if self.helloPackage is not None:
      oprot.writeFieldBegin('helloPackage', TType.STRUCT, 1)
      self.helloPackage.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class friendBlinks_args:
  """
  Attributes:
   - friendName
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'friendName', None, None, ), # 1
  )

  def __init__(self, friendName=None,):
    self.friendName = friendName

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.friendName = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('friendBlinks_args')
    if self.friendName is not None:
      oprot.writeFieldBegin('friendName', TType.STRING, 1)
      oprot.writeString(self.friendName)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
