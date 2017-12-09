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


class StatusCode:
  SUCCESS = 1
  ILLEGAL_TARGET = 2
  GAME_NOT_STARTED = 10
  GAME_ENDED = 11

  _VALUES_TO_NAMES = {
    1: "SUCCESS",
    2: "ILLEGAL_TARGET",
    10: "GAME_NOT_STARTED",
    11: "GAME_ENDED",
  }

  _NAMES_TO_VALUES = {
    "SUCCESS": 1,
    "ILLEGAL_TARGET": 2,
    "GAME_NOT_STARTED": 10,
    "GAME_ENDED": 11,
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

class GameStatus:
  WAITING_FOR_PLAYERS = 1
  STARTED = 2
  ENDED = 3

  _VALUES_TO_NAMES = {
    1: "WAITING_FOR_PLAYERS",
    2: "STARTED",
    3: "ENDED",
  }

  _NAMES_TO_VALUES = {
    "WAITING_FOR_PLAYERS": 1,
    "STARTED": 2,
    "ENDED": 3,
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

class StartGameResponse:
  """
  Attributes:
   - status
   - initialLocation
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'status', None, None, ), # 1
    (2, TType.STRUCT, 'initialLocation', (Location, Location.thrift_spec), None, ), # 2
  )

  def __init__(self, status=None, initialLocation=None,):
    self.status = status
    self.initialLocation = initialLocation

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
          self.status = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.initialLocation = Location()
          self.initialLocation.read(iprot)
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
    oprot.writeStructBegin('StartGameResponse')
    if self.status is not None:
      oprot.writeFieldBegin('status', TType.I32, 1)
      oprot.writeI32(self.status)
      oprot.writeFieldEnd()
    if self.initialLocation is not None:
      oprot.writeFieldBegin('initialLocation', TType.STRUCT, 2)
      self.initialLocation.write(oprot)
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

class ClientState:
  """
  Attributes:
   - location
   - health
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'location', (Location, Location.thrift_spec), None, ), # 1
    (2, TType.I32, 'health', None, None, ), # 2
  )

  def __init__(self, location=None, health=None,):
    self.location = location
    self.health = health

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
          self.location = Location()
          self.location.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.health = iprot.readI32();
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
    oprot.writeStructBegin('ClientState')
    if self.location is not None:
      oprot.writeFieldBegin('location', TType.STRUCT, 1)
      self.location.write(oprot)
      oprot.writeFieldEnd()
    if self.health is not None:
      oprot.writeFieldBegin('health', TType.I32, 2)
      oprot.writeI32(self.health)
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
    (3, TType.I32, 'attackTarget', None, None, ), # 3
    (4, TType.I32, 'healTarget', None, None, ), # 4
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
        if ftype == TType.I32:
          self.attackTarget = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I32:
          self.healTarget = iprot.readI32();
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
      oprot.writeFieldBegin('attackTarget', TType.I32, 3)
      oprot.writeI32(self.attackTarget)
      oprot.writeFieldEnd()
    if self.healTarget is not None:
      oprot.writeFieldBegin('healTarget', TType.I32, 4)
      oprot.writeI32(self.healTarget)
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

class GameState:
  """
  Attributes:
   - clientStates
   - clusterAssignments
  """

  thrift_spec = (
    None, # 0
    (1, TType.MAP, 'clientStates', (TType.I32,None,TType.STRUCT,(ClientState, ClientState.thrift_spec)), None, ), # 1
    (2, TType.MAP, 'clusterAssignments', (TType.I32,None,TType.I32,None), None, ), # 2
  )

  def __init__(self, clientStates=None, clusterAssignments=None,):
    self.clientStates = clientStates
    self.clusterAssignments = clusterAssignments

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
        if ftype == TType.MAP:
          self.clientStates = {}
          (_ktype1, _vtype2, _size0 ) = iprot.readMapBegin()
          for _i4 in xrange(_size0):
            _key5 = iprot.readI32();
            _val6 = ClientState()
            _val6.read(iprot)
            self.clientStates[_key5] = _val6
          iprot.readMapEnd()
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.MAP:
          self.clusterAssignments = {}
          (_ktype8, _vtype9, _size7 ) = iprot.readMapBegin()
          for _i11 in xrange(_size7):
            _key12 = iprot.readI32();
            _val13 = iprot.readI32();
            self.clusterAssignments[_key12] = _val13
          iprot.readMapEnd()
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
    oprot.writeStructBegin('GameState')
    if self.clientStates is not None:
      oprot.writeFieldBegin('clientStates', TType.MAP, 1)
      oprot.writeMapBegin(TType.I32, TType.STRUCT, len(self.clientStates))
      for kiter14,viter15 in self.clientStates.items():
        oprot.writeI32(kiter14)
        viter15.write(oprot)
      oprot.writeMapEnd()
      oprot.writeFieldEnd()
    if self.clusterAssignments is not None:
      oprot.writeFieldBegin('clusterAssignments', TType.MAP, 2)
      oprot.writeMapBegin(TType.I32, TType.I32, len(self.clusterAssignments))
      for kiter16,viter17 in self.clusterAssignments.items():
        oprot.writeI32(kiter16)
        oprot.writeI32(viter17)
      oprot.writeMapEnd()
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

class ActionResponse:
  """
  Attributes:
   - status
   - updatedGameState
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'status', None, None, ), # 1
    (2, TType.STRUCT, 'updatedGameState', (GameState, GameState.thrift_spec), None, ), # 2
  )

  def __init__(self, status=None, updatedGameState=None,):
    self.status = status
    self.updatedGameState = updatedGameState

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
          self.status = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.updatedGameState = GameState()
          self.updatedGameState.read(iprot)
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
    oprot.writeStructBegin('ActionResponse')
    if self.status is not None:
      oprot.writeFieldBegin('status', TType.I32, 1)
      oprot.writeI32(self.status)
      oprot.writeFieldEnd()
    if self.updatedGameState is not None:
      oprot.writeFieldBegin('updatedGameState', TType.STRUCT, 2)
      self.updatedGameState.write(oprot)
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