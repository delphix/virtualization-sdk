#!/bin/sh
#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# This script uploads the two jars produced by split_v1.0.0_jar.sh to artifactory.
#

git rev-parse --is-inside-work-tree || exit 1
ROOT=`git rev-parse --show-toplevel`
LIBS_DIR=${ROOT}/build/libs

#
# These urls and names determine how the artifacts are specified with Gradle. Here is how they look in Gradle:
#    implementation group: "com.delphix.virtualization.platform", name:"api-java", version:"1.0.0"
#    implementation group: "com.delphix.virtualization.sdk", name:"wrappers-python", version:"1.0.0"
#
# These are temporary. The Java jar will likely be pulled in directly during the Gradle build since the protobuf
# messages will live in the app gate. The Python jar will be pulled in until we deprecate support for v1.0.0.
#
ARTIFACTORY_API_URL=http://artifactory.delphix.com/artifactory/virtualization-sdk/com/delphix/virtualization/platform/api-java/1.0.0
ARTIFACTORY_WRAPPERS_URL=http://artifactory.delphix.com/artifactory/virtualization-sdk/com/delphix/virtualization/sdk/wrappers-python/1.0.0

API_JAR_NAME=api-java-1.0.0.jar
WRAPPERS_JAR_NAME=wrappers-python-1.0.0.jar

API_JAR_PATH=${LIBS_DIR}/${API_JAR_NAME}
WRAPPERS_JAR_PATH=${LIBS_DIR}/${WRAPPERS_JAR_NAME}

[ ! -f ${API_JAR_PATH} ] && echo "${API_JAR_PATH} does not exist. Run ${ROOT}/bin/split_v1.0.0_jar.sh to create it and then run this script again." && exit 1
[ ! -f ${WRAPPERS_JAR_PATH} ] && echo "${WRAPPERS_JAR_PATH} does not exist. Run ${ROOT}/bin/split_v1.0.0_jar.sh to create it and then run this script again." && exit 1

[ -z ${ARTIFACTORY_JAR_KEY} ] && echo "The environment variable 'ARTIFACTORY_JAR_KEY' is not set. Set it and run this script again." && exit 1

curl -H "X-JFrog-Art-Api: ${ARTIFACTORY_JAR_KEY}" -T ${API_JAR_PATH} ${ARTIFACTORY_API_URL}/${API_JAR_NAME}
curl -H "X-JFrog-Art-Api: ${ARTIFACTORY_JAR_KEY}" -T ${WRAPPERS_JAR_PATH} ${ARTIFACTORY_WRAPPERS_URL}/${WRAPPERS_JAR_NAME}
