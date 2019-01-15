#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os

import virtualization._internal
from virtualization._internal import package_util


class TestPackageUtil:
    @staticmethod
    def test_get_version():
        assert package_util.get_version() == '0.1.0'

    @staticmethod
    def test_get_internal_package_root():
        assert package_util.get_internal_package_root() == os.path.dirname(
            virtualization._internal.__file__)
