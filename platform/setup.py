import os
import setuptools

PYTHON_SRC = 'src/main/python'

with open(os.path.join(PYTHON_SRC, 'dlpx/virtualization/platform/VERSION')) as version_file:
    version = version_file.read().strip()

install_requires = [
  "dvp-api == 1.7.0",
  "dvp-common == {}".format(version),
  "enum34;python_version < '3.4'",
]

setuptools.setup(name='dvp-platform',
                 version=version,
                 install_requires=install_requires,
                 package_dir={'': PYTHON_SRC},
                 packages=setuptools.find_packages(PYTHON_SRC),
                 python_requires='>=2.7, <3.9, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*',
)
