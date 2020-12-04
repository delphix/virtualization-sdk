#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import logging
import threading
import time

import requests
from dlpx.virtualization._internal import exceptions, plugin_util

logger = logging.getLogger(__name__)


class DelphixClient(object):
    """
    A DelphixClient is essentially a session that takes in a Delphix Engine.
    Before being able to do anything, the caller must login with the correct
    credentials as well as the used Delphix Engine API version. Methods can
    potentially raise HttpPostError and UnexpectedError.
    """
    __BOUNDARY = '----------boundary------'
    __UPLOAD_CONTENT = 'multipart/form-data; boundary={}'.format(__BOUNDARY)
    __JOB_POLLING_INTERVAL = 5
    __WAIT_TIMEOUT_SECONDS = 3600
    __cookie = None

    def __init__(self, engine, timeout=None):
        self.__engine = engine
        if timeout is not None:
            self.__WAIT_TIMEOUT_SECONDS = timeout

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

    @staticmethod
    def get_engine_api(artifact_content):
        """
        Get Delphix Engine API in the upload artifact content and
        validate before returning. If the api is missing or malformed
        raise an InvalidArtifactError
        """
        if 'engineApi' in artifact_content:
            engine_api = artifact_content['engineApi']
            if (isinstance(engine_api, dict)
                    and engine_api.get('type') == 'APIVersion'
                    and isinstance(engine_api.get('major'), int)
                    and isinstance(engine_api.get('minor'), int)
                    and isinstance(engine_api.get('micro'), int)):
                logger.info('engineApi found: {}.'.format(
                    json.dumps(engine_api)))
                return engine_api
            logger.debug(
                'engineApi found but malformed: {!r}'.format(engine_api))
        raise exceptions.InvalidArtifactError()

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
            raise exceptions.UserError('Encountered a http request failure.'
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
                and (response_json.get('type') == 'OKResult'
                     or response_json.get('type') == 'DataResult')):
            return response_json

        if response_json.get('type') == 'ErrorResult':
            raise exceptions.HttpError(response.status_code,
                                       response_json['error'])
        raise exceptions.UnexpectedError(response.status_code,
                                         json.dumps(response_json, indent=2))

    def __get(self, resource, content_type='application/json', stream=False):
        """
        Generates the http request get based on the resource provided. If no
        content_type is passed in assume it's application/json. If the get
        fails we attempt to raise a specific error between HttpGetError and
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

        try:
            response = requests.get(url=url, headers=headers, stream=stream)
        except requests.exceptions.RequestException as err:
            raise exceptions.UserError('Encountered a http request failure.'
                                       '\n{}'.format(err))

        #
        # Save cookie if one was received because the next time a request
        # happens the newest cookie is expected. If the post recent cookie
        # returned isn't used the request will fail.
        #
        if 'set-cookie' in response.headers:
            self.__cookie = response.headers['set-cookie']
            logger.debug('New cookie found: {}'.format(self.__cookie))

        if response.status_code == 200:
            return response
        else:
            response_error = None
            try:
                response_error = response.json()['error']
            except ValueError:
                pass
            raise exceptions.HttpError(response.status_code, response_error)

    def __get_plugin_ref_from_id(self, plugin_name, plugin_id):

        logger.info('Getting plugin object ref for {}'.format(plugin_name))

        plugin_response = self.__get('delphix/toolkit')
        try:
            plugins = plugin_response.json()
        except ValueError:
            raise exceptions.UnexpectedError(plugin_response.status_code,
                                             plugin_response.text)

        for p in plugins['result']:
            #
            # Compare the plugin id to the name field from each plugin
            # and make sure the plugin hasn't been replicated.
            # The 'name' field will be converted to 'id' in the future.
            #
            if p['identifier'] == plugin_id and p['namespace'] is None:
                return p['reference']

        raise exceptions.MissingPluginError(plugin_name, self.__engine)

    def __download_logs(self, plugin_name, token, directory):
        """
        Download plugin logs from the provided plugin and Delphix Engine using
        a token that was previously generated to the desired directory
        """

        logger.info(
            'Downloading logs for plugin {} with token {} to {}.'.format(
                plugin_name, token, directory))

        download_zip_data = self.__get(
            'delphix/data/downloadOutputStream?token={}'.format(token),
            'application/octet-stream', True)
        download_zip_name = "{}/{}".format(
            directory,
            "dlpx-plugin-logs-{}-{}.tar.gz".format(plugin_name, token))
        with open(download_zip_name, "wb") as f:
            for chunk in download_zip_data:
                f.write(chunk)

    def upload_plugin(self, name, content, wait):
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
        upload_response = self.__post('delphix/data/upload',
                                      content_type=self.__UPLOAD_CONTENT,
                                      data=self.__encode(
                                          json.dumps(content), token, name))
        if wait:
            self._wait_for_upload_to_complete(name,
                                              upload_response.get('action'),
                                              upload_response.get('job'))

    def _wait_for_upload_to_complete(self, name, upload_action, upgrade_job):
        """
        Waits a maximum of 60 minutes for the plugin upload to complete before
        returning from the cli command. If the upload response contains a job,
        this means that the plugin will be upgraded. We log additional details
        regarding events if the job exists (i.e. event code, details, and
        action), but only if we haven't seen the job event before. We will
        return when the job succeeds, fails, or times out. Can raise
        PluginUploadJobFailed or PluginUploadWaitTimedOut
        """
        ticker = threading.Event()
        start_time = time.time()
        event_tuples = set()
        failed_statuses = ('FAILED', 'SUSPENDED', 'CANCELLED')
        while not ticker.wait(self.__JOB_POLLING_INTERVAL):
            if upgrade_job:
                status_response = self.__get(
                    'delphix/action/{}/getJob'.format(upload_action)).json()
                events = status_response.get('result').get('events')
                for event in events:
                    event_tuple = (event.get('timestamp'),
                                   event.get('messageCode'))
                    if event_tuple not in event_tuples:
                        logger.info('Timestamp: {}, Code: {}'.format(
                            event.get('timestamp'), event.get('messageCode')))
                        logger.warn(event.get('messageDetails'))
                        if event.get('messageAction') is not None:
                            logger.warn(event.get('messageAction'))
                        event_tuples.add(event_tuple)
                status = status_response.get('result').get('jobState')
            else:
                status_response = self.__get(
                    'delphix/action/{}'.format(upload_action)).json()
                status = status_response.get('result').get('state')

            if status == 'COMPLETED':
                logger.warn(
                    'Plugin {} was successfully uploaded.'.format(name))
                ticker.set()
            elif status in failed_statuses:
                ticker.set()
                raise exceptions.PluginUploadJobFailed(name)
            elif (time.time() - start_time) > self.__WAIT_TIMEOUT_SECONDS:
                ticker.set()
                raise exceptions.PluginUploadWaitTimedOut(name)

    def download_plugin_logs(self, directory, plugin_config):
        """
        Download plugin logs that have been logged from the plugin scripts.
        Can raise HttpPostError and UnexpectedError.
        """

        # Get the name and id of the plugin from the plugin config.
        plugin_name = plugin_util.get_plugin_config_property(
            plugin_config, 'name')
        plugin_id = plugin_util.get_plugin_config_property(plugin_config, 'id')

        # Convert plugin id to object reference id.
        plugin_ref = self.__get_plugin_ref_from_id(plugin_name, plugin_id)

        # Get the download token.
        logger.info(
            'Getting token for download for plugin: {}.'.format(plugin_ref))
        data = {
            'type': 'SupportBundleGenerateParameters',
            'bundleType': 'PLUGIN_LOG',
            'plugin': '{}'.format(plugin_ref)
        }
        response = self.__post('delphix/service/support/bundle/generate',
                               data=data)
        token = response['result'].encode('utf-8').strip()
        logger.debug('Got token {!r} successfully.'.format(token))

        self.__download_logs(plugin_name, token, directory)

        logger.info('Plugin logs were successfully downloaded to {}.'.format(
            directory))

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
