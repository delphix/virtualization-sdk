#!/bin/bash
#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# This script uploads all Python distributions created by the SDK. It assumes that all artifacts
# already exist. This is not intended to be a long term solution. Instead, this is a dirty way to abstract away
# some of this logic. It should instead be rolled directly into the Gradle build and our future CI pipeline.
#
# This script can upload to both our internal dev and prod PyPI repositories. It defaults to dev.

SCRIPT_DIR=`dirname $0`
source ${SCRIPT_DIR}/common.sh

USAGE="Usage: upload.sh [--prod]"

# Validate usage is correct and expected environment variables are set.
if [[ $# -gt 1 ]]; then
    die $USAGE
elif [[ $# -eq 1 && $1 != "--prod" ]]; then
    die $USAGE
elif [[ -z ${ARTIFACTORY_PYPI_USER} || -z ${ARTIFACTORY_PYPI_PASS} ]]; then
    die "ARTIFACTORY_PYPI_USER and/or ARTIFACTORY_PYPI_PASS environment variables are not set. Set them or pass them in as arguments to upload.sh."
fi

# dvp-local-pypi is used for testing and is the default. delphix-local is our internal production PyPI repository and
# should only be used when publishing final versions.
if [[ $# -eq 0 ]]; then
  REPO="http://artifactory.delphix.com/artifactory/api/pypi/dvp-local-pypi"
else
  REPO="http://artifactory.delphix.com/artifactory/api/pypi/delphix-local"
fi

# Check early that 'twine' is on the path.
command -v twine 2>&1 >/dev/null || die "'twine' is either not install or not on PATH. To install 'twine' run 'pip install twine'"

# All the file paths need to be relative to the root of the git repo
ROOT=`git rev-parse --show-toplevel`

# Get the SDK version from build.gradle in the root of the SDK. This essentially just looks for a line that has
# 'version =' and pulls the value from the quotes after it. Nothing too sophisticated and fairly error prone.
VERSION=`cat "${ROOT}/build.gradle" | grep '^\s*version\s*=\s*"*"'| sed -E 's/.*"(.*)".*/\1/g'`
[ -z "$VERSION" ] && die "Failed to retrieve SDK version from build.gradle."

echo "Uploading 'common' Python distribution..."
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/common/build/python-dist/*${VERSION}.tar.gz" > /dev/null
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/common/build/python-dist/*${VERSION//-/_}*.whl" > /dev/null

echo "Uploading 'platform' Python distribution..."
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/platform/build/python-dist/*${VERSION}.tar.gz" > /dev/null
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/platform/build/python-dist/*${VERSION//-/_}*.whl" > /dev/null

echo "Uploading 'libs' Python distribution..."
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/libs/build/python-dist/*${VERSION}.tar.gz" > /dev/null
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/libs/build/python-dist/*${VERSION//-/_}*.whl" > /dev/null

echo "Uploading 'tools' Python distribution..."
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/tools/build/python-dist/*${VERSION}.tar.gz" > /dev/null
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/tools/build/python-dist/*${VERSION//-/_}*.whl" > /dev/null

echo "Uploading 'dvp' Python distribution..."
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/dvp/build/python-dist/*${VERSION}.tar.gz" > /dev/null
twine upload --repository-url ${REPO} -u ${ARTIFACTORY_PYPI_USER} -p ${ARTIFACTORY_PYPI_PASS} "${ROOT}/dvp/build/python-dist/*${VERSION//-/_}*.whl" > /dev/null

exit 0
