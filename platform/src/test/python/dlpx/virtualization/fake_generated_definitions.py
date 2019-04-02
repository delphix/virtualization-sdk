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
