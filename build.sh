#!/bin/bash
#
# Copyright (c) 2018 by Delphix. All rights reserved.
#

# This script must be executed from the root directory of the virtualization-sdk repo.
cd "$(git rev-parse --show-toplevel)"

echo "Copying Virtualization SDK binaries from NAS..."
scp -r delphix@support-tools:/nas/engineering/fdrozdowski/virtualization-sdk/bin .

echo "Compiling protobuf definitions to Java and Python classes..."
mkdir -p java_classes/build
mkdir -p python_classes
bin/protoc-3.6.1-osx-x86_64/bin/protoc -I=common/src/proto -I=libs/src/proto -I=platform/src/proto -I=. --java_out=java_classes --python_out=python_classes common/src/proto/delphix.proto platform/src/proto/delphix-platform.proto libs/src/proto/delphix-libs.proto

echo "Compiling Java source files to Java classes..."
javac -d java_classes/build/ -classpath bin/protobuf-java-3.6.1.jar java_classes/com/delphix/virtualization/common/*java java_classes/com/delphix/virtualization/platform/*java java_classes/com/delphix/virtualization/libs/*java

echo "Preparing Virtualization SDK jar directory..."
JAR_DIRECTORY=virtualization-sdk-jar
mkdir -p ${JAR_DIRECTORY}
cp bin/six.py ${JAR_DIRECTORY}
cp -r bin/google ${JAR_DIRECTORY}
cp -r python_classes/ ${JAR_DIRECTORY}
cp -r java_classes/build/ ${JAR_DIRECTORY}
rsync -av --progress platform/src/python/virtualization/platform/ ${JAR_DIRECTORY} --exclude __init__.py

echo "Creating a Virtualization SDK jar..."
JAR_FILE_NAME=sdk-0.0.0.jar
cd ${JAR_DIRECTORY}
jar cvf ${JAR_FILE_NAME} .
mv ${JAR_FILE_NAME} ./../

echo "Success!"
