#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json

import pytest
from dlpx.virtualization._internal import delphix_client, exceptions
from dlpx.virtualization._internal.commands import upload


class FakeDelphixClient(object):
    """
    A fake of the DelphixClient class created inside delphix_client.py. This
    fake is used to test the upload function by raising client results when
    failure occurs without having to do actual http requests.
    """
    def __init__(self, engine):
        self.__users = {'admin': 'delphix'}
        self.engine = engine
        self.uploaded_files = {}

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

    def upload_plugin(self, name, content):
        if content.get('discoveryDefinition') is None:
            raise exceptions.HttpError(
                200, {
                    'type':
                    'APIError',
                    'details':
                    'The schema "repositorySchema" in the'
                    ' "DiscoveryDefinition" cannot be updated because'
                    ' there exist objects that conform to the original'
                    ' schema.',
                    'action':
                    'Delete the following objects and try again:'
                    ' db_centos75_157_2,db_centos75_157_1,'
                    'db_centos75_157_0',
                    'id':
                    'exception.toolkit.cannot.update.schema'
                })
        self.uploaded_files[name] = content


@pytest.mark.usefixtures('delphix_client_class')
class TestUpload:
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
    def test_upload_success(artifact_file, artifact_content, fake_client):

        user = 'admin'
        password = 'delphix'

        upload.upload(fake_client.engine, user, artifact_file, password)

        # Make sure that the fake client was passed in the correct contents.
        assert (
            fake_client.uploaded_files['artifact.json'] == artifact_content)

    @staticmethod
    @pytest.mark.parametrize('artifact_file',
                             ['/not/a/real/file/upload_artifact.json'])
    def test_upload_no_file(fake_client, artifact_file):

        user = 'admin'
        password = 'delphix'

        with pytest.raises(exceptions.UserError) as err_info:
            upload.upload(fake_client.engine, user, artifact_file, password)

        message = err_info.value.message
        assert message == ("Unable to read upload artifact file"
                           " '/not/a/real/file/upload_artifact.json'"
                           "\nError code: 2. Error message: ENOENT")

        # Make sure the file was not uploaded to the client.
        assert ('upload_artifact.json' not in fake_client.uploaded_files)

    @staticmethod
    @pytest.mark.parametrize(
        'artifact_content',
        ['{}\nNOT JSON'.format(json.dumps({'random': 'json'}))])
    def test_upload_file_not_json(artifact_file, fake_client):

        user = 'admin'
        password = 'delphix'

        with pytest.raises(exceptions.UserError) as err_info:
            upload.upload(fake_client.engine, user, artifact_file, password)

        message = err_info.value.message
        assert message == (
            'Upload failed because the upload artifact was not a'
            ' valid json file. Verify the file was built using'
            ' the delphix build command.')

        # Make sure the file was not uploaded to the client.
        assert ('upload_artifact.json' not in fake_client.uploaded_files)

    @staticmethod
    @pytest.mark.parametrize('engine_api', [{
        'type': 'APIVersion',
        'major': -1,
        'minor': 11,
        'micro': 0
    }])
    def test_upload_api_incorrect(artifact_file, fake_client):

        user = 'admin'
        password = 'delphix'

        with pytest.raises(exceptions.HttpError) as err_info:
            upload.upload(fake_client.engine, user, artifact_file, password)

        error = err_info.value.error
        message = err_info.value.message
        assert err_info.value.status_code == 200
        assert error['details'] == 'Invalid API version.'
        assert error['action'] == ('Change the API version to one supported'
                                   ' by your version of the Delphix Engine.'
                                   ' Review the Release Notes for your'
                                   ' Delphix Engine version to determine which'
                                   ' API version is supported.')

        assert message == ('API request failed with HTTP Status 200'
                           '\nDetails: Invalid API version.'
                           '\nAction: Change the API version to one supported'
                           ' by your version of the Delphix Engine.'
                           ' Review the Release Notes for your'
                           ' Delphix Engine version to determine which'
                           ' API version is supported.')

        # Make sure the file was not uploaded to the client.
        assert ('upload_artifact.json' not in fake_client.uploaded_files)

    @staticmethod
    def test_upload_password_incorrect(artifact_file, artifact_content,
                                       fake_client):

        user = 'admin'
        password = 'delphix2'

        with pytest.raises(exceptions.HttpError) as err_info:
            upload.upload(fake_client.engine, user, artifact_file, password)

        error = err_info.value.error
        message = err_info.value.message
        assert err_info.value.status_code == 401
        assert error['details'] == 'Invalid username or password.'
        assert error['action'] == 'Try with a different set of credentials.'

        assert message == (
            'API request failed with HTTP Status 401'
            '\nDetails: Invalid username or password.'
            '\nAction: Try with a different set of credentials.')

        # Make sure the file was not uploaded to the client.
        assert ('upload_artifact.json' not in fake_client.uploaded_files)

    @staticmethod
    @pytest.mark.parametrize('discovery_definition', [None])
    def test_upload_plugin_failed(artifact_file, artifact_content,
                                  fake_client):

        user = 'admin'
        password = 'delphix'

        with pytest.raises(exceptions.HttpError) as err_info:
            upload.upload(fake_client.engine, user, artifact_file, password)

        error = err_info.value.error
        message = err_info.value.message
        assert err_info.value.status_code == 200
        assert error['details'] == ('The schema "repositorySchema" in the'
                                    ' "DiscoveryDefinition" cannot be updated'
                                    ' because there exist objects that conform'
                                    ' to the original schema.')
        assert error['action'] == ('Delete the following objects and try'
                                   ' again: db_centos75_157_2,'
                                   'db_centos75_157_1,db_centos75_157_0')

        assert message == ('API request failed with HTTP Status 200'
                           '\nDetails: The schema "repositorySchema" in the'
                           ' "DiscoveryDefinition" cannot be updated because'
                           ' there exist objects that conform to the original'
                           ' schema.'
                           '\nAction: Delete the following objects and try'
                           ' again: db_centos75_157_2,db_centos75_157_1,'
                           'db_centos75_157_0')

        # Make sure the file was not uploaded to the client.
        assert ('upload_artifact.json' not in fake_client.uploaded_files)
