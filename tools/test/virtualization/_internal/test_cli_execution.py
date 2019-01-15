#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os


class TestCliExecution:
    @staticmethod
    def test_main():
        return_value = os.system('python -m virtualization._internal --help')
        assert return_value == 0

    @staticmethod
    def test_entry_point():
        return_value = os.system('delphix --help')
        assert return_value == 0
