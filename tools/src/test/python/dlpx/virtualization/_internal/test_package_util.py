#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

from dlpx.virtualization._internal import package_util


class TestPackageUtil:
    @staticmethod
    def test_get_build_api_version():
        assert package_util.get_version() == '1.0.0'

    @staticmethod
    def test_get_engine_api_version():
        assert package_util.get_engine_api_version_from_settings() == '1.11.0'

    @staticmethod
    def test_get_build_api_version_json():
        build_api_version = {
            'type': 'APIVersion',
            'major': 1,
            'minor': 0,
            'micro': 0
        }
        assert package_util.get_build_api_version() == build_api_version

    @staticmethod
    def test_get_engine_api_version_json():
        engine_api_version = {
            'type': 'APIVersion',
            'major': 1,
            'minor': 11,
            'micro': 0
        }
        assert package_util.get_engine_api_version() == engine_api_version

    @staticmethod
    def test_get_internal_package_root():
        assert package_util.get_internal_package_root().endswith(
            'main/python/dlpx/virtualization/_internal')
