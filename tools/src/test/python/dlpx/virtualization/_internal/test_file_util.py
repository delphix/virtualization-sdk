#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os

from dlpx.virtualization._internal import file_util


class TestFileUtil:
    @staticmethod
    def test_delete_paths(plugin_config_file, schema_file, src_dir):
        file_util.delete_paths(plugin_config_file, schema_file, src_dir)

        assert not os.path.exists(plugin_config_file)
        assert not os.path.exists(schema_file)
        assert not os.path.exists(src_dir)

    @staticmethod
    def test_delete_paths_none_values(plugin_config_file):
        file_util.delete_paths(plugin_config_file, None)

        assert not os.path.exists(plugin_config_file)
