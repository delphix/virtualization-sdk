#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import ast
import json
import os

import mock
import pytest

from dlpx.virtualization._internal import exceptions, plugin_util
from dlpx.virtualization._internal.commands import initialize as init


@pytest.fixture
def schema_template():
    with open(init.SCHEMA_TEMPLATE_PATH, 'r') as f:
        return json.load(f)


@pytest.fixture
def entry_point_template():
    with open(init.ENTRY_POINT_TEMPLATE_PATH, 'r') as f:
        return f.read()


class TestInitialize:
    @staticmethod
    def test_init(tmpdir, schema_template, entry_point_template, plugin_name,
                  plugin_pretty_name):
        # Initialize an empty directory.
        init.init(tmpdir.strpath, plugin_name, plugin_util.STAGED_TYPE,
                  plugin_pretty_name)

        config = plugin_util.read_plugin_config_file(
            os.path.join(tmpdir.strpath, init.DEFAULT_PLUGIN_CONFIG_FILE))

        # Validate the config file is as we expect.
        plugin_util.validate_plugin_config_content(config)
        assert config['pluginType'] == plugin_util.STAGED_TYPE
        assert config['name'] == plugin_name
        assert config['prettyName'] == plugin_pretty_name
        assert config['entryPoint'] == init.DEFAULT_ENTRY_POINT
        assert config['srcDir'] == os.path.join(tmpdir.strpath,
                                                init.DEFAULT_SRC_DIRECTORY)
        assert config['schemaFile'] == os.path.join(tmpdir.strpath,
                                                    init.DEFAULT_SCHEMA_FILE)

        # Validate the schema file is identical to the template.
        with open(config['schemaFile'], 'r') as f:
            schema = json.load(f)
            assert schema == schema_template

        # Rebuild the entry file name from the entry point in the config file.
        entry_module, _ = config['entryPoint'].split(':')
        entry_file = entry_module + '.py'

        # Validate the entry file is identical to the template.
        with open(os.path.join(config['srcDir'], entry_file), 'r') as f:
            contents = f.read()
            assert contents == entry_point_template

    @staticmethod
    def test_invalid_with_config_file(plugin_config_file, plugin_name):
        with pytest.raises(exceptions.PathExistsError):
            init.init(
                os.path.dirname(plugin_config_file), plugin_name,
                plugin_util.DIRECT_TYPE, None)

    @staticmethod
    def test_invalid_with_schema_file(schema_file, plugin_name):
        with pytest.raises(exceptions.PathExistsError):
            init.init(
                os.path.dirname(schema_file), plugin_name,
                plugin_util.DIRECT_TYPE, None)

    @staticmethod
    def test_invalid_with_src_dir(src_dir, plugin_name):
        with pytest.raises(exceptions.PathExistsError):
            init.init(
                os.path.dirname(src_dir), plugin_name, plugin_util.DIRECT_TYPE,
                None)

    @staticmethod
    @mock.patch('yaml.dump')
    @mock.patch('dlpx.virtualization._internal.file_util.delete_paths')
    def test_init_calls_cleanup_on_failure(mock_cleanup, mock_yaml_dump,
                                           tmpdir, plugin_name,
                                           plugin_pretty_name):
        mock_yaml_dump.side_effect = RuntimeError()
        with pytest.raises(exceptions.UserError):
            init.init(tmpdir.strpath, plugin_name, plugin_util.STAGED_TYPE,
                      plugin_pretty_name)

        mock_cleanup.assert_called_once_with(init.DEFAULT_PLUGIN_CONFIG_FILE,
                                             init.DEFAULT_SCHEMA_FILE,
                                             init.DEFAULT_SRC_DIRECTORY)

    @staticmethod
    def test_default_schema_definition(schema_template):
        plugin_util.validate_schemas(schema_template)

        # Validate the repository schema only has the 'name' property.
        assert len(schema_template['repositoryDefinition']
                   ['properties']) == 1, json.dumps(
                       schema_template['repositoryDefinition'])
        assert 'name' in schema_template['repositoryDefinition']['properties']
        assert schema_template['repositoryDefinition']['nameField'] == 'name'
        assert schema_template['repositoryDefinition']['identityFields'] == [
            'name'
        ]

        # Validate the source config schema only has the 'name' property.
        assert len(schema_template['sourceConfigDefinition']
                   ['properties']) == 1, json.dumps(
                       schema_template['sourceConfigDefinition'])
        assert 'name' in schema_template['sourceConfigDefinition'][
            'properties']
        assert schema_template['sourceConfigDefinition']['nameField'] == 'name'
        assert schema_template['sourceConfigDefinition']['identityFields'] == [
            'name'
        ]

        #
        # Validate the linked source, virtual source, and snapshot definitions
        # have no properties.
        #
        assert schema_template['linkedSourceDefinition']['properties'] == {}
        assert schema_template['virtualSourceDefinition']['properties'] == {}
        assert schema_template['snapshotDefinition']['properties'] == {}

    @staticmethod
    def test_default_entry_point(entry_point_template):
        tree = ast.parse(entry_point_template)
        for stmt in ast.walk(tree):
            if isinstance(stmt, ast.Assign):
                #
                # Validate that the default entry point has something being
                # assigned to it.
                #
                if stmt.targets[0].id == init.DEFAULT_ENTRY_POINT_SYMBOL:
                    return

        raise RuntimeError(("Failed to find assignment to variable '{}' "
                            "in entry point template file.").format(
                                init.DEFAULT_ENTRY_POINT_SYMBOL))
