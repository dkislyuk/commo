#
# Autogenerated by Thrift Compiler (0.9.1)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class ActionStatusCode:
  SUCCESS = 1
  ILLEGAL_TARGET = 2

  _VALUES_TO_NAMES = {
    1: "SUCCESS",
    2: "ILLEGAL_TARGET",
  }

  _NAMES_TO_VALUES = {
    "SUCCESS": 1,
    "ILLEGAL_TARGET": 2,
  }

class ActionType:
  MOVE = 1
  ATTACK = 2
  HEAL = 3

  _VALUES_TO_NAMES = {
    1: "MOVE",
    2: "ATTACK",
    3: "HEAL",
  }

  _NAMES_TO_VALUES = {
    "MOVE": 1,
    "ATTACK": 2,
    "HEAL": 3,
  }


class Location:
  """
  Attributes:
   - x
   - y
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'x', None, None, ), # 1
    (2, TType.I32, 'y', None, None, ), # 2
  )

  def __init__(self, x=None, y=None,):
    self.x = x
    self.y = y

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
        if ftype == TType.I32:
          self.x = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.y = iprot.readI32();
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
    oprot.writeStructBegin('Location')
    if self.x is not None:
      oprot.writeFieldBegin('x', TType.I32, 1)
      oprot.writeI32(self.x)
      oprot.writeFieldEnd()
    if self.y is not None:
      oprot.writeFieldBegin('y', TType.I32, 2)
      oprot.writeI32(self.y)
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

class Action:
  """
  Attributes:
   - type
   - moveTarget
   - attackTarget
   - healTarget
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'type', None, None, ), # 1
    (2, TType.STRUCT, 'moveTarget', (Location, Location.thrift_spec), None, ), # 2
    (3, TType.STRUCT, 'attackTarget', (Location, Location.thrift_spec), None, ), # 3
    (4, TType.STRUCT, 'healTarget', (Location, Location.thrift_spec), None, ), # 4
  )

  def __init__(self, type=None, moveTarget=None, attackTarget=None, healTarget=None,):
    self.type = type
    self.moveTarget = moveTarget
    self.attackTarget = attackTarget
    self.healTarget = healTarget

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
        if ftype == TType.I32:
          self.type = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.moveTarget = Location()
          self.moveTarget.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRUCT:
          self.attackTarget = Location()
          self.attackTarget.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRUCT:
          self.healTarget = Location()
          self.healTarget.read(iprot)
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
    oprot.writeStructBegin('Action')
    if self.type is not None:
      oprot.writeFieldBegin('type', TType.I32, 1)
      oprot.writeI32(self.type)
      oprot.writeFieldEnd()
    if self.moveTarget is not None:
      oprot.writeFieldBegin('moveTarget', TType.STRUCT, 2)
      self.moveTarget.write(oprot)
      oprot.writeFieldEnd()
    if self.attackTarget is not None:
      oprot.writeFieldBegin('attackTarget', TType.STRUCT, 3)
      self.attackTarget.write(oprot)
      oprot.writeFieldEnd()
    if self.healTarget is not None:
      oprot.writeFieldBegin('healTarget', TType.STRUCT, 4)
      self.healTarget.write(oprot)
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
