#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import pytest
from dlpx.virtualization._internal import delphix_client, exceptions
from dlpx.virtualization._internal.commands import download_logs


class FakeDelphixClient(object):
    """
    A fake of the DelphixClient class created inside delphix_client.py. This
    fake is used to test the upload function by raising client results when
    failure occurs without having to do actual http requests.
    """

    def __init__(self, engine):
        self.__users = {'admin': 'delphix'}
        self.engine = engine
        self.directory = ""
        self.plugin_config = ""

    @staticmethod
    def get_engine_api(content):
        if 'engineApi' in content:
            engine_api = content['engineApi']
            if (isinstance(engine_api, dict)
                    and engine_api.get('type') == 'APIVersion'
                    and isinstance(engine_api.get('major'), int)
                    and isinstance(engine_api.get('minor'), int)
                    and isinstance(engine_api.get('micro'), int)):
                return engine_api
        raise exceptions.InvalidArtifactError()

    def login(self, engine_api, user, password):
        if (engine_api.get('major') < 0 or engine_api.get('minor') < 0
                or engine_api.get('micro') < 0):
            raise exceptions.HttpError(
                200, {
                    'type':
                    'APIError',
                    'details':
                    'Invalid API version.',
                    'action':
                    'Change the API version to one supported by your'
                    ' version of the Delphix Engine. Review the Release'
                    ' Notes for your Delphix Engine version to determine'
                    ' which API version is supported.',
                    'id':
                    'exception.webservices.session.invalid.version'
                })

        found_password = self.__users.get(user)
        if password != found_password:
            raise exceptions.HttpError(
                401, {
                    'type': 'APIError',
                    'details': 'Invalid username or password.',
                    'action': 'Try with a different set of credentials.',
                    'id': 'exception.webservices.login.failed'
                })

    def download_plugin_logs(self, directory, plugin_config):
        self.directory = directory
        self.plugin_config = plugin_config


@pytest.mark.usefixtures('delphix_client_class')
class TestDownloadLogs:
    @staticmethod
    @pytest.fixture
    def fake_client():
        return FakeDelphixClient('test-engine.com')

    @staticmethod
    @pytest.fixture
    def delphix_client_class(monkeypatch, fake_client):
        """
        This fixture makes it so that whenever a function in this class would
        have called DelphixClient() it instead calls FakeDelphixClient()
        allowing us to mock the results of the client methods login and
        upload_plugin.
        """

        def create_client(_):
            return fake_client

        #
        # Return back the specific fake_client created in the fixture so we
        # can check properties set in it to verify state.
        #
        monkeypatch.setattr(delphix_client, 'DelphixClient', create_client)

    @staticmethod
    def test_download_success(plugin_config_file, src_dir, fake_client):
        user = 'admin'
        password = 'delphix'

        download_logs.download_logs(fake_client.engine, plugin_config_file,
                                    user, password, src_dir)
        assert fake_client.directory == src_dir
        assert fake_client.plugin_config == plugin_config_file
