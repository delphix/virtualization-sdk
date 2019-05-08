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

cd ${ROOT}

# Diff 'build.gradle' with origin/master. This works since we don't have any backport branches. Grep that diff
# for a line that starts with a '+' that signifies an addition in git. The line should then have 'version =' followed
# by a something in quotes that starts with x.y.z where x, y, and z are digits. Anything is allowed to follow that
# until the quotes end.
VERSION=`git diff origin/master -- build.gradle | grep '^\+\s*version\s*=\s*"[0-9]\.[0-9]\.[0-9].*"'`
[[ -z ${VERSION} ]] && die "The SDK version has not been increased. Please increment the version in <virtualization-sdk>/build.gradle."

cd ${CWD}

exit 0
