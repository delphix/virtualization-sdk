#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import ast
import json
import os

import jinja2
import mock
import pytest
from dlpx.virtualization._internal import (exceptions, plugin_util,
                                           plugin_validator, schema_validator,
                                           util_classes)
from dlpx.virtualization._internal.commands import initialize as init


@pytest.fixture
def schema_template():
    with open(init.SCHEMA_TEMPLATE_PATH, 'r') as f:
        return json.load(f)


@pytest.fixture
def entry_point_template():
    with open(
            os.path.join(init.PLUGIN_TEMPLATE_DIR,
                         init.ENTRY_POINT_TEMPLATE_NAME), 'r') as f:
        return f.read()


def direct_operations_template():
    with open(
            os.path.join(init.PLUGIN_TEMPLATE_DIR,
                         init.DIRECT_OPERATIONS_TEMPLATE_NAME), 'r') as f:
        return f.read()


def staged_operations_template():
    with open(
            os.path.join(init.PLUGIN_TEMPLATE_DIR,
                         init.STAGED_OPERATIONS_TEMPLATE_NAME), 'r') as f:
        return f.read()


@pytest.fixture
def format_entry_point_template(entry_point_template):
    template = jinja2.Environment().from_string(entry_point_template)

    def format_template(plugin_name, ingestion_strategy):
        if ingestion_strategy == plugin_util.DIRECT_TYPE:
            operations = direct_operations_template()
        elif ingestion_strategy == plugin_util.STAGED_TYPE:
            operations = staged_operations_template()
        else:
            raise RuntimeError(
                'Got unrecognized ingestion strategy: {!r}'.format(
                    ingestion_strategy))
        return template.render(name=repr(plugin_name),
                               linked_operations=operations)

    return format_template


class TestInitialize:
    @staticmethod
    @pytest.mark.parametrize(
        'ingestion_strategy',
        [plugin_util.DIRECT_TYPE, plugin_util.STAGED_TYPE])
    def test_init(tmpdir, ingestion_strategy, schema_template, plugin_name,
                  plugin_pretty_name, format_entry_point_template):
        # Initialize an empty directory.
        init.init(tmpdir.strpath, plugin_name, ingestion_strategy,
                  plugin_pretty_name)

        # Validate the config file is as we expect.
        config = plugin_util.read_and_validate_plugin_config_file(
            os.path.join(tmpdir.strpath, init.DEFAULT_PLUGIN_CONFIG_FILE),
            True, False)

        assert config['pluginType'] == ingestion_strategy
        assert config['name'] == plugin_name
        assert config['prettyName'] == plugin_pretty_name
        assert config['entryPoint'] == init.DEFAULT_ENTRY_POINT
        assert config['srcDir'] == init.DEFAULT_SRC_DIRECTORY
        assert config['schemaFile'] == init.DEFAULT_SCHEMA_FILE

        # Validate the schema file is identical to the template.
        schema_file_path = os.path.join(tmpdir.strpath, config['schemaFile'])
        with open(schema_file_path, 'r') as f:
            schema = json.load(f)
            assert schema == schema_template

        # Rebuild the entry file name from the entry point in the config file.
        entry_module, _ = config['entryPoint'].split(':')
        entry_file = entry_module + '.py'

        # Validate the entry file is identical to the template.
        entry_file_path = os.path.join(tmpdir.strpath, config['srcDir'],
                                       entry_file)
        with open(entry_file_path, 'r') as f:
            contents = f.read()
            assert contents == format_entry_point_template(
                plugin_name, ingestion_strategy)

    @staticmethod
    @pytest.mark.parametrize(
        'ingestion_strategy',
        [plugin_util.DIRECT_TYPE, plugin_util.STAGED_TYPE])
    def test_plugin_from_init_is_valid(tmpdir, ingestion_strategy, plugin_name,
                                       plugin_pretty_name):
        # This test will fail with a DIRECT ingestion strategy due to PYT-486.
        # Once PYT-486 is fixed, remove this check.
        if ingestion_strategy == plugin_util.DIRECT_TYPE:
            pytest.skip('Skipping DIRECT ingestion strategy due to PYT-486.')
        init.init(tmpdir.strpath, plugin_name, ingestion_strategy,
                  plugin_pretty_name)

        plugin_config_file = os.path.join(tmpdir.strpath,
                                          init.DEFAULT_PLUGIN_CONFIG_FILE)
        schema_file = os.path.join(tmpdir.strpath, init.DEFAULT_SCHEMA_FILE)
        validator = plugin_validator.PluginValidator(plugin_config_file,
                                                     schema_file, True, True)
        validator.validate()

        assert not validator.warnings

    @staticmethod
    def test_invalid_with_config_file(plugin_config_file, plugin_name):
        with pytest.raises(exceptions.PathExistsError):
            init.init(os.path.dirname(plugin_config_file), plugin_name,
                      plugin_util.DIRECT_TYPE, None)

    @staticmethod
    def test_invalid_with_schema_file(schema_file, plugin_name):
        with pytest.raises(exceptions.PathExistsError):
            init.init(os.path.dirname(schema_file), plugin_name,
                      plugin_util.DIRECT_TYPE, None)

    @staticmethod
    def test_invalid_with_src_dir(src_dir, plugin_name):
        with pytest.raises(exceptions.PathExistsError):
            init.init(os.path.dirname(src_dir), plugin_name,
                      plugin_util.DIRECT_TYPE, None)

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

        src_dir_path = os.path.join(tmpdir.strpath, init.DEFAULT_SRC_DIRECTORY)
        config_file_path = os.path.join(tmpdir.strpath,
                                        init.DEFAULT_PLUGIN_CONFIG_FILE)
        schema_file_path = os.path.join(tmpdir.strpath,
                                        init.DEFAULT_SCHEMA_FILE)

        mock_cleanup.assert_called_once_with(config_file_path,
                                             schema_file_path, src_dir_path)

    @staticmethod
    def test_default_schema_definition(schema_template):
        validator = schema_validator.SchemaValidator(
            None, plugin_util.PLUGIN_SCHEMA, util_classes.ValidationMode.ERROR,
            schema_template)
        validator.validate()

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
    def test_default_entry_point(plugin_name):
        entry_point_contents = init._get_entry_point_contents(
            plugin_name, plugin_util.DIRECT_TYPE)
        tree = ast.parse(entry_point_contents)
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
