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

cp common/src/proto/delphix.proto ${JAR_DIRECTORY}/dlpx/virtualization/common.proto
cp platform/src/proto/delphix-platform.proto ${JAR_DIRECTORY}/dlpx/virtualization/platform.proto
cp libs/src/proto/delphix-libs.proto ${JAR_DIRECTORY}/dlpx/virtualization/libs.proto

cd ${JAR_DIRECTORY}
cp -r ./../bin .

echo "Compiling protobuf definitions to Java and Python classes..."
bin/protoc-3.6.1-osx-x86_64/bin/protoc -I=dlpx/virtualization --java_out=. --python_out=dlpx/virtualization dlpx/virtualization/common.proto dlpx/virtualization/platform.proto dlpx/virtualization/libs.proto

echo "Compiling Java source files to Java classes..."
javac -d . -classpath bin/protobuf-java-3.6.1.jar com/delphix/virtualization/common/*java com/delphix/virtualization/platform/*java com/delphix/virtualization/libs/*java

rsync -av --progress ./../platform/src/python/virtualization/platform/ . --exclude __init__.py

echo "Creating a Virtualization SDK jar..."
JAR_FILE_NAME=sdk-\<version\>.jar
jar cvf ${JAR_FILE_NAME} .
mv ${JAR_FILE_NAME} ./../
rm -r bin
