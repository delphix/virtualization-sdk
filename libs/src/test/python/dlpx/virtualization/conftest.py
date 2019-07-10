#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import pytest
from dlpx.virtualization.common._common_classes import RemoteUser, RemoteHost, RemoteEnvironment, RemoteConnection


@pytest.fixture
def remote_user():
    return RemoteUser("user", "user-reference")


@pytest.fixture
def remote_host():
    return RemoteHost("host", "host-reference", "binary_path", "scratch_path")


@pytest.fixture
def remote_environment(remote_host):
    return RemoteEnvironment("environment",
                             "environment-reference",
                             remote_host)


@pytest.fixture
def remote_connection(remote_environment, remote_user):
    return RemoteConnection(remote_environment, remote_user)
