import os
import setuptools

PYTHON_SRC = 'src/main/python'

with open(os.path.join(PYTHON_SRC, 'dlpx/virtualization/_internal/VERSION')) as version_file:
    version = version_file.read().strip()

#
# Update the dependency using below use cases
# 1. Dependency version change does not break test cases or have code issues
#   - Only update the maximum version (<).
# 2. Dependency version changes break test cases or have code issues
#   - Update the minimum as well as maximum version along with code changes.
#
install_requires = [
    "attrs >= 22.2, < 22.3",
    "certifi >= 2022, < 2023",
    "click == 7.1.2",
    "click-configfile == 0.2.3",
    "configparser >= 5.3, < 5.4",
    "dvp-libs == {}".format(version),
    "dvp-platform == {}".format(version),
    "flake8 >= 6.0, < 6.1",
    "httpretty >= 1.0, < 1.1",
    "importlib-resources >= 5.10, < 5.11",
    "jinja2 >= 3.1, < 3.2",
    "jsonschema >= 4.17, < 4.18",
    "MarkupSafe >= 2.1, < 2.2",
    "pkgutil_resolve_name == 1.3.10",
    "pyyaml >= 6, < 7",
    "requests >= 2.31, < 2.32",
    "six >= 1.16, < 1.17",
    "zipp >= 3.11, < 3.12",
]

setuptools.setup(name='dvp-tools',
                 version=version,
                 install_requires=install_requires,
                 package_dir={'': PYTHON_SRC},
                 packages=setuptools.find_packages(PYTHON_SRC),
                 python_requires='>=3.11, <3.12',
                 )
