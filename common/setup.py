import os
import setuptools

PYTHON_SRC = 'src/main/python'

install_requires = [
  "dvp-api == 1.4.0",
]

with open(os.path.join(PYTHON_SRC, 'dlpx/virtualization/common/VERSION')) as version_file:
    version = version_file.read().strip()

setuptools.setup(name='dvp-common',
                 version=version,
                 install_requires=install_requires,
                 package_dir={'': PYTHON_SRC},
                 packages=setuptools.find_packages(PYTHON_SRC),
)
