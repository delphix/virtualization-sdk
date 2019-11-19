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

echo "Preparing Virtualization SDK jar directory..."
JAR_DIRECTORY=virtualization-sdk-jar
mkdir -p ${JAR_DIRECTORY}

echo "Copying Virtualization SDK binaries from NAS..."
scp -r delphix@support-tools:/nas/engineering/fdrozdowski/virtualization-sdk/bin/protoc-3.6.1-osx-x86_64 .
scp delphix@support-tools:/nas/engineering/fdrozdowski/virtualization-sdk/bin/protobuf-java-3.6.1.jar .

mkdir -p dlpx/virtualization
cp ${ROOT}/common/src/main/proto/dlpx/virtualization/common.proto dlpx/virtualization/common.proto
cp ${ROOT}/platform/src/main/proto/dlpx/virtualization/platform.proto dlpx/virtualization/platform.proto
cp ${ROOT}/libs/src/main/proto/dlpx/virtualization/libs.proto dlpx/virtualization/libs.proto

echo "Compiling protobuf definitions to Java and Python classes..."
protoc-3.6.1-osx-x86_64/bin/protoc -I=. --java_out=${JAR_DIRECTORY} dlpx/virtualization/common.proto dlpx/virtualization/platform.proto dlpx/virtualization/libs.proto

echo "Compiling Java source files to Java classes..."
find ${JAR_DIRECTORY} -name "*.java" > sources.txt
javac -classpath protobuf-java-3.6.1.jar @sources.txt

VERSION=`cat "${ROOT}/build.gradle" | grep '^\s*version\s*=\s*"*"'| sed -E 's/.*"(.*)".*/\1/g'`
[ -z "$VERSION" ] && die "Failed to retrieve SDK version from build.gradle."

echo "Creating a Virtualization SDK jar..."
JAR_FILE_NAME="api-java-$VERSION.jar"
jar cvf ${JAR_FILE_NAME} -C ${JAR_DIRECTORY} . > /dev/null

exit 0
