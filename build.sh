#!/bin/bash
#
# Copyright (c) 2018, 2019 by Delphix. All rights reserved.
#

# This script must be executed from the root directory of the virtualization-sdk repo.
cd "$(git rev-parse --show-toplevel)"

echo "Copying Virtualization SDK binaries from NAS..."
scp -r delphix@support-tools:/nas/engineering/fdrozdowski/virtualization-sdk/bin .

echo "Preparing Virtualization SDK jar directory..."
JAR_DIRECTORY=virtualization-sdk-jar
mkdir -p ${JAR_DIRECTORY}

cp bin/six.py ${JAR_DIRECTORY}
cp -r bin/google ${JAR_DIRECTORY}

mkdir -p ${JAR_DIRECTORY}/dlpx/virtualization/
touch ${JAR_DIRECTORY}/dlpx/__init__.py
touch ${JAR_DIRECTORY}/dlpx/virtualization/__init__.py

cp common/src/main/proto/dlpx/virtualization/common.proto ${JAR_DIRECTORY}/dlpx/virtualization/common.proto
cp platform/src/main/proto/dlpx/virtualization/delphix-platform.proto ${JAR_DIRECTORY}/dlpx/virtualization/platform.proto
cp libs/src/main/proto/dlpx/virtualization/delphix-libs.proto ${JAR_DIRECTORY}/dlpx/virtualization/libs.proto

cd ${JAR_DIRECTORY}
cp -r ./../bin .

echo "Compiling protobuf definitions to Java and Python classes..."
bin/protoc-3.6.1-osx-x86_64/bin/protoc -I=. --java_out=. --python_out=. dlpx/virtualization/common.proto dlpx/virtualization/platform.proto dlpx/virtualization/libs.proto

echo "Pre-compiling the Python Virtualization Platform protobuf module..."

# The command below assumes that there's "python" on the PATH and it resolves to Python 2.7 (CPython).
java -jar bin/jython-standalone-2.7.1.jar -Dcpython_cmd=python -m py_compile dlpx/virtualization/platform_pb2.py

echo "Compiling Java source files to Java classes..."
javac -d . -classpath bin/protobuf-java-3.6.1.jar com/delphix/virtualization/common/*java com/delphix/virtualization/platform/*java com/delphix/virtualization/libs/*java

rsync -av --progress ./../platform/src/main/python/dlpx/virtualization/platform/ . --exclude __init__.py
rm -r bin

echo "Creating a Virtualization SDK jar..."
JAR_FILE_NAME=sdk-\<version\>.jar
jar cvf ${JAR_FILE_NAME} .
mv ${JAR_FILE_NAME} ./../
