#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

from google.protobuf import message


def test_import_common():
    from dlpx.virtualization.api import common_pb2
    assert issubclass(common_pb2.Repository, message.Message)
