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
    "attrs >= 25.3, < 25.4",
    "certifi >= 2024, < 2025",
    "click == 7.1.2",
    "click-configfile == 0.2.3",
    "configparser >= 7.2, < 7.3",
    "dvp-libs == {}".format(version),
    "dvp-platform == {}".format(version),
    "flake8 >= 7.3, < 7.4",
    "httpretty >= 1.0, < 1.1",
    "importlib-resources >= 6.5, < 6.6",
    "jinja2 >= 3.1, < 3.2",
    "jsonschema >= 4.25, < 4.26",
    "MarkupSafe >= 3.0, < 3.1",
    "pkgutil_resolve_name == 1.3.10",
    "pyyaml >= 6, < 7",
    "requests >= 2.32, < 2.33",
    "six >= 1.16, < 1.17",
    "zipp >= 3.23, < 3.24",
]

setuptools.setup(name='dvp-tools',
                 version=version,
                 install_requires=install_requires,
                 package_dir={'': PYTHON_SRC},
                 packages=setuptools.find_packages(PYTHON_SRC),
                 python_requires='>=3.11, <3.12',
                 )
