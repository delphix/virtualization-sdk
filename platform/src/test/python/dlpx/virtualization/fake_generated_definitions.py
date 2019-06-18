class Model(object):
    # swaggerTypes: The key is attribute name and the
    # value is attribute type.
    swagger_types = {}

    # attributeMap: The key is attribute name and the
    # value is json key in definition.
    attribute_map = {}


class RepositoryDefinition(Model):
  def __init__(self, name):
    self.swagger_types = {
      'name': str
    }

    self.attribute_map = {
      'name': 'name'
    }
    self._name = name

  @property
  def name(self):
    return self._name

  @staticmethod
  def from_dict(input_dict):
    return RepositoryDefinition(input_dict['name'])

  def to_dict(self):
    return { "name": self._name }


class SourceConfigDefinition(Model):
  def __init__(self, name):
    self.swagger_types = {
      'name': str
    }

    self.attribute_map = {
      'name': 'name'
    }
    self._name = name

  @property
  def name(self):
    return self._name

  @staticmethod
  def from_dict(input_dict):
    return SourceConfigDefinition(input_dict['name'])

  def to_dict(self):
    return { "name": self._name }


class LinkedSourceDefinition(Model):
  def __init__(self, name):
    self.swagger_types = {
      'name': str
    }

    self.attribute_map = {
      'name': 'name'
    }
    self._name = name

  @property
  def name(self):
    return self._name

  @staticmethod
  def from_dict(input_dict):
    return LinkedSourceDefinition(input_dict['name'])


class VirtualSourceDefinition(Model):
  def __init__(self, name):
    self.swagger_types = {
      'name': str
    }

    self.attribute_map = {
      'name': 'name'
    }
    self._name = name

  @property
  def name(self):
    return self._name

  @staticmethod
  def from_dict(input_dict):
    return VirtualSourceDefinition(input_dict['name'])

  def to_dict(self):
    return { "name": self._name }


class SnapshotDefinition(Model):
  def __init__(self, name):
    self.swagger_types = {
      'name': str
    }

    self.attribute_map = {
      'name': 'name'
    }
    self._name = name

  @property
  def name(self):
    return self._name

  @staticmethod
  def from_dict(input_dict):
    return SnapshotDefinition(input_dict['name'])

  def to_dict(self):
    return { "name": self._name }


class SnapshotParametersDefinition(Model):
  """
  The appdata snapshot parameter will eventually be customizable but for now
  this just follows the old appdata parameter where the delphix user can decide
  if resync is true or not. This will now go into pre and post snapshot
  operations rather than the resync operation. The main point is customers will
  set this to be true is that this means the operation is a "hard" resync and
  that all data should be refreshed.
  """
  def __init__(self, resync):
    self.swagger_types = {
      'resync': bool
    }

    self.attribute_map = {
      'resync': 'resync'
    }
    self._resync = resync

  @property
  def resync(self):
    return self._resync

  @staticmethod
  def from_dict(input_dict):
    return SnapshotParametersDefinition(input_dict['resync'])

  def to_dict(self):
    return { "resync": self._resync }
