#
# Copyright (c) 2019, 2022 by Delphix. All rights reserved.
#
import os
from dlpx.virtualization._internal import package_util

import pytest


class TestPackageUtil:
    @staticmethod
    def test_get_version():
        assert package_util.get_version() == '4.0.3'

    @staticmethod
    def test_get_virtualization_api_version():
        assert package_util.get_virtualization_api_version() == '1.6.3'

    @staticmethod
    def test_get_engine_api_version():
        assert package_util.get_engine_api_version_from_settings() == '1.11.11'

    @staticmethod
    def test_get_build_api_version_json():
        build_api_version = {
            'type': 'APIVersion',
            'major': 1,
            'minor': 6,
            'micro': 3
        }
        assert package_util.get_build_api_version() == build_api_version

    @staticmethod
    def test_get_engine_api_version_json():
        engine_api_version = {
            'type': 'APIVersion',
            'major': 1,
            'minor': 11,
            'micro': 11
        }
        assert package_util.get_engine_api_version() == engine_api_version

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
