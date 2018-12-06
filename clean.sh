#!/bin/bash
#
# Copyright (c) 2018 by Delphix. All rights reserved.
#

# This script must be executed from the root directory of the virtualization-sdk repo.
cd "$(git rev-parse --show-toplevel)"

rm -rf bin java_classes python_classes virtualization-sdk-jar
