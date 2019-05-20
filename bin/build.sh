#!/bin/bash
#
# Copyright (c) 2018, 2019 by Delphix. All rights reserved.
#

SCRIPT_DIR=`dirname $0`
source ${SCRIPT_DIR}/common.sh

# This script must be executed from the root directory of the virtualization-sdk repo.
ROOT=`git rev-parse --show-toplevel`
cd $ROOT

mkdir -p build/libs
cd build/libs

echo "Copying Virtualization SDK binaries from NAS..."
scp -r delphix@support-tools:/nas/engineering/fdrozdowski/virtualization-sdk/bin .

echo "Preparing Virtualization SDK jar directory..."
JAR_DIRECTORY=virtualization-sdk-jar
mkdir -p ${JAR_DIRECTORY}

cp bin/six.py ${JAR_DIRECTORY}
cp -r bin/google ${JAR_DIRECTORY}
cp -r bin/enum ${JAR_DIRECTORY}
cp bin/typing.py ${JAR_DIRECTORY}

mkdir -p ${JAR_DIRECTORY}/dlpx/virtualization/
touch ${JAR_DIRECTORY}/dlpx/__init__.py
touch ${JAR_DIRECTORY}/dlpx/virtualization/__init__.py

cp ${ROOT}/common/src/main/proto/dlpx/virtualization/common.proto ${JAR_DIRECTORY}/dlpx/virtualization/common.proto
cp ${ROOT}/platform/src/main/proto/dlpx/virtualization/platform.proto ${JAR_DIRECTORY}/dlpx/virtualization/platform.proto
cp ${ROOT}/libs/src/main/proto/dlpx/virtualization/libs.proto ${JAR_DIRECTORY}/dlpx/virtualization/libs.proto

cd ${JAR_DIRECTORY}
cp -r ./../bin .

echo "Compiling protobuf definitions to Java and Python classes..."
bin/protoc-3.6.1-osx-x86_64/bin/protoc -I=. --java_out=. --python_out=. dlpx/virtualization/common.proto dlpx/virtualization/platform.proto dlpx/virtualization/libs.proto

echo "Pre-compiling the Python Virtualization Platform protobuf module..."

# The command below assumes that there's "python" on the PATH and it resolves to Python 2.7 (CPython).
java -jar bin/jython-standalone-2.7.1.jar -Dcpython_cmd=python -m py_compile dlpx/virtualization/platform_pb2.py
java -jar bin/jython-standalone-2.7.1.jar -Dcpython_cmd=python -m py_compile dlpx/virtualization/libs_pb2.py

echo "Compiling Java source files to Java classes..."
javac -d . -classpath bin/protobuf-java-3.6.1.jar com/delphix/virtualization/common/*java com/delphix/virtualization/platform/*java com/delphix/virtualization/libs/*java > /dev/null

rsync -av --progress ${ROOT}/common/src/main/python/dlpx/ dlpx/ > /dev/null
rsync -av --progress ${ROOT}/platform/src/main/python/dlpx/ dlpx/ > /dev/null
rsync -av --progress ${ROOT}/libs/src/main/python/dlpx/ dlpx/ > /dev/null
rm -r bin

VERSION=`cat "${ROOT}/build.gradle" | grep '^\s*version\s*=\s*"*"'| sed -E 's/.*"(.*)".*/\1/g'`
[ -z "$VERSION" ] && die "Failed to retrieve SDK version from build.gradle."

echo "Creating a Virtualization SDK jar..."
JAR_FILE_NAME="sdk-$VERSION.jar"
jar cvf ${JAR_FILE_NAME} . > /dev/null
mv ${JAR_FILE_NAME} ./..

exit 0
