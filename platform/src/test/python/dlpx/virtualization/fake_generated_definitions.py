class RepositoryDefinition(object):

  def __init__(self, name):
    self.__name = name

  @property
  def name(self):
    return self.__name

  @staticmethod
  def from_dict(input_dict):
    return RepositoryDefinition(input_dict["name"])

  def to_dict(self):
    return { "name": self.__name }

class SourceConfigDefinition(object):

  def __init__(self, name):
    self.__name = name

  @property
  def name(self):
    return self.__name

  @staticmethod
  def from_dict(input_dict):
    return SourceConfigDefinition(input_dict["name"])

  def to_dict(self):
    return { "name": self.__name }

class LinkedSourceDefinition(object):

  def __init__(self, name):
    self.__name = name

  @property
  def name(self):
    return self.__name

  @staticmethod
  def from_dict(input_dict):
    return LinkedSourceDefinition(input_dict["name"])

  def to_dict(self):
    return { "name": self.__name }

class VirtualSourceDefinition(object):

  def __init__(self, name):
    self.__name = name

  @property
  def name(self):
    return self.__name

  @staticmethod
  def from_dict(input_dict):
    return VirtualSourceDefinition(input_dict["name"])

  def to_dict(self):
    return { "name": self.__name }

class SnapshotDefinition(object):

  def __init__(self, name):
    self.__name = name

  @property
  def name(self):
    return self.__name

  @staticmethod
  def from_dict(input_dict):
    return SnapshotDefinition(input_dict["name"])

  def to_dict(self):
    return { "name": self.__name }
