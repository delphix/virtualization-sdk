#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json

import httpretty
import pytest
import requests

from dlpx.virtualization._internal import exceptions
from dlpx.virtualization._internal.commands import upload


class FakeDelphixClient:
    """
    A fake of the DelphixClient class created inside upload.py. This fake is
    used to test the upload function by raising client results when failure
    occurs without having to do actual http requests.
    """

    def __init__(self, engine):
        self.__users = {'admin': 'delphix'}
        self.engine = engine
        self.uploaded_files = {}

    def login(self, engine_api, user, password):
        if (engine_api.get('major') < 0 or engine_api.get('minor') < 0
                or engine_api.get('micro') < 0):
            raise exceptions.HttpPostError(
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
            raise exceptions.HttpPostError(
                401, {
                    'type': 'APIError',
                    'details': 'Invalid username or password.',
                    'action': 'Try with a different set of credentials.',
                    'id': 'exception.webservices.login.failed'
                })

    def upload_plugin(self, name, content):
        if content.get('discoveryDefinition') is None:
            raise exceptions.HttpPostError(
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
        monkeypatch.setattr(upload, 'DelphixClient', create_client)

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

        with pytest.raises(exceptions.HttpPostError) as err_info:
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

        assert message == ('Plugin upload failed with HTTP Status 200'
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

        with pytest.raises(exceptions.HttpPostError) as err_info:
            upload.upload(fake_client.engine, user, artifact_file, password)

        error = err_info.value.error
        message = err_info.value.message
        assert err_info.value.status_code == 401
        assert error['details'] == 'Invalid username or password.'
        assert error['action'] == 'Try with a different set of credentials.'

        assert message == (
            'Plugin upload failed with HTTP Status 401'
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

        with pytest.raises(exceptions.HttpPostError) as err_info:
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

        assert message == ('Plugin upload failed with HTTP Status 200'
                           '\nDetails: The schema "repositorySchema" in the'
                           ' "DiscoveryDefinition" cannot be updated because'
                           ' there exist objects that conform to the original'
                           ' schema.'
                           '\nAction: Delete the following objects and try'
                           ' again: db_centos75_157_2,db_centos75_157_1,'
                           'db_centos75_157_0')

        # Make sure the file was not uploaded to the client.
        assert ('upload_artifact.json' not in fake_client.uploaded_files)


class TestEngineApi:
    @staticmethod
    def test_get(engine_api, artifact_content):
        assert upload.get_engine_api(artifact_content) == engine_api

    @staticmethod
    @pytest.mark.parametrize('engine_api', [
        None, 'not a dict',
        {
            'type': 'APIVersion',
            'major': 'not an int',
            'minor': 11,
            'micro': 0
        }
    ])
    def test_validate_fail(artifact_content):
        with pytest.raises(exceptions.InvalidArtifactError) as err_info:
            upload.get_engine_api(artifact_content)

        message = err_info.value.message
        assert message == (
            'The engineApi field is either missing or malformed.'
            ' The field must be of the form:'
            '\n{'
            '\n  "type": "APIVersion",'
            ' \n  "major": 1,'
            ' \n  "minor": 7,'
            ' \n  "micro": 0'
            '\n}'
            '\nVerify that the artifact passed in was generated'
            ' by the build function.')


@pytest.mark.usefixtures('httpretty_enabled')
class TestDelphixClient:
    @staticmethod
    @pytest.fixture
    def httpretty_enabled():
        httpretty.HTTPretty.allow_net_connect = False
        httpretty.enable()
        yield
        httpretty.disable()

    SES_RESP_SUCCESS = ((
        '{"type":"OKResult","status":"OK","result":{'
        '"type":"APISession","version":{'
        '"type":"APIVersion","major":1,"minor":11,"micro":0},'
        '"locale":null,"client":null},"job":null,"action":null}'), {
            'Set-Cookie':
            'JSESSIONID=8F075FBEC53E8413BC2D5EEF29EAA721;'
            ' Path=/resources; HttpOnly',
            'X-Frame-Options':
            'SAMEORIGIN',
            'X-Content-Type-Options':
            'nosniff',
            'X-XSS-Protection':
            '1; mode=block',
            'Cache-Control':
            'max-age=0',
            'Expires':
            'Mon, 04 Feb 2019 06:00:12 GMT',
            'Content-Type':
            'application/json',
            'Content-Length':
            '180',
            'Date':
            'Mon, 04 Feb 2019 06:00:12 GMT'
        })
    SES_RESP_FAIL = ((
        '{"type":"ErrorResult","status":"ERROR","error":{'
        '"type":"APIError","details":"Invalid API version \\"2.11.0\\".",'
        '"action":"Change the API version to one supported by your'
        ' version of the Delphix Engine. Review the Release Notes for'
        ' your Delphix Engine version to determine which API version is'
        ' supported.",'
        '"id":"exception.webservices.session.invalid.version",'
        '"commandOutput":null,"diagnoses":[]}}'), {
            'Set-Cookie':
            'JSESSIONID=E6A9006C615CACC0A3DC1BC65379B207;'
            ' Path=/resources; HttpOnly',
            'X-Frame-Options':
            'SAMEORIGIN',
            'X-Content-Type-Options':
            'nosniff',
            'X-XSS-Protection':
            '1; mode=block',
            'Cache-Control':
            'max-age=0',
            'Expires':
            'Mon, 04 Feb 2019 05:41:49 GMT',
            'Content-Type':
            'application/json',
            'Content-Length':
            '392',
            'Date':
            'Mon, 04 Feb 2019 05:41:49 GMT'
        })
    SES_RESP_UNKNOWN_FAIL = ('{"blob":"Unknown","status":"UNKNOWN"}', {
        'Set-Cookie':
        'JSESSIONID=E6A9006C615CACC0A3DC1BC65379B207;'
        ' Path=/resources; HttpOnly',
        'X-Frame-Options':
        'SAMEORIGIN',
        'X-Content-Type-Options':
        'nosniff',
        'X-XSS-Protection':
        '1; mode=block',
        'Cache-Control':
        'max-age=0',
        'Expires':
        'Mon, 04 Feb 2019 05:41:49 GMT',
        'Content-Type':
        'application/json',
        'Content-Length':
        '37',
        'Date':
        'Mon, 04 Feb 2019 05:41:49 GMT'
    })
    LOGIN_RESP_SUCCESS = ((
        '{"type":"OKResult","status":"OK","result":"USER-2",'
        '"job":null,"action":null}'), {
            'X-Frame-Options':
            'SAMEORIGIN',
            'X-Content-Type-Options':
            'nosniff',
            'X-XSS-Protection':
            '1; mode=block',
            'Set-Cookie':
            'JSESSIONID=A96E274A157195647944973CFEA37FBF;'
            ' Path=/resources; HttpOnly',
            'Cache-Control':
            'max-age=0',
            'Expires':
            'Mon, 04 Feb 2019 07:10:16 GMT',
            'Content-Type':
            'application/json',
            'Content-Length':
            '76',
            'Date':
            'Mon, 04 Feb 2019 07:10:16 GMT'
        })
    LOGIN_RESP_FAIL = ((
        '{"type":"ErrorResult","status":"ERROR","error":{'
        '"type":"APIError","details":"Invalid username or password.",'
        '"action":"Try with a different set of credentials.",'
        '"id":"exception.webservices.login.failed",'
        '"commandOutput":null,"diagnoses":[]}}'), {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Cache-Control': 'max-age=0',
            'Expires': 'Tue, 04 Feb 2019 07:38:09 GMT',
            'Content-Type': 'application/json',
            'Content-Length': '239',
            'Date': 'Tue, 04 Feb 2019 07:38:09 GMT'
        })
    LOGIN_RESP_NO_DETAIL_FAIL = ((
        '{"type":"ErrorResult","status":"ERROR","error":{'
        '"type":"APIError","error":"Not a real error: Invalid username'
        ' or password. Try with a different set of credentials.",'
        '"id":"exception.webservices.login.failed",'
        '"commandOutput":null,"diagnoses":[]}}'), {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Cache-Control': 'max-age=0',
            'Expires': 'Tue, 04 Feb 2019 07:38:09 GMT',
            'Content-Type': 'application/json',
            'Content-Length': '244',
            'Date': 'Tue, 04 Feb 2019 07:38:09 GMT'
        })
    TOKEN_RESP_SUCCESS = (('{"type":"OKResult","status":"OK","result":{'
                           '"type":"FileUploadResult",'
                           '"url":"/resources/json/delphix/data/upload",'
                           '"token":"5cb1eeb2-46da-4feb-a6a5-edf37851a415"},'
                           '"job":null,"action":"ACTION-1"}'), {
                               'X-Frame-Options': 'SAMEORIGIN',
                               'X-Content-Type-Options': 'nosniff',
                               'X-XSS-Protection': '1; mode=block',
                               'Cache-Control': 'max-age=0',
                               'Expires': 'Mon, 04 Feb 2019 08:01:08 GMT',
                               'Content-Type': 'application/json',
                               'Content-Length': '192',
                               'Date': 'Mon, 04 Feb 2019 08:01:08 GMT'
                           })
    TOKEN_RESP_FAIL = ((
        '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"'
        ' "http://www.w3.org/TR/html4/strict.dtd"><html>'
        '<head><title>Error 403</title></head><body><h1>'
        'Error processing request</h1><p>HTTP status: 403</p>'
        '<p>Message: Use &#47;resources&#47;json&#47;delphix&#47;'
        'login to log in first</p><p>Request was POST'
        ' /resources/json/delphix/toolkit/requestUploadToken'
        '</p></body></html>'), {
            'Set-Cookie':
            'JSESSIONID=C007AE1F52A410365DA1F4A9FABC5871;'
            ' Path=/resources; HttpOnly',
            'X-Frame-Options':
            'SAMEORIGIN',
            'X-Content-Type-Options':
            'nosniff',
            'X-XSS-Protection':
            '1; mode=block',
            'Content-Type':
            'text/html;charset=utf-8',
            'Content-Language':
            'en',
            'Content-Length':
            '364',
            'Date':
            'Mon, 04 Feb 2019 08:06:49 GMT'
        })
    UPLOAD_RESP_SUCCESS = (('{"type":"OKResult","status":"OK",'
                            '"result":"","job":null,"action":"ACTION-2"}'), {
                                'X-Frame-Options': 'SAMEORIGIN',
                                'X-Content-Type-Options': 'nosniff',
                                'X-XSS-Protection': '1; mode=block',
                                'Content-Type': 'text/plain',
                                'Content-Length': '76',
                                'Date': 'Mon, 04 Feb 2019 08:08:33 GMT'
                            })
    UPLOAD_RESP_FAIL = ((
        '{"type":"ErrorResult","status":"ERROR","error":{'
        '"type":"APIError",'
        '"details":"The schema \\"repositorySchema\\" in the '
        '\\"DiscoveryDefinition\\"'
        ' cannot be updated because there exist objects that conform to'
        ' the original schema.",'
        '"action":"Delete the following objects and try again:'
        ' db_centos75_157_2,db_centos75_157_1,db_centos75_157_0",'
        '"id":"exception.toolkit.cannot.update.schema",'
        '"commandOutput":null,"diagnoses":[]}}'), {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Cache-Control': 'max-age=0',
            'Expires': 'Mon, 04 Feb 2019 23:12:00 GMT',
            'Content-Type': 'application/json',
            'Content-Length': '416',
            'Date': 'Mon, 04 Feb 2019 08:09:44 GMT'
        })

    @staticmethod
    def test_delphix_client_success(engine_api, artifact_content):
        session_body, session_header = TestDelphixClient.SES_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/session',
            body=session_body,
            forcing_headers=session_header)

        login_body, login_header = TestDelphixClient.LOGIN_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/login',
            body=login_body,
            forcing_headers=login_header)

        token_body, token_header = TestDelphixClient.TOKEN_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST, 'http://test-engine.com/resources/'
            'json/delphix/toolkit/requestUploadToken',
            body=token_body,
            forcing_headers=token_header)

        upload_body, upload_header = TestDelphixClient.UPLOAD_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/data/upload',
            body=upload_body,
            forcing_headers=upload_header)

        dc = upload.DelphixClient('test-engine.com')
        dc.login(engine_api, 'admin', 'delphix')
        dc.upload_plugin('plugin name', artifact_content)

        history = httpretty.HTTPretty.latest_requests
        assert history[-1].path == u'/resources/json/delphix/data/upload'
        assert (history[-2].path ==
                u'/resources/json/delphix/toolkit/requestUploadToken')
        assert history[-3].path == u'/resources/json/delphix/login'
        assert history[-4].path == u'/resources/json/delphix/session'

    @staticmethod
    def test_request_timeout(engine_api):
        def exception_callback(request, uri, headers):
            # raise requests.Timeout to test request exceptions.
            raise requests.Timeout('Connection timed out.')

        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/session',
            body=exception_callback)

        dc = upload.DelphixClient('test-engine.com')

        with pytest.raises(exceptions.UserError) as err_info:
            dc.login(engine_api, 'admin', 'delphix')

        message = err_info.value.message
        assert message == ('Upload failed due to a http request failure.'
                           '\n(\'Connection aborted.\','
                           ' BadStatusLine("\'\'",))')

        history = httpretty.HTTPretty.latest_requests
        assert history[-1].path == u'/resources/json/delphix/session'

    @staticmethod
    @pytest.mark.parametrize('engine_api', [{
        'type': 'APIVersion',
        'major': 2,
        'minor': 11,
        'micro': 0
    }])
    def test_delphix_client_wrong_api(engine_api):
        session_body, session_header = TestDelphixClient.SES_RESP_FAIL
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/session',
            body=session_body,
            forcing_headers=session_header)

        dc = upload.DelphixClient('test-engine.com')

        with pytest.raises(exceptions.HttpPostError) as err_info:
            dc.login(engine_api, 'admin', 'delphix')

        error = err_info.value.error
        message = err_info.value.message
        assert err_info.value.status_code == 200
        assert error['details'] == 'Invalid API version "2.11.0".'
        assert error['action'] == ('Change the API version to one supported'
                                   ' by your version of the Delphix Engine.'
                                   ' Review the Release Notes for your'
                                   ' Delphix Engine version to determine which'
                                   ' API version is supported.')

        assert message == ('Plugin upload failed with HTTP Status 200'
                           '\nDetails: Invalid API version "2.11.0".'
                           '\nAction: Change the API version to one supported'
                           ' by your version of the Delphix Engine.'
                           ' Review the Release Notes for your'
                           ' Delphix Engine version to determine which'
                           ' API version is supported.')

        history = httpretty.HTTPretty.latest_requests
        assert history[-1].path == u'/resources/json/delphix/session'

    @staticmethod
    def test_delphix_client_unknown_error(engine_api):
        session_body, session_header = TestDelphixClient.SES_RESP_UNKNOWN_FAIL
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/session',
            body=session_body,
            forcing_headers=session_header,
            status=404)

        dc = upload.DelphixClient('test-engine.com')

        with pytest.raises(exceptions.UnexpectedError) as err_info:
            dc.login(engine_api, 'admin', 'delphix')

        assert err_info.value.status_code == 404
        assert err_info.value.response == (
            '{\n  "status": "UNKNOWN", \n  "blob": "Unknown"\n}')
        assert err_info.value.message == (
            'Received an unexpected error with HTTP Status 404,\nDumping full'
            ' response:\n{\n  "status": "UNKNOWN", \n  "blob": "Unknown"\n}')

        history = httpretty.HTTPretty.latest_requests
        assert history[-1].path == u'/resources/json/delphix/session'

    @staticmethod
    def test_delphix_client_wrong_login(engine_api):
        session_body, session_header = TestDelphixClient.SES_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/session',
            body=session_body,
            forcing_headers=session_header)

        login_body, login_header = TestDelphixClient.LOGIN_RESP_FAIL
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/login',
            body=login_body,
            forcing_headers=login_header,
            status=401)

        dc = upload.DelphixClient('test-engine.com')

        with pytest.raises(exceptions.HttpPostError) as err_info:
            dc.login(engine_api, 'admin2', 'delphix')

        error = err_info.value.error
        message = err_info.value.message
        assert err_info.value.status_code == 401
        assert error['details'] == 'Invalid username or password.'
        assert error['action'] == 'Try with a different set of credentials.'
        assert message == (
            'Plugin upload failed with HTTP Status 401'
            '\nDetails: Invalid username or password.'
            '\nAction: Try with a different set of credentials.')

        history = httpretty.HTTPretty.latest_requests
        assert history[-1].path == u'/resources/json/delphix/login'
        assert history[-2].path == u'/resources/json/delphix/session'

    @staticmethod
    def test_delphix_client_wrong_login_no_detail(engine_api):
        session_body, session_header = TestDelphixClient.SES_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/session',
            body=session_body,
            forcing_headers=session_header)

        login_body, login_header = TestDelphixClient.LOGIN_RESP_NO_DETAIL_FAIL
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/login',
            body=login_body,
            forcing_headers=login_header,
            status=401)

        dc = upload.DelphixClient('test-engine.com')

        with pytest.raises(exceptions.HttpPostError) as err_info:
            dc.login(engine_api, 'admin2', 'delphix')

        message = err_info.value.message
        assert err_info.value.status_code == 401
        assert message == ('Plugin upload failed with HTTP Status 401'
                           '\nUnable to parse details of error.'
                           ' Dumping full response: {'
                           '\n  "commandOutput": null, '
                           '\n  "diagnoses": [], '
                           '\n  "type": "APIError", '
                           '\n  "id": "exception.webservices.login.failed", '
                           '\n  "error": "Not a real error: Invalid username'
                           ' or password. Try with a different set of'
                           ' credentials."'
                           '\n}')

        history = httpretty.HTTPretty.latest_requests
        assert history[-1].path == u'/resources/json/delphix/login'
        assert history[-2].path == u'/resources/json/delphix/session'

    @staticmethod
    def test_delphix_client_get_token_fail(engine_api, artifact_content):
        session_body, session_header = TestDelphixClient.SES_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/session',
            body=session_body,
            forcing_headers=session_header)

        login_body, login_header = TestDelphixClient.LOGIN_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/login',
            body=login_body,
            forcing_headers=login_header)

        token_body, token_header = TestDelphixClient.TOKEN_RESP_FAIL
        httpretty.register_uri(
            httpretty.POST, 'http://test-engine.com/resources/'
            'json/delphix/toolkit/requestUploadToken',
            body=token_body,
            forcing_headers=token_header,
            status=403)

        dc = upload.DelphixClient('test-engine.com')
        dc.login(engine_api, 'admin', 'delphix')

        with pytest.raises(exceptions.UnexpectedError) as err_info:
            dc.upload_plugin('plugin name', artifact_content)

        assert err_info.value.status_code == 403
        assert err_info.value.response == token_body
        assert err_info.value.message == (
            'Received an unexpected error with HTTP Status 403,\nDumping full'
            ' response:\n{}'.format(token_body))

        history = httpretty.HTTPretty.latest_requests
        assert (history[-1].path ==
                u'/resources/json/delphix/toolkit/requestUploadToken')
        assert history[-2].path == u'/resources/json/delphix/login'
        assert history[-3].path == u'/resources/json/delphix/session'

    @staticmethod
    def test_delphix_client_upload_fail(engine_api, artifact_content):
        session_body, session_header = TestDelphixClient.SES_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/session',
            body=session_body,
            forcing_headers=session_header)

        login_body, login_header = TestDelphixClient.LOGIN_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/login',
            body=login_body,
            forcing_headers=login_header)

        token_body, token_header = TestDelphixClient.TOKEN_RESP_SUCCESS
        httpretty.register_uri(
            httpretty.POST, 'http://test-engine.com/resources/'
            'json/delphix/toolkit/requestUploadToken',
            body=token_body,
            forcing_headers=token_header)

        upload_body, upload_header = TestDelphixClient.UPLOAD_RESP_FAIL
        httpretty.register_uri(
            httpretty.POST,
            'http://test-engine.com/resources/json/delphix/data/upload',
            body=upload_body,
            forcing_headers=upload_header)

        dc = upload.DelphixClient('test-engine.com')
        dc.login(engine_api, 'admin', 'delphix')

        with pytest.raises(exceptions.HttpPostError) as err_info:
            dc.upload_plugin('plugin name', artifact_content)
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

        assert message == ('Plugin upload failed with HTTP Status 200'
                           '\nDetails: The schema "repositorySchema" in the'
                           ' "DiscoveryDefinition" cannot be updated because'
                           ' there exist objects that conform to the original'
                           ' schema.'
                           '\nAction: Delete the following objects and try'
                           ' again: db_centos75_157_2,db_centos75_157_1,'
                           'db_centos75_157_0')

        history = httpretty.HTTPretty.latest_requests
        assert history[-1].path == u'/resources/json/delphix/data/upload'
        assert (history[-2].path ==
                u'/resources/json/delphix/toolkit/requestUploadToken')
        assert history[-3].path == u'/resources/json/delphix/login'
        assert history[-4].path == u'/resources/json/delphix/session'
