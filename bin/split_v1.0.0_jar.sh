#!/bin/bash
#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# This script downloads the original 1.0.0 jar and splits it into two jars.
# The first contains only Java protobuf classes. The second jar contains
# Python protobuf classes and common, libs, and platform.
# Both of these are consumed by the Delphix Engine.
#
# This script should only need to be ran once ever to generate these jars. In order
# to support multiple version of the Virtualization API, we are now going to ship
# the wrappers with the plugin itself instead of with the Delphix Engine.
#
# However, in order to be backwards compatible with SDK version 1.0.0, we must
# continue shipping the 1.0.0 wrappers with the Delphix Engine. The Delphix Engine
# will continue to need the Java protobuf classes of the latest version, but will
# no longer need the Python classes nor common, libs, and platform hence why this
# script will only need to be ran once.
#
# This script exists primarily to document how the jars were built in case there is
# an issue and we need to reproduce it.
#

git rev-parse --is-inside-work-tree || exit 1
ROOT=`git rev-parse --show-toplevel`

LIBS_DIR=${ROOT}/build/libs
BUILD_DIR=${ROOT}/build/split-1.0.0/
EXTRACTED_DIR=${BUILD_DIR}/extracted
JAVA_DIR=${BUILD_DIR}/java
PYTHON_DIR=${BUILD_DIR}/python

# Start with a clean directory
rm -rf ${BUILD_DIR}

mkdir ${BUILD_DIR}
mkdir ${LIBS_DIR}
mkdir ${EXTRACTED_DIR}
mkdir ${JAVA_DIR}
mkdir ${PYTHON_DIR}

# Download the original 1.0.0 jar that contains both Java and Python files.
CURRENT_JAR_NAME="sdk-1.0.0.jar"
JAR_FILE=${BUILD_DIR}/${CURRENT_JAR_NAME}
wget -P ${BUILD_DIR} http://artifactory.delphix.com/artifactory/virtualization-sdk/com/delphix/virtualization/sdk/1.0.0/${CURRENT_JAR_NAME}

# Extract the com/ directory into the Java directory. These are all the Java protobuf files.
pushd ${JAVA_DIR}
jar xvf ${JAR_FILE} com/

# Create a new jar that contains com/*.
jar cvf ${LIBS_DIR}/api-java-1.0.0.jar .

# Extract all the Python files into their own directory.
pushd ${PYTHON_DIR}
jar xvf ${JAR_FILE} dlpx google enum six.py typing.py

# Compile google and enum files
python -m compileall -f -d dlpx dlpx/
python -m compileall -f -d google google/
python -m compileall -f -d enum enum/
python -m compileall -f -d six six.py
python -m compileall -f -d typing typing.py

#
# Zip the files and base64 encode the zip. This is odd, but since we already import the
# plugin from a base64 encoded zip this makes it easy to import the wrappers as well.
#
zip -r virtualization-sdk-wrappers-1.0.0.zip `find . -name "*.py" -o -name "*.pyc"`
base64 --input virtualization-sdk-wrappers-1.0.0.zip > virtualization-sdk-wrappers-v1.0.0.txt

# Create a jar with just the text file containing the base64 encoded zip.
jar cvf ${LIBS_DIR}/wrappers-python-1.0.0.jar virtualization-sdk-wrappers-v1.0.0.txt

popd
popd
