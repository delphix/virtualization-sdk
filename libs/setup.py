import os
import setuptools

PYTHON_SRC = 'src/main/python'

with open(os.path.join(PYTHON_SRC, 'dlpx/virtualization/libs/VERSION')) as version_file:
    version = version_file.read().strip()

install_requires = [
    "dvp-api == 1.9.0",
    "dvp-common == {}".format(version),
    "six >= 1.16, < 1.17",
]

setuptools.setup(name='dvp-libs',
                 version=version,
                 install_requires=install_requires,
                 package_dir={'': PYTHON_SRC},
                 packages=setuptools.find_packages(PYTHON_SRC),
                 python_requires='>=3.11, <3.12',
                 )
