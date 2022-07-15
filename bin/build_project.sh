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
	echo "Syntax: sh build_project.sh -[h|b|t|m]"
	echo "  Options   |   Description                 |   Examples"
	echo "     h      |   Print this Help.            |   sh build_project.sh -h"
	echo "----------------------------------------------------------------------------------------------------"
	echo "     b      |   Build the modules.          |   sh build_project.sh -b"
	echo "            |                               |   sh build_project.sh -b -m common"
	echo "----------------------------------------------------------------------------------------------------"
	echo "     t      |   Run tests for the modules.  |   sh build_project.sh -t"
	echo "            |                               |   sh build_project.sh -bt -m tools"
	echo "----------------------------------------------------------------------------------------------------"
	echo "     m      |   provide a list of modules.  |   sh build_project.sh -bt -m common -m libs"
	echo "            |   Valid python modules:       |"
	echo "            |     - common                  |"
	echo "            |     - libs                    |"
	echo "            |     - platform                |"
	echo "            |     - tools                   |"
	echo "            |     - dvp                     |"
	echo "----------------------------------------------------------------------------------------------------"
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

# Global variables
modules=("common" "libs" "platform" "tools" "dvp")
should_build=false
should_test=false

# Run operation for module
run_operations()  {
	module_name=$1
	printf "Operations that will be performed for %s: \n build = %s \n test = %s.\n" "$module_name" "$should_build" "$should_test"
	current_path="$PWD"
	module_path="$(get_project_path)/$module_name"
	cd "$module_path" || exit
	if [ "$should_build" = true ]; then
		echo "########################################## $module_name build started  ##########################################"
		build_module
		echo "########################################## $module_name build complete ##########################################"
	fi
	if [ "$should_test" = true ]; then
		echo "########################################## $module_name tests started  ##########################################"
		test_module
		echo "########################################## $module_name tests complete ##########################################"
	fi
	cd "$current_path" || exit
}

# get the project full path like Users/test-user/repository/virtualization-sdk
get_project_path() {
	SCRIPT_RELATIVE_DIR=$(dirname "${BASH_SOURCE[0]}")
	cd "$SCRIPT_RELATIVE_DIR" || exit
	script_path="$PWD"
	dirname "$script_path"
}

# Build the module
build_module()  {
	pip install -r requirements.txt
	pip install -e .
}

# Test the module
test_module()  {
	python -m pytest src/test/python
}

# Get the options
while getopts ":hbtm:" option; do
	case $option in
	h) # display Help
		Help
		exit
		;;
	b) # Build modules
		should_build=true ;;
	t) # Test modules
		should_test=true ;;
	m) # Check Modules
		if [[ ${modules[*]} =~ (^|[[:space:]])"$OPTARG"($|[[:space:]]) ]]; then
			multi+=("$OPTARG")
		else
			echo "Modules must be one of [${modules[*]}]." && exit 1
		fi ;;
	\?) # Invalid options.
		echo "Error: Invalid option"
		help
		exit 1
		;;
	:) # Missing arguments
		echo "Missing option argument for -$OPTARG" >&2
		exit 1
		;;
	*) # Unimplemented option if any
		echo "Unimplemented option: -$option" >&2
		exit 1
		;;
	esac
done

if [ ${#multi[@]} -eq 0 ]; then
	multi=("${modules[@]}")
fi

for module in "${multi[@]}"; do
	run_operations "$module"
done
