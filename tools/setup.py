import os
import setuptools

PYTHON_SRC = 'src/main/python'

with open(os.path.join(PYTHON_SRC, 'dlpx/virtualization/_internal/VERSION')) as version_file:
    version = version_file.read().strip()

install_requires = [
    "click == 7.1.2",
    "click-configfile == 0.2.3",
    "dvp-platform == {}".format(version),
    "dvp-libs == {}".format(version),
    "flake8 == 6.0.0",
    "jinja2 == 3.1.2",
    "jsonschema == 4.17.3",
    "pyyaml == 6",
    "requests == 2.28.1",
    "httpretty == 1.0.5",
]

setuptools.setup(name='dvp-tools',
                 version=version,
                 install_requires=install_requires,
                 package_dir={'': PYTHON_SRC},
                 packages=setuptools.find_packages(PYTHON_SRC),
                 python_requires='>=3.8, <3.9',
)
