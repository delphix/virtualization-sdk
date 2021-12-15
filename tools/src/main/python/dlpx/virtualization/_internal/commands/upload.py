#
# Copyright (c) 2019, 2021 by Delphix. All rights reserved.
#

import errno
import json
import logging
import os

from dlpx.virtualization._internal import delphix_client, exceptions
from dlpx.virtualization.common.util import to_str

logger = logging.getLogger(__name__)
UNKNOWN_ERR = 'UNKNOWN_ERR'


def upload(engine, user, upload_artifact, password, wait):
    """
    Takes in the engine hostname/ip address, logs on and uploads the artifact
    passed in. The upload artifact should have been generated via the build
    command from a plugin. The file is expected to contain the delphix api
    version as well as be in the json format. During the process, print any
    errors that occur cleanly.

    Raises specifically:
        UserError
        InvalidArtifactError
        HttpError
        UnexpectedError
        PluginUploadJobFailed
        PluginUploadWaitTimedOut
    """
    logger.debug('Upload parameters include'
                 ' engine: {},'
                 ' user: {},'
                 ' upload_artifact: {},'
                 ' wait: {}'.format(engine, user, upload_artifact, wait))
    logger.info('Uploading plugin artifact {} ...'.format(upload_artifact))

    #
    # Click handles the conversions for us, so we need not run inputs through to_str in
    # the cli upload function. However, this function may be called from places other
    # than its corresponding cli function, such as unit tests. As such, we should ensure
    # all appropriate inputs at this point are properly converted to unicode strings as
    # soon as they enter the program.
    #
    engine = to_str(engine)
    user = to_str(user)
    upload_artifact = to_str(upload_artifact)
    password = to_str(password)

    # Read content of upload artifact
    try:
        with open(upload_artifact, 'rb') as f:
            try:
                content = json.load(f)
            except ValueError:
                raise exceptions.UserError(
                    'Upload failed because the upload artifact was not a valid'
                    ' json file. Verify the file was built using the delphix'
                    ' build command.')
    except IOError as err:
        raise exceptions.UserError(
            'Unable to read upload artifact file \'{}\''
            '\nError code: {}. Error message: {}'.format(
                upload_artifact, err.errno,
                errno.errorcode.get(err.errno, UNKNOWN_ERR)))

    # Create a new delphix session.
    client = delphix_client.DelphixClient(engine)
    engine_api = client.get_engine_api(content)
    client.login(engine_api, user, password)
    client.upload_plugin(os.path.basename(upload_artifact), content, wait)
