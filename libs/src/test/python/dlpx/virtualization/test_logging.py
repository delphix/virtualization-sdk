#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import mock
import pytest

from dlpx.virtualization.libs import PlatformHandler
from dlpx.virtualization.libs_pb2 import LogRequest
from dlpx.virtualization.libs_pb2 import LogResult
from dlpx.virtualization.libs_pb2 import LogResponse


class TestPythonHandler:

    @staticmethod
    @pytest.fixture()
    def successful_response():
        result = LogResult()
        response = LogResponse()
        response.return_value.CopyFrom(result)
        return response

    @staticmethod
    @pytest.mark.parametrize("py_level,expected_level", [
        (logging.DEBUG, LogRequest.DEBUG),
        (logging.INFO, LogRequest.INFO),
        (logging.WARNING, LogRequest.ERROR),
        (logging.ERROR, LogRequest.ERROR),
        (logging.CRITICAL, LogRequest.ERROR)
    ])

    @mock.patch("dlpx.virtualization._engine.libs", create=True)
    def test_levels(mock_internal_libs, py_level, expected_level, successful_response):
        mock_internal_libs.log.return_value = successful_response

        logger = logging.getLogger()
        logger.setLevel(py_level)
        logger.addHandler(PlatformHandler())

        logger.log(py_level, 'Some message: %s', 'parameter')

        log_request = LogRequest()
        log_request.message = 'Some message: parameter'
        log_request.level = expected_level

        mock_internal_libs.log.assert_called_with(log_request)

    @staticmethod
    @mock.patch("dlpx.virtualization._engine.libs", create=True)
    def test_format(mock_internal_libs, successful_response):
        mock_internal_libs.log.return_value = successful_response

        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler = PlatformHandler()
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)
        logger.addHandler(handler)

        logger.error('Some message: %s', 'parameter')

        log_request = LogRequest()
        log_request.message = '[ERROR] Some message: parameter'
        log_request.level = LogRequest.ERROR

        mock_internal_libs.log.assert_called_with(log_request)


    @staticmethod
    @mock.patch("dlpx.virtualization._engine.libs", create=True)
    def test_log_non_string(mock_internal_libs, successful_response):

        mock_internal_libs.log.return_value = successful_response

        handler = PlatformHandler()
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)
        logger.addHandler(handler)

        logger.error(10)

        log_request = LogRequest()
        log_request.message = '10'
        log_request.level = LogRequest.ERROR

        mock_internal_libs.log.assert_called_with(log_request)
