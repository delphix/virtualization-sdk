import os
import setuptools

PYTHON_SRC = 'src/main/python'

with open(os.path.join(PYTHON_SRC, 'dlpx/virtualization/VERSION')) as version_file:
    version = version_file.read().strip()

install_requires = [
  "dvp-common == {}".format(version),
  "dvp-libs == {}".format(version),
  "dvp-platform == {}".format(version),
  "dvp-tools == {}".format(version)
]

setuptools.setup(name='dvp',
                 version=version,
                 install_requires=install_requires,
                 package_dir={'': PYTHON_SRC},
                 packages=setuptools.find_packages(PYTHON_SRC),
)
