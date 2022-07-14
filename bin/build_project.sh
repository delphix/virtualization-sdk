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
	echo "options:"
	echo "h     Print this Help."
	echo "b     Build the modules."
	echo "t     Run tests for the modules."
	echo "m     provide a list of modules. Valid python modules: common, libs, platform, tools, dvp."
	echo ""
	echo "Examples:"
	echo "1. Build all -> 'sh build_project.sh -b'"
	echo "2. Test all -> 'sh build_project.sh -t'"
	echo "3. Build and test all -> 'sh build_project.sh -bt'"
	echo "4. Build and test common -> 'sh build_project.sh -bt -m common'"
	echo "5. Build and test common and libs -> 'sh build_project.sh -bt -m common -m libs'"
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
build=false
test=false

# Run operation for module
run_operations()  {
	module_name=$1
	should_build=$2
	should_test=$3
	printf "Operations that will be performed for %s: \n build = %s \n test = %s.\n" "$module_name" "$should_build" "$should_test"
	current_path="$PWD"
	module_path="$( get_project_path )/$module_name"
	cd "$module_path" || xit
	if [ "$should_build" = true ]; then
		build_module
	fi
	if [ "$should_test" = true ]; then
		test_module
	fi
	cd "$current_path" || exit
	pwd
}

# get the module full path
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
		Help ;;
	b) # Build modules
		build=true ;;
	t) # Test modules
		test=true ;;
	m) # Check Modules
		if [[ ${modules[*]} =~ (^|[[:space:]])"$OPTARG"($|[[:space:]]) ]]; then
			multi+=("$OPTARG")
		else
			echo "Modules can be one of [${modules[*]}]." && exit 1
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

for val in "${multi[@]}"; do
	run_operations "$val" ${build} $test
done
