#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import copy
import errno
import json
import logging
import os
import re
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

SWAGGER_FILE_NAME = 'swagger.json'
OUTPUT_DIR_NAME = '.delphix-compile'
SWAGGER_SERVER_MODULE = 'swagger_server'
SWAGGER_JAR = 'codegen/swagger-codegen-cli-2.3.1.jar'


def generate_python(name, source_dir, plugin_config_dir, schema_content,
                    final_dirname):
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
    logger.info('Creating new directory {!r}'.format(output_dir))
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
    _execute_swagger_codegen(swagger_file, output_dir, final_dirname)

    #
    # Copy the python model classes to the src directory passed in. While doing
    # this, also switch up the import to only do `from generate` instead of
    # `from swagger_client.generate` etc... If this works than the python
    # classes were generated properly.
    #
    logger.info('Moving generated python files to'
                ' source directory {!r}'.format(source_dir))
    _copy_generated_to_dir(source_dir, output_dir, final_dirname)


def _make_dir(path):
    """Make a dir given the path.

    Takes in a path and makes a directory there. The assumption is that the
    parent dir that it is in already exists. For example if the path passed in
    is `/this/is/a/test/path` the folder `/this/is/a/test` should already
    exist.

    Args:
        path (str): The path to the directory that is being created.
    """

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
    swagger_json['definitions'] = schema_dict

    outfile = os.path.join(output_dir, SWAGGER_FILE_NAME)
    # Dump JSON into swagger json file. This should work since we just created
    # the dir `output_dir`. If this fails just let the full failure go through
    with open(outfile, 'w') as f:
        # swagger_json is a dict json.dumps will be successful.
        f.write(json.dumps(swagger_json, indent=2))

    return outfile


def _execute_swagger_codegen(swagger_file, output_dir, final_dirname):
    jar = os.path.join(os.path.dirname(__file__), SWAGGER_JAR)

    # Create the process that runs the jar putting stdout / stderr into pipes.
    try:
        process_inputs = [
            'java', '-jar', jar, 'generate', '-i', swagger_file,
            '--model-package', final_dirname, '-l', 'python-flask',
            '-DsupportPython2=true', '-o', output_dir
        ]

        logger.info('Running process with arguments: {!r}'.format(
            ' '.join(process_inputs)))
        process = subprocess.Popen(
            process_inputs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as err:
        if err.errno == errno.ENOENT:
            raise exceptions.UserError('Swagger python code generation failed.'
                                       ' Make sure java is on the PATH.')
        raise exceptions.UserError(
            'Unable to generate  {!r}'
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


def _copy_generated_to_dir(source_dir, output_dir, final_dirname):
    _make_dir(os.path.join(source_dir, final_dirname))
    swagger_server_dir = os.path.join(output_dir, SWAGGER_SERVER_MODULE)
    generated_dir = os.path.join(swagger_server_dir, final_dirname)
    generated_files = os.listdir(generated_dir)
    #
    # Go through all the files generated and modify them to have the right
    # imports if there are any internal objects.
    #
    for file_name in generated_files:
        full_path = os.path.join(generated_dir, file_name)
        if os.path.isfile(full_path):
            _copy_file_with_correct_imports(file_name, full_path, source_dir,
                                            final_dirname)

    # Also must copy the util.py file and move it to the the generated folder
    util_file_name = 'util.py'
    util_full_path = os.path.join(swagger_server_dir, util_file_name)
    _copy_file_with_correct_imports(util_file_name, util_full_path, source_dir,
                                    final_dirname)


def _copy_file_with_correct_imports(file_name, full_path, source_dir,
                                    final_dirname):
    final_dir = os.path.join(source_dir, final_dirname)
    with open(full_path, 'r') as f:
        content = f.read()

    # First change 'from swagger_server.generated.<>' to  'from generated.<>'
    orig_regex = r'from {}.{}.(\S)'.format(SWAGGER_SERVER_MODULE,
                                           final_dirname)
    new_regex = r'from {}.\1'.format(final_dirname)
    content_mid = re.sub(orig_regex, new_regex, content)

    # Next change 'from swagger_server import <>' to 'from generated import <>'
    orig_regex = r'from {} import'.format(SWAGGER_SERVER_MODULE)
    new_regex = r'from {} import'.format(final_dirname)
    content_new = re.sub(orig_regex, new_regex, content_mid)

    final_path = os.path.join(final_dir, file_name)
    with open(final_path, 'w') as f:
        f.write(content_new)
