#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import pytest

#
# conftest.py is used to share fixtures among multiple tests files. pytest will
# automatically get discovered in the test class if the figure name is used
# as the input variable. The idea of fixtures is to define certain object
# configs and allow them to get used in different tests but also being allowed
# to set certain parts definated in other fixtures. Read more at:
# https://docs.pytest.org/en/latest/fixture.html
#


@pytest.fixture
def artifact_config(engine_api, discovery_definition):
    """
    This fixture creates base artifact that was generated from build and
    used in upload. If any fields besides engine_api needs to be changed,
    add fixtures below and add the function name to be part of the input to
    this function.
    """
    config = {
        'snapshotSchema': {
            'type': 'object'
        },
        'name': 'minimal_direct',
        'language': 'LUA',
        'hostTypes': ['UNIX'],
        'virtualSourceDefinition': {
            'status': '',
            'configure': 'return {}',
            'parameters': {
                'type': 'object',
                'properties': {
                    'instanceName': {
                        'prettyName': 'Instance Name',
                        'type': 'string',
                        'description': 'The name of the instance'
                    },
                }
            },
            'stop': '',
            'start': '',
            'unconfigure': '',
            'reconfigure': 'return {}',
            'preSnapshot': '',
            'type': 'ToolkitVirtualSource',
            'postSnapshot': 'return {}'
        },
        'linkedSourceDefinition': {
            'preSnapshot':
            '-- Small script.'
            '\n\nRunSync {'
            '\n   environment        = source.environment,'
            '\n   user               = source.environmentUser,'
            '\n   host               = source.host,'
            '\n   sourceDirectory    = source.dataDirectory,'
            '\n   excludePaths       = parameters.excludes,'
            '\n   followSymlinkPaths = parameters.followSymlinks'
            '\n}\n',
            'type':
            'ToolkitLinkedDirectSource',
            'postSnapshot':
            'return {}',
            'parameters': {
                'type': 'object',
                'properties': {}
            }
        },
        'version': '1.0.0',
        'buildApi': {
            'type': 'APIVersion',
            'major': 1,
            'minor': 11,
            'micro': 0
        },
        'defaultLocale': 'en-us',
        'prettyName': 'Minimalist Direct Toolkit',
        'type': 'Toolkit',
        'resources': {}
    }

    if engine_api is not None:
        config['engineApi'] = engine_api

    if discovery_definition is not None:
        config['discoveryDefinition'] = discovery_definition

    return config


@pytest.fixture
def engine_api():
    return {'type': 'APIVersion', 'major': 1, 'minor': 11, 'micro': 0}


@pytest.fixture
def discovery_definition():
    return {
        'type':
        'ToolkitDiscoveryDefinition',
        'repositoryNameField':
        'installPath',
        'repositoryIdentityFields': ['installPath'],
        'repositoryDiscovery':
        '-- Small script.'
        'installs = RunBash {'
        '\n    command         = resources["find_installs.sh"],'
        '\n    environment     = remote.environment,'
        '\n    user            = remote.environmentUser,'
        '\n    host            = remote.host,'
        '\n    variables       = {},'
        '\n    outputSchema    = {'
        '\n        type="array",'
        '\n        items={'
        '\n            type="object",'
        '\n            properties={'
        '\n                installPath = { type="string" },'
        '\n                version     = { type="string" }'
        '\n            }'
        '\n        }'
        '\n    }'
        '\n}'
        '\nreturn installs'
        '\n',
        'repositorySchema': {
            'type': 'object',
            'properties': {
                'version': {
                    'prettyName': 'Version',
                    'type': 'string',
                    'description': 'The version of the Delphix DB binaries'
                },
                'installPath': {
                    'prettyName':
                    'Delphix DB Binary Installation Path',
                    'type':
                    'string',
                    'description':
                    'The path to the Delphix DB installation binaries'
                }
            }
        },
        'sourceConfigNameField':
        'dataPath',
        'sourceConfigIdentityFields': ['dataPath'],
        'sourceConfigDiscovery':
        '-- Small script.'
        'instances = RunBash {'
        '\n    command        = resources["find_instances.sh"],'
        '\n    environment    = remote.environment,'
        '\n    user           = remote.environmentUser,'
        '\n    host           = remote.host,'
        '\n    variables      = {'
        '\n        INSTALLPATH = repository.installPath'
        '\n    },'
        '\n    outputSchema    = {'
        '\n        type="array",'
        '\n        items={'
        '\n            type="object",'
        '\n            properties={'
        '\n                dbName   = { type="string" },'
        '\n                dataPath = { type="string" },'
        '\n                port     = { type="string" }'
        '\n            }'
        '\n        }'
        '\n    }'
        '\n}'
        '\nreturn instances'
        '\n',
        'sourceConfigSchema': {
            'type': 'object',
            'properties': {
                'dbName': {
                    'prettyName': 'Delphix DB Name',
                    'type': 'string',
                    'description': 'The name of the Delphix DB instance.'
                },
                'dataPath': {
                    'prettyName': 'Data Path',
                    'type': 'string',
                    'description': 'The path to the Delphix DB instance data'
                },
                'port': {
                    'prettyName': 'Port',
                    'type': 'integer',
                    'description': 'The port of the Delphix DB'
                }
            }
        }
    }
