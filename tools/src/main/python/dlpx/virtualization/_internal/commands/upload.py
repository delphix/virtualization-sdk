#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import errno
import json
import logging
import os

import requests

from dlpx.virtualization._internal import exceptions

logger = logging.getLogger(__name__)
UNKNOWN_ERR = 'UNKNOWN_ERR'


def upload(engine, user, upload_artifact, password):
    """
    Takes in the engine hostname/ip address, logs on and uploads the artifact
    passed in. The upload artifact should have been generated via the build
    command from a plugin. The file is expected to contain the delphix api
    version as well as be in the json format. During the process, print any
    errors that occur cleanly.

    Raises specifically:
        UserError
        InvalidArtifactError
        HttpPostError
        UnexpectedError
    """
    logger.debug('Upload parameters include'
                 ' engine: {},'
                 ' user: {},'
                 ' upload_artifact: {}'.format(engine, user, upload_artifact))
    logger.info('Uploading plugin artifact {!r} ...'.format(upload_artifact))

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
            'Unable to read upload artifact file {!r}'
            '\nError code: {}. Error message: {}'.format(
                upload_artifact, err.errno,
                errno.errorcode.get(err.errno, UNKNOWN_ERR)))

    engine_api = get_engine_api(content)

    # Create a new delphix session.
    session = DelphixClient(engine)
    session.login(engine_api, user, password)
    session.upload_plugin(os.path.basename(upload_artifact), content)


def get_engine_api(content):
    """
    Get Delphix Engine API and validate before returning. If the api is missing
    or malformed raise an InvalidArtifactError
    """
    if 'engineApi' in content:
        engine_api = content['engineApi']
        if (isinstance(engine_api, dict)
                and engine_api.get('type') == 'APIVersion'
                and isinstance(engine_api.get('major'), int)
                and isinstance(engine_api.get('minor'), int)
                and isinstance(engine_api.get('micro'), int)):
            logger.info('engineApi found: {}.'.format(json.dumps(engine_api)))
            return engine_api
        logger.debug('engineApi found but malformed: {!r}'.format(engine_api))
    raise exceptions.InvalidArtifactError()


class DelphixClient:
    """
    A DelphixClient is essentially a session that takes in a delphix engine.
    Before being able to do anything, the caller must login with the correct
    credentials as well as the used delphix engine api version. This class
    also has an upload plugin function that gets the token and attempts to
    upload the plugin. Methods can potentially raise HttpPostError and
    UnexpectedError.
    """
    __BOUNDARY = '----------boundary------'
    __UPLOAD_CONTENT = 'multipart/form-data; boundary={}'.format(__BOUNDARY)
    __cookie = None

    def __init__(self, engine):
        self.__engine = engine

    def login(self, engine_api, user, password):
        """
        Takes in the engine_api, user, and password and attempts to login to
        the engine. Can raise HttpPostError and UnexpectedError.
        """
        logger.info('Logging onto the Delphix Engine {!r}.'.format(
            self.__engine))
        self.__post('delphix/session',
                    data={
                        'type': 'APISession',
                        'version': engine_api
                    })
        logger.debug('Session started successfully.')
        self.__post('delphix/login',
                    data={
                        'type': 'LoginRequest',
                        'username': user,
                        'password': password
                    })
        logger.info('Successfully logged in as {!r}.'.format(user))

    def upload_plugin(self, name, content):
        """
        Takes in the plugin name and content (as a json). Attempts to upload
        the plugin onto the connected Delphix Engine. Can raise HttpPostError
        and UnexpectedError.
        """

        # Get the upload token.
        logger.debug('Getting token to do upload.')
        response = self.__post('delphix/toolkit/requestUploadToken')
        token = response['result']['token']
        logger.debug('Got token {!r} successfully.'.format(token))

        logger.info('Uploading plugin {!r}.'.format(name))
        # Encode plugin content.
        self.__post('delphix/data/upload',
                    content_type=self.__UPLOAD_CONTENT,
                    data=self.__encode(json.dumps(content), token, name))
        logger.info('Plugin was successfully uploaded.')

    def __post(self, resource, content_type='application/json', data=None):
        """
        Generates the http request post based on the resource. If no
        content_type is passed in assume it's a json. If the post fails we
        attempt to raise a specific error between HttpPostError and
        UnexpectedError.
        """
        # Form HTTP header and add the cookie if one has been set.
        headers = {'Content-type': content_type}
        if self.__cookie is not None:
            logger.debug('Cookie being used: {}'.format(self.__cookie))
            headers['Cookie'] = self.__cookie
        else:
            logger.debug('No cookie being used')

        url = 'http://{}/resources/json/{}'.format(self.__engine, resource)
        #
        # Issue post request that was passed in, if data is a dict then convert
        # it to a json string.
        #
        if data is not None and not isinstance(data, (str, bytes, unicode)):
            data = json.dumps(data)
        try:
            response = requests.post(url=url, data=data, headers=headers)
        except requests.exceptions.RequestException as err:
            raise exceptions.UserError(
                'Upload failed due to a http request failure.'
                '\n{}'.format(err))

        #
        # Save cookie if one was received because the next time a request
        # happens the newest cookie is expected. If the post recent cookie
        # returned isn't used the request will fail.
        #
        if 'set-cookie' in response.headers:
            self.__cookie = response.headers['set-cookie']
            logger.debug('New cookie found: {}'.format(self.__cookie))

        try:
            response_json = response.json()
        except ValueError:
            raise exceptions.UnexpectedError(response.status_code,
                                             response.text)

        logger.debug('Response body: {}'.format(json.dumps(response_json)))

        if (response.status_code == 200
                and response_json.get('type') == 'OKResult'):
            return response_json

        if response_json.get('type') == 'ErrorResult':
            raise exceptions.HttpPostError(response.status_code,
                                           response_json['error'])
        raise exceptions.UnexpectedError(response.status_code,
                                         json.dumps(response_json, indent=2))

    @staticmethod
    def __encode(content, token, filename):
        """
        Takes the content and figures out the content_type and body of the http
        request. This encode method only works for upload. We may end up using
        a library to generate the content_type and body instead.
        Need to figure out what lib to use for this instead.
        """
        encode_body = []

        # Add the metadata about the upload first
        encode_body.extend([
            '--{}'.format(DelphixClient.__BOUNDARY),
            'Content-Disposition: form-data; name="{}"'.format('token'),
            '',
            token,
        ])

        #
        # Put file contents in body. The upload server determines the
        # mime-type so no need to set it.
        #
        encode_body.extend([
            '--{}'.format(DelphixClient.__BOUNDARY),
            'Content-Disposition:'
            'form-data; name="file"; filename="{}"'.format(filename),
            'Content-Type: application/octet-stream',
            '',
            content,
        ])
        encode_body.extend(['--{}--'.format(DelphixClient.__BOUNDARY), ''])
        logger.debug('Generated body: {}'.format(encode_body))
        # Return context_type to use and body
        return '\r\n'.join(encode_body)
