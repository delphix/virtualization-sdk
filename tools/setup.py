import os
import setuptools

PYTHON_SRC = 'src/main/python'

with open(os.path.join(PYTHON_SRC, 'dlpx/virtualization/_internal/VERSION')) as version_file:
    version = version_file.read().strip()

install_requires = [
  "click >= 7.1",
  "click-configfile == 0.2.3",
  "dvp-platform == {}".format(version),
  "enum34 >= 1.1.6",
  "flake8 >= 3.6",
  "jinja2 >= 2.10",
  "jsonschema >= 3",
  "pyyaml >= 3",
  "requests >= 2.21.0",
]

setuptools.setup(name='dvp-tools',
                 version=version,
                 install_requires=install_requires,
                 package_dir={'': PYTHON_SRC},
                 packages=setuptools.find_packages(PYTHON_SRC),
)
