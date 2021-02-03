#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#

import errno
import json
import os
import subprocess

import pytest
from dlpx.virtualization._internal import codegen, const, exceptions, file_util


class TestCodegen:
    TEST_GEN_FILE = 'test_gen_file.py'

    @staticmethod
    @pytest.fixture
    def popen_helper(monkeypatch, plugin_config_file):
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
                self.jar = None
                self.swagger_file = None
                self.package_name = None
                self.module_name = None
                self.output_dir = None
                self.stdout_input = None
                self.stderr_input = None
                self.fake_popen_err = None

            def set_popen_output(self, return_code, stdout=None, stderr=None):
                if not self.fake_popen_output:
                    self.fake_popen_output = FakePopen(return_code, stdout,
                                                       stderr)
                else:
                    assert False, 'Popen output should be set only once.'

            def set_popen_err(self, err):
                self.fake_popen_err = err

            def set_popen_input(self, args, stdout=None, stderr=None):
                if not (self.fake_popen_err or self.fake_popen_output):
                    assert False, 'Fake Popen output or err must be set.'

                (_, _, self.jar, _, _, _, self.swagger_file, _, _, _,
                 codegen_config_file, _, _, _, self.module_name, _,
                 self.output_dir) = args

                with open(codegen_config_file, 'r') as f:
                    self.package_name = json.load(f)['packageName']

                self.stdout_input = stdout
                self.stderr_input = stderr

                if self.fake_popen_err:
                    raise self.fake_popen_err

                #
                # The files expected from the jar run are created if process
                # has a success exit code.
                #
                if not self.fake_popen_output.return_code:
                    self.create_codegen_jar_files(self.output_dir,
                                                  self.package_name,
                                                  self.module_name)
                return self.fake_popen_output

            @staticmethod
            def create_codegen_jar_files(output_dir, package_name,
                                         module_name):
                #
                # To create a fake of this run, create a dir at the output dir
                # with the final_package name. Inside it created another folder
                # with the final module name.
                #
                package_path = os.path.join(output_dir, package_name)
                os.mkdir(package_path)
                #
                # Need to create a util.py and __init__.py because this the
                # two files expected in the package.
                #
                util_file = os.path.join(package_path, 'util.py')
                with open(util_file, 'w') as f:
                    f.write('# This is the util.py module.')

                init_file = os.path.join(package_path, '__init__.py')
                with open(init_file, 'w') as f:
                    f.write('# This is the __init__.py module.')

                module_path = os.path.join(package_path, module_name)
                os.mkdir(module_path)

                test_gen_file = os.path.join(module_path,
                                             TestCodegen.TEST_GEN_FILE)
                with open(test_gen_file, 'w') as f:
                    f.write('from {0}.{1}.base_model_ import Model'
                            '\nfrom {0} import util'.format(
                                package_name, module_name))

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
            ' .dvp-gen-output/swagger_server/generated/test_gen_file.py')
        popen_helper.set_popen_output(0, stderr=stderr_ret)

        codegen.generate_python(gen_py.name, gen_py.source_dir,
                                gen_py.plugin_content_dir, gen_py.schema_dict)

        assert popen_helper.stdout_input == subprocess.PIPE
        assert popen_helper.stderr_input == subprocess.PIPE
        assert os.path.exists(popen_helper.swagger_file)
        assert popen_helper.package_name == codegen.CODEGEN_PACKAGE
        assert popen_helper.module_name == codegen.CODEGEN_MODULE
        expected_output_dir = os.path.join(gen_py.plugin_content_dir,
                                           const.OUTPUT_DIR_NAME)
        assert popen_helper.output_dir == expected_output_dir

        # Validate that the "generated" file were copied.
        util_file = os.path.join(gen_py.source_dir, codegen.CODEGEN_PACKAGE,
                                 'util.py')
        init_file = os.path.join(gen_py.source_dir, codegen.CODEGEN_PACKAGE,
                                 '__init__.py')

        gen_file = os.path.join(gen_py.source_dir, codegen.CODEGEN_PACKAGE,
                                codegen.CODEGEN_MODULE,
                                TestCodegen.TEST_GEN_FILE)

        assert os.path.exists(util_file)
        assert os.path.exists(init_file)
        assert os.path.exists(gen_file)

    @staticmethod
    def test_get_build_dir_success(tmpdir):
        testdir = os.path.join(tmpdir.strpath, const.OUTPUT_DIR_NAME)
        file_util.make_dir(testdir, True)
        assert os.path.exists(testdir)
        assert os.path.isdir(testdir)

    @staticmethod
    def test_get_build_dir_fail():
        testdir = '/dir/that/does/not/exist/test_dir'
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.make_dir(testdir, True)

        message = err_info.value.message
        assert message == ("Unable to create new directory"
                           " '/dir/that/does/not/exist/test_dir'"
                           "\nError code: 2."
                           " Error message: No such file or directory")

    @staticmethod
    def test_write_swagger_file(tmpdir, schema_content):
        name = 'test'
        expected_file = tmpdir.join(codegen.SWAGGER_FILE_NAME).strpath
        codegen._write_swagger_file(name, schema_content, tmpdir.strpath)
        assert os.path.exists(expected_file)
        assert os.path.isfile(expected_file)

        with open(expected_file, 'rb') as f:
            content = json.load(f)

        assert content['definitions'] == schema_content
        assert content['info']['title'] == name

    @staticmethod
    def test_write_swagger_file_with_delphix_refs(
            tmpdir, schema_content, linked_source_definition_with_refs,
            linked_source_definition_with_opaque_refs):
        name = 'test'
        expected_file = tmpdir.join(codegen.SWAGGER_FILE_NAME).strpath
        schema_content['linkedSourceDefinition'] = linked_source_definition_with_refs
        codegen._write_swagger_file(name, schema_content, tmpdir.strpath)
        assert os.path.exists(expected_file)
        assert os.path.isfile(expected_file)

        with open(expected_file, 'rb') as f:
            content = json.load(f)

        schema_content['linkedSourceDefinition'] = \
            linked_source_definition_with_opaque_refs
        assert content['definitions'] == schema_content
        assert content['info']['title'] == name

    @staticmethod
    def test_execute_swagger_codegen_success(tmpdir, schema_content,
                                             popen_helper):
        name = 'test'
        swagger_file = tmpdir.join(codegen.SWAGGER_FILE_NAME).strpath
        codegen._write_swagger_file(name, schema_content, tmpdir.strpath)

        stderr_ret = (
            '[main] INFO io.swagger.parser.Swagger20Parser - reading from'
            ' swagger.json'
            '[main] INFO io.swagger.codegen.AbstractGenerator - writing file'
            ' .dvp-gen-output/swagger_server/generated/test_gen_file.py')
        popen_helper.set_popen_output(0, stderr=stderr_ret)
        codegen._execute_swagger_codegen(swagger_file, tmpdir.strpath)

        assert popen_helper.stdout_input == subprocess.PIPE
        assert popen_helper.stderr_input == subprocess.PIPE
        assert os.path.exists(popen_helper.swagger_file)
        assert popen_helper.package_name == codegen.CODEGEN_PACKAGE
        assert popen_helper.module_name == codegen.CODEGEN_MODULE
        assert popen_helper.output_dir == tmpdir.strpath

        # Validate that the "generated" file were created in the right dir.
        util_file = tmpdir.join(codegen.CODEGEN_PACKAGE, 'util.py').strpath
        init_file = tmpdir.join(codegen.CODEGEN_PACKAGE, '__init__.py').strpath
        gen_file = tmpdir.join(codegen.CODEGEN_PACKAGE, codegen.CODEGEN_MODULE,
                               TestCodegen.TEST_GEN_FILE).strpath

        assert os.path.exists(util_file)
        assert os.path.exists(init_file)
        assert os.path.exists(gen_file)

    @staticmethod
    def test_execute_swagger_codegen_java_missing(tmpdir, schema_content,
                                                  popen_helper):
        name = 'test'
        swagger_file = tmpdir.join(codegen.SWAGGER_FILE_NAME).strpath
        codegen._write_swagger_file(name, schema_content, tmpdir.strpath)

        oserr = OSError(errno.ENOENT, 'No such file or directory')
        popen_helper.set_popen_err(oserr)

        with pytest.raises(exceptions.UserError) as err_info:
            codegen._execute_swagger_codegen(swagger_file, tmpdir.strpath)

        message = err_info.value.message
        assert message == ('Swagger python code generation failed.'
                           ' Make sure java is on the PATH.')

        assert popen_helper.stdout_input == subprocess.PIPE
        assert popen_helper.stderr_input == subprocess.PIPE
        assert os.path.exists(popen_helper.swagger_file)
        assert popen_helper.package_name == codegen.CODEGEN_PACKAGE
        assert popen_helper.module_name == codegen.CODEGEN_MODULE
        assert popen_helper.output_dir == tmpdir.strpath

        # Validate that the "generated" file were not created.
        util_file = tmpdir.join(codegen.CODEGEN_PACKAGE, 'util.py').strpath
        init_file = tmpdir.join(codegen.CODEGEN_PACKAGE, '__init__.py').strpath
        gen_file = tmpdir.join(codegen.CODEGEN_PACKAGE, codegen.CODEGEN_MODULE,
                               TestCodegen.TEST_GEN_FILE).strpath

        assert not os.path.exists(util_file)
        assert not os.path.exists(init_file)
        assert not os.path.exists(gen_file)

    @staticmethod
    def test_execute_swagger_codegen_jar_issue(tmpdir, schema_content,
                                               popen_helper):
        name = 'test'
        swagger_file = tmpdir.join(codegen.SWAGGER_FILE_NAME).strpath
        codegen._write_swagger_file(name, schema_content, tmpdir.strpath)

        oserr = OSError(errno.ENFILE, 'Too many open files in system')
        popen_helper.set_popen_err(oserr)

        with pytest.raises(exceptions.UserError) as err_info:
            codegen._execute_swagger_codegen(swagger_file, tmpdir.strpath)

        message = err_info.value.message
        assert message == ('Unable to run {!r} to generate python code.'
                           '\nError code: 23. Error message: Too many open'
                           ' files in system'.format(popen_helper.jar))

        assert popen_helper.stdout_input == subprocess.PIPE
        assert popen_helper.stderr_input == subprocess.PIPE
        assert os.path.exists(popen_helper.swagger_file)
        assert popen_helper.package_name == codegen.CODEGEN_PACKAGE
        assert popen_helper.module_name == codegen.CODEGEN_MODULE
        assert popen_helper.output_dir == tmpdir.strpath

        # Validate that the "generated" file were not created.
        util_file = tmpdir.join(codegen.CODEGEN_PACKAGE, 'util.py').strpath
        init_file = tmpdir.join(codegen.CODEGEN_PACKAGE, '__init__.py').strpath
        gen_file = tmpdir.join(codegen.CODEGEN_PACKAGE, codegen.CODEGEN_MODULE,
                               TestCodegen.TEST_GEN_FILE).strpath

        assert not os.path.exists(util_file)
        assert not os.path.exists(init_file)
        assert not os.path.exists(gen_file)

    @staticmethod
    def test_execute_swagger_codegen_proccess_fail(tmpdir, schema_content,
                                                   popen_helper):
        name = 'test'
        swagger_file = tmpdir.join(codegen.SWAGGER_FILE_NAME).strpath
        codegen._write_swagger_file(name, schema_content, tmpdir.strpath)

        popen_helper.set_popen_output(1)

        with pytest.raises(exceptions.UserError) as err_info:
            codegen._execute_swagger_codegen(swagger_file, tmpdir.strpath)

        message = err_info.value.message
        assert message == ('Swagger python code generation failed.'
                           'See logs for more information.')

        assert popen_helper.stdout_input == subprocess.PIPE
        assert popen_helper.stderr_input == subprocess.PIPE
        assert os.path.exists(popen_helper.swagger_file)
        assert popen_helper.package_name == codegen.CODEGEN_PACKAGE
        assert popen_helper.module_name == codegen.CODEGEN_MODULE
        assert popen_helper.output_dir == tmpdir.strpath

        # Validate that the "generated" file were not created.
        util_file = tmpdir.join(codegen.CODEGEN_PACKAGE, 'util.py').strpath
        init_file = tmpdir.join(codegen.CODEGEN_PACKAGE, '__init__.py').strpath
        gen_file = tmpdir.join(codegen.CODEGEN_PACKAGE, codegen.CODEGEN_MODULE,
                               TestCodegen.TEST_GEN_FILE).strpath

        assert not os.path.exists(util_file)
        assert not os.path.exists(init_file)
        assert not os.path.exists(gen_file)

    @staticmethod
    @pytest.mark.parametrize('plugin_config_file', [None])
    def test_copy_generated_to_dir_success(tmpdir, popen_helper):
        #
        # Setting plugin_config_file fixture to none so no uneeded files get
        # created for popen_helper.
        #
        src_dir = tmpdir.join('src').strpath
        os.mkdir(src_dir)
        dst_dir = tmpdir.join('dst').strpath
        os.mkdir(dst_dir)

        # Using the helper create the files.
        popen_helper.create_codegen_jar_files(src_dir, codegen.CODEGEN_PACKAGE,
                                              codegen.CODEGEN_MODULE)

        # Call the copy function
        codegen._copy_generated_to_dir(src_dir, dst_dir)

        # Validate that the "generated" file were copied.
        util_relpath = os.path.join(codegen.CODEGEN_PACKAGE, 'util.py')
        init_relpath = os.path.join(codegen.CODEGEN_PACKAGE, '__init__.py')
        gen_relpath = os.path.join(codegen.CODEGEN_PACKAGE,
                                   codegen.CODEGEN_MODULE,
                                   TestCodegen.TEST_GEN_FILE)

        assert os.path.exists(os.path.join(dst_dir, util_relpath))
        assert os.path.exists(os.path.join(dst_dir, init_relpath))
        assert os.path.exists(os.path.join(dst_dir, gen_relpath))

        #
        # Also assert that the files were copied not moved so should still
        # exist in the src_dir.
        #
        assert os.path.exists(os.path.join(src_dir, util_relpath))
        assert os.path.exists(os.path.join(src_dir, init_relpath))
        assert os.path.exists(os.path.join(src_dir, gen_relpath))

    @staticmethod
    def test_copy_generated_to_dir_fail(tmpdir):
        src_dir = os.path.join('fake', 'dir')
        # dst_dir needs to be real so that making the dir inside it works.
        dst_dir = tmpdir.strpath

        with pytest.raises(OSError) as err_info:
            codegen._copy_generated_to_dir(src_dir, dst_dir)

        if os.name == 'nt':
            assert err_info.value.strerror == 'The system cannot find the path' \
                                              ' specified'
        else:
            assert err_info.value.strerror == 'No such file or directory'

        assert err_info.value.filename.startswith(src_dir)
