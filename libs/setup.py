import os
import setuptools

PYTHON_SRC = 'src/main/python'

with open(os.path.join(PYTHON_SRC, 'dlpx/virtualization/libs/VERSION')) as version_file:
    version = version_file.read().strip()

install_requires = [
  "dvp-api == 1.4.0",
  "dvp-common == {}".format(version)
]

setuptools.setup(name='dvp-libs',
                 version=version,
                 install_requires=install_requires,
                 package_dir={'': PYTHON_SRC},
                 packages=setuptools.find_packages(PYTHON_SRC),
)
