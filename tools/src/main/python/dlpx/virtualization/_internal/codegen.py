#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import copy
import errno
import json
import logging
import os
import shutil
import subprocess

from dlpx.virtualization._internal import exceptions

logger = logging.getLogger(__name__)
UNKNOWN_ERR = 'UNKNOWN_ERR'

# The Swagger JSON specification requires these following fields.
SWAGGER_JSON_FORMAT = {
    'swagger': '2.0',
    'info': {
        'version': '1.0.0',
        'title': None
    },
    'paths': {},
    'definitions': {}
}

#
# The default snapshot params we currently support. This is so that in the
# future when we want to support plugin author defined schemas for snapshot
# params the upgrade case will be relatively simple.
#

SNAPSHOT_PARAMS_JSON = {
    'snapshotParametersDefinition': {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'resync': {
                'type': 'boolean'
            }
        }
    }
}

SWAGGER_FILE_NAME = 'swagger.json'
OUTPUT_DIR_NAME = '.delphix-compile'
CODEGEN_PACKAGE = 'generated'
CODEGEN_MODULE = 'definitions'
SWAGGER_JAR = 'codegen/swagger-codegen-cli-2.3.1.jar'
CODEGEN_CONFIG = 'codegen/codegen-config.json'
CODEGEN_COPY_FILES = ['__init__.py', 'util.py', CODEGEN_MODULE]


def generate_python(name, source_dir, plugin_config_dir, schema_content):
    """Uses Swagger Codegen to generate the python code from the schema dict.


    Takes in a plugin config path reads it for information to determine what
    schemas to generate and where to put it. Run this to be able to write
    the plugin with defined schemas.

    Args:
        name (str): The pretty name of the plugin, required as part of the
            swagger json input file.
        source_dir (str): The path to the source directory where the generated
            code should be put into.
        plugin_config_dir (str): The directory that the plugin config was found
        schema_content (dict): The dict that is used to generate the swagger
            json input file. This is then used to generate the python paths
        final_dirname (str): The directory we want

    """
    #
    # Create the output dir that we're writting the swagger generated files to.
    # the dir will be a hidden directory because most the files are not
    # relevant to the plugin writer. We want to always force this to be
    # recreated.
    #
    output_dir = os.path.join(plugin_config_dir, OUTPUT_DIR_NAME)
    logger.info('Creating new output directory: {!r}'.format(output_dir))
    _make_dir(output_dir)

    #
    # Create the json with the correct Swagger JSON specification required to
    # generate the objects. Write it to the output dir that we created above.
    #
    logger.info('Writing the swagger file in {!r}'.format(output_dir))
    swagger_file = _write_swagger_file(name, schema_content, output_dir)

    #
    # Execute the swagger codegen jar that generates the python classes from
    # the schemas specified in the json. Run the jar making it write to the
    # output_dir again.
    #
    logger.info('Executing swagger codegen generate with'
                ' swagger file {!r}'.format(swagger_file))
    _execute_swagger_codegen(swagger_file, output_dir)

    #
    # Copy the python model classes to the src directory passed in. While doing
    # this, also switch up the import to only do `from generate` instead of
    # `from swagger_client.generate` etc... If this works than the python
    # classes were generated properly.
    #
    logger.info('Copying generated python files to'
                ' source directory {!r}'.format(source_dir))
    _copy_generated_to_dir(output_dir, source_dir)


def _make_dir(path):

    #
    # Delete the folder if it is there to clear the location. Ignore errors in
    # case the folder didn't exist. Since we'll be creating another dir at
    # that location, we should handle any errors when creating the dir.
    #
    shutil.rmtree(path, ignore_errors=True)
    try:
        os.mkdir(path)
        logger.debug('Successfully created directory {!r}'.format(path))
    except OSError as err:
        raise exceptions.UserError(
            'Unable to create new directory {!r}'
            '\nError code: {}. Error message: {}'.format(
                path, err.errno, os.strerror(err.errno)))


def _write_swagger_file(name, schema_dict, output_dir):
    swagger_json = copy.deepcopy(SWAGGER_JSON_FORMAT)
    swagger_json['info']['title'] = name
    swagger_json['definitions'] = copy.deepcopy(schema_dict)
    # Add in the snapshot param definition
    swagger_json['definitions'].update(SNAPSHOT_PARAMS_JSON)

    swagger_file = os.path.join(output_dir, SWAGGER_FILE_NAME)
    logger.info('Writing swagger file to {!r}'.format(swagger_file))
    #
    # Dump JSON into swagger json file. This should work since we just created
    # the dir `output_dir`. If this fails just let the full failure go through
    #
    with open(swagger_file, 'w') as f:
        # swagger_json is a dict json.dumps will be successful.
        f.write(json.dumps(swagger_json, indent=2))

    return swagger_file


def _execute_swagger_codegen(swagger_file, output_dir):
    jar = os.path.join(os.path.dirname(__file__), SWAGGER_JAR)
    codegen_config = os.path.join(os.path.dirname(__file__), CODEGEN_CONFIG)

    # Create the process that runs the jar putting stdout / stderr into pipes.
    try:
        process_inputs = [
            'java', '-jar', jar, 'generate', '-DsupportPython2=true', '-i',
            swagger_file, '-l', 'python-flask', '-c', codegen_config,
            '--model-package', CODEGEN_MODULE, '-o', output_dir
        ]

        logger.info('Running process with arguments: {!r}'.format(
            ' '.join(process_inputs)))
        process = subprocess.Popen(process_inputs,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except OSError as err:
        if err.errno == errno.ENOENT:
            raise exceptions.UserError('Swagger python code generation failed.'
                                       ' Make sure java is on the PATH.')
        raise exceptions.UserError(
            'Unable to run {!r} to generate python code.'
            '\nError code: {}. Error message: {}'.format(
                jar, err.errno, os.strerror(err.errno)))

    # Get the pipes pointed so we have access to them.
    stdout, stderr = process.communicate()

    #
    # Wait for the process to end and take the results. If res then we know
    # something failed so throw a UserError.
    #
    if process.wait():
        logger.error('stdout: {}'.format(stdout))
        logger.error('stderr: {}'.format(stderr))
        raise exceptions.UserError('Swagger python code generation failed.'
                                   'See logs for more information.')

    # Print the stdout and err into the logs.
    logger.info('stdout: {}'.format(stdout))
    logger.info('stderr: {}'.format(stderr))


def _copy_generated_to_dir(src_location, dst_location):
    """Copies the expected files from the src_location to the dst_location.

    Args:
        src_location (str): Location that the files/dirs will be found at.
        dst_location (str): Location that the files/dirs will be copied to.
    """
    #
    # output_dir is the dir that codegen had originally outputted to and
    # therefore is actually the location of the files being copied are where
    # as source_dir is actually the target destination for the copied files.
    #
    source_dir = os.path.join(src_location, CODEGEN_PACKAGE)
    destination_dir = os.path.join(dst_location, CODEGEN_PACKAGE)
    _make_dir(destination_dir)

    logger.info('Copying generated files {} from {!r} to {!r}.'.format(
        CODEGEN_COPY_FILES, source_dir, destination_dir))

    for name in CODEGEN_COPY_FILES:
        src = os.path.join(source_dir, name)
        try:
            #
            # Try copying as a directory first, if it's a dir then the dst
            # must include the name of of the dir for it to be copied there.
            #
            shutil.copytree(src, os.path.join(destination_dir, name))
            logger.info('Successfully copied directory {!r}.'.format(name))
        except OSError as err:
            if err.errno == errno.ENOTDIR or err.errno == errno.EINVAL:
                #
                # In the case that it's not a dir, this error would have been
                # caught. Try copying it as a file. The dst should not have the
                # name in it this time.
                #
                # errno.ENOTDIR is received on linux/mac and
                # errno.EINVAL is received on windows
                #
                shutil.copy2(src, destination_dir)
                logger.info('Successfully copied file {!r}.'.format(name))
            else:
                #
                # Since we're not expecting any other errors raise anything
                # that does exist.
                #
                raise
