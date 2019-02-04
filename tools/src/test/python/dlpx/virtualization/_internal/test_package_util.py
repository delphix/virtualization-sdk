#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

from dlpx.virtualization._internal import package_util


class TestPackageUtil:
    @staticmethod
    def test_get_version():
        assert package_util.get_version() == '0.1.0'

    @staticmethod
    def test_get_internal_package_root():
        assert package_util.get_internal_package_root().endswith(
            'main/python/dlpx/virtualization/_internal')
