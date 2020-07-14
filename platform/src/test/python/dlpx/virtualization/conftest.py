#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#

import pytest

#
# conftest.py is used to share fixtures among multiple tests files. pytest will
# automatically get discovered in the test class if the figure name is used
# as the input variable. The idea of fixtures is to define certain object
# configs and allow them to get used in different tests but also being allowed
# to set certain parts defined in other fixtures. Read more at:
# https://docs.pytest.org/en/latest/fixture.html
#

OBJECT_TYPES = [
    'repository', 'source_config', 'linked_source', 'virtual_source',
    'snapshot'
]


@pytest.fixture
def method_name(object_op):
    return 'add_{}'.format(object_op)


@pytest.fixture
def get_impls_to_exec(object_op):
    return 'get_{}_impls_to_exec'.format(object_op)
