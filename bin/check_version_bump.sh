#!/bin/bash
#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# This script checks the diff of 'build.gradle' and fails if the version has not been changed. This is a crude
# implementation of this check and should not be kept around for long. Instead, the version should probably be managed
# primarily by our CI pipeline so no manual action is needed.

ROOT=`git rev-parse --show-toplevel`
SCRIPT_DIR=`dirname $0`
CWD=`pwd`

source ${SCRIPT_DIR}/common.sh

# Diff 'build.gradle' with origin/master. This works since we don't have any backport branches. Grep that diff
# for a line that starts with a '+' that signifies an addition in git. The line should then have 'version =' followed
# by a something in quotes that starts with x.y.z where x, y, and z are digits. Anything is allowed to follow that
# until the quotes end.
GRADLE_VERSION_REGEX=".*([0-9]\.[0-9]\.[0-9].*)\""
GRADLE_VERSION_DIFF=`git diff origin/master -- $ROOT/build.gradle | grep '^\+\s*version\s*=\s*"[0-9]\.[0-9]\.[0-9].*"'`

# Extract the exact version string from the diff.
if [[ $GRADLE_VERSION_DIFF =~ $GRADLE_VERSION_REGEX ]]; then
    GRADLE_VERSION=${BASH_REMATCH[1]}
fi

[[ -z ${GRADLE_VERSION} ]] && die "The SDK version has not been increased. Please increment the version in <virtualization-sdk>/build.gradle."

# Unfortunately there are currently two places to specify the version. Validate
# that the version in tools has been changed.
TOOLS_VERSION_REGEX=".*([0-9]\.[0-9]\.[0-9].*)"
TOOLS_VERSION_DIFF=`git diff origin/master -- $ROOT/tools/src/main/python/dlpx/virtualization/_internal/settings.cfg | grep '^\+\s*package_version\s*=\s*[0-9]\.[0-9]\.[0-9].*'`

if [[ $TOOLS_VERSION_DIFF =~ $TOOLS_VERSION_REGEX ]]; then
    TOOLS_VERSION=${BASH_REMATCH[1]}
fi

[[ -z $TOOLS_VERSION ]] && die "The SDK version has been increased in <virtualization-sdk/build.gradle but not in <virtualization-sdk>/tools/src/main/python/dlpx/virtualization/_internal/settings.cfg. Please increment the version there as well. These versions must match."

# Validate that the two versions are the same.
[[ $GRADLE_VERSION != $TOOLS_VERSION ]] && echo "The version in <virtualization-sdk>/build.gradle ($GRADLE_VERSION) does not match the version in <virtualization-sdk>/tools/src/main/python/dlpx/virtualization/_internal/settings.cfg ($TOOLS_VERSION). These versions must match."

exit 0
