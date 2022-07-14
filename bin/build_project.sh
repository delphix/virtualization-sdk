#!/bin/bash
#
# Copyright (c) 2022 by Delphix. All rights reserved.
#

# This script provides functionality to build and run test cases for all python packages. The same script can be used
# to build and run test cases for specific python packages also.

############################################################
# Help                                                     #
############################################################
Help() {
	# Display Help
	echo "Build and Run test cases for python modules common, libs, platform, tools and dvp."
	echo
	echo "Syntax: ./build_project.sh -[h|b|t] [modules]"
	echo "options:"
	echo "h     Print this Help."
	echo "b     Build the module. If [modules] is provided, only that specific module will be build."
	echo "t     Run tests for the module. If [modules] is provided, only that specific module will be tested."
	echo ""
	echo "[module]:"
	echo "Provide a comma (,) separated list of python modules. Below are the valid python modules."
	echo "common, libs, platform, tools, dvp"
	echo
}

############################################################
############################################################
# Main program                                             #
############################################################
############################################################
############################################################
# Process the input options. Add options as needed.        #
############################################################

# Python modules

# Get the options
while getopts ":hbt:" option; do
	case $option in
	h) # display Help
		Help
		exit
		;;
	b) # Build modules
		echo "Build modules."
		exit ;;
	t) # Build and test modules
	  	echo "Build module and run tests."
		exit ;;
	\?) # Invalid option
		echo "Error: Invalid option"
		exit
		;;
	esac
done
