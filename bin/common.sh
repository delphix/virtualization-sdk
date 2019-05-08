#!/bin/bash
#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# A helper function that takes an arbitrary number of arguments, prints them to stdout and exits with a non-zero exit
# code.
die() { printf "$*\n" 1>&2; exit 1; }
