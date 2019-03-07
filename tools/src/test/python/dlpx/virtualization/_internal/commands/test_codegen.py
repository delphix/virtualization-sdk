#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os
import subprocess

import pytest

from dlpx.virtualization._internal import codegen
from dlpx.virtualization._internal.commands import compile


class TestCodegen:
    TEST_GEN_FILE = 'test_gen_file.py'

    @staticmethod
    @pytest.fixture
    def popen_helper(monkeypatch, plugin_config_file, codegen_gen_py_inputs):
        class FakePopen:
            def __init__(self, return_code, stdout, stderr):
                self.return_code = return_code
                self.stdout = stdout
                self.stderr = stderr

            def wait(self):
                return self.return_code

            def communicate(self):
                return self.stdout, self.stderr

        class PopenHelper:
            """
            A popen helper that keeps track of the popen calls and defines what
            the call should return.
            """

            def __init__(self):
                self.fake_popen_output = None
                self.swagger_file = None
                self.final_dirname = None
                self.output_dir = None
                self.stdout_input = None
                self.stderr_input = None

            def set_popen_output(self, return_code, stdout=None, stderr=None):
                if not self.fake_popen_output:
                    self.fake_popen_output = FakePopen(return_code, stdout,
                                                       stderr)
                else:
                    assert False, 'Popen output should be set only once.'

            def set_popen_input(self, args, stdout=None, stderr=None):
                if not self.fake_popen_output:
                    assert False, 'Popen output object was not set'

                (_, _, _, _, _, self.swagger_file, _, self.final_dirname, _, _,
                 _, _, self.output_dir) = args

                self.stdout_input = stdout
                self.stderr_input = stderr

                # The files expected from the jar run are created here.
                PopenHelper.create_codegen_jar_files()

                return self.fake_popen_output

            @staticmethod
            def create_codegen_jar_files():
                gen_py = codegen_gen_py_inputs
                #
                # To create a fake of this run, create a dir at the output dir
                # with
                # the swagger_server name. Inside it created another folder
                # 'generated'
                #
                swagger_server_path = os.path.join(
                    gen_py.plugin_content_dir, codegen.OUTPUT_DIR_NAME,
                    codegen.SWAGGER_SERVER_MODULE)
                os.mkdir(swagger_server_path)
                util_file = os.path.join(swagger_server_path, 'util.py')
                with open(util_file, 'w') as f:
                    f.write('# This is the util.py class.')
                # Need to create a util.py
                generated_path = os.path.join(swagger_server_path,
                                              compile.GENERATED_MODULE)
                os.mkdir(generated_path)

                test_gen_file = os.path.join(generated_path,
                                             TestCodegen.TEST_GEN_FILE)
                with open(test_gen_file, 'w') as f:
                    f.write('from {0}.{1}.base_model_ import Model'
                            '\nfrom {0} import util'.format(
                                codegen.SWAGGER_SERVER_MODULE,
                                compile.GENERATED_MODULE))

        helper = PopenHelper()
        monkeypatch.setattr(subprocess, 'Popen', helper.set_popen_input)

        return helper

    @staticmethod
    def test_codegen_success(codegen_gen_py_inputs, popen_helper):
        gen_py = codegen_gen_py_inputs
        stderr_ret = (
            '[main] INFO io.swagger.parser.Swagger20Parser - reading from'
            ' swagger.json'
            '[main] INFO io.swagger.codegen.AbstractGenerator - writing file'
            ' .delphix-compile/swagger_server/generated/test_gen_file.py')
        popen_helper.set_popen_output(0, stderr=stderr_ret)

        codegen.generate_python(gen_py.name, gen_py.source_dir,
                                gen_py.plugin_content_dir, gen_py.schema_dict,
                                compile.GENERATED_MODULE)

        assert popen_helper.stdout_input == subprocess.PIPE
        assert popen_helper.stderr_input == subprocess.PIPE
        assert os.path.exists(popen_helper.swagger_file)
        assert popen_helper.final_dirname == compile.GENERATED_MODULE
        expected_output_dir = os.path.join(gen_py.plugin_content_dir,
                                           codegen.OUTPUT_DIR_NAME)
        assert popen_helper.output_dir == expected_output_dir

        # Validate that the "generated" file were copied.
        util_file = os.path.join(gen_py.source_dir, compile.GENERATED_MODULE,
                                 'util.py')

        gen_file = os.path.join(gen_py.source_dir, compile.GENERATED_MODULE,
                                TestCodegen.TEST_GEN_FILE)

        assert os.path.exists(util_file)
        assert os.path.exists(gen_file)

        # Also validate that the expected content was changed as expected.
        expected_content = (
            'from {0}.base_model_ import Model\nfrom {0} import util'.format(
                compile.GENERATED_MODULE))

        with open(gen_file, 'rb') as f:
            content = f.read()

        assert content == expected_content
