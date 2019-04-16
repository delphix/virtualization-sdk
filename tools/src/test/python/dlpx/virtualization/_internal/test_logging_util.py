#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os
import tempfile

import mock

from dlpx.virtualization._internal import logging_util


class TestLoggingUtil:
    @staticmethod
    @mock.patch('os.path.exists')
    @mock.patch('os.makedirs')
    def test_log_dir_created(mock_makedirs, mocked_path_exists):
        logging_util.LOGGING_DIRECTORY = tempfile.gettempdir()
        mocked_path_exists.return_value = False

        logging_util.setup_logger()

        mock_makedirs.assert_called_once_with(
            os.path.expanduser(tempfile.gettempdir()))

    @staticmethod
    @mock.patch('os.path.exists')
    @mock.patch('os.makedirs')
    def test_log_dir_not_created_if_exists(mock_makedirs, mocked_path_exists):
        logging_util.LOGGING_DIRECTORY = tempfile.gettempdir()
        mocked_path_exists.return_value = True

        logging_util.setup_logger()

        assert not mock_makedirs.called, 'makedirs called when path existed'
