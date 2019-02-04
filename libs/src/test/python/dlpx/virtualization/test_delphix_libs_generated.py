#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

from google.protobuf import message


def test_import_common():
    from dlpx.virtualization import common_pb2
    assert issubclass(common_pb2.Repository, message.Message)


def test_import_libs():
    from dlpx.virtualization import delphix_libs_pb2
    assert issubclass(delphix_libs_pb2.RunSyncRequest, message.Message)
