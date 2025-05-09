#
# Copyright (c) 2019, 2022 by Delphix. All rights reserved.
#
import os

import pytest

from dlpx.virtualization._internal import package_util

DVP_VERSION = '5.0.1'
DVP_API_VERSION = '1.9.0'


class TestPackageUtil:
    @staticmethod
    def test_get_version():
        assert package_util.get_version() == DVP_VERSION

    @staticmethod
    def test_get_virtualization_api_version():
        assert package_util.get_virtualization_api_version() == DVP_API_VERSION

    @staticmethod
    def test_get_engine_api_version(engine_api_version_string):
        assert package_util.get_engine_api_version_from_settings() \
               == engine_api_version_string

    @staticmethod
    def test_get_build_api_version_json():
        major, minor, micro = (
            int(n) for n in DVP_API_VERSION.split('.'))
        build_api_version = {
            'type': 'APIVersion',
            'major': major,
            'minor': minor,
            'micro': micro
        }
        assert package_util.get_build_api_version() == build_api_version

    @staticmethod
    def test_get_engine_api_version_json(engine_api):
        assert package_util.get_engine_api_version() == engine_api

    @staticmethod
    def test_get_internal_package_root():
        assert package_util.get_internal_package_root().endswith(
            os.path.join('dlpx', 'virtualization', '_internal'))

    @staticmethod
    @pytest.mark.parametrize('version_string', [
        '1.1.0', '   1.1.0', '1.1.0-internal-001', '  1.1.0-internal-001',
        ' 1.1.0-internal-002   ', '1.1.0whatever'
    ])
    def test_get_external_version_string(version_string):
        assert package_util.get_external_version_string(
            version_string) == '1.1.0'
