#
# Copyright (c) 2020 by Delphix. All rights reserved.
#

import os

UNIX_HOST_TYPE = 'UNIX'
WINDOWS_HOST_TYPE = 'WINDOWS'
STAGED_TYPE = 'STAGED'
DIRECT_TYPE = 'DIRECT'

OUTPUT_DIR_NAME = '.dvp-gen-output'
PLUGIN_SCHEMAS_DIR = os.path.join(os.path.dirname(__file__),
                                  'validation_schemas')
PLUGIN_CONFIG_SCHEMA = os.path.join(PLUGIN_SCHEMAS_DIR,
                                    'plugin_config_schema.json')

PLUGIN_CONFIG_SCHEMA_NO_ID_VALIDATION = os.path.join(
    PLUGIN_SCHEMAS_DIR, 'plugin_config_schema_no_id_validation.json')

PLUGIN_SCHEMA = os.path.join(PLUGIN_SCHEMAS_DIR, 'plugin_schema.json')
