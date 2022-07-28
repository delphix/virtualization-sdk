#!/bin/bash
#
# Copyright (c) 2022 by Delphix. All rights reserved.
#

# This script provides functionality to build and run test cases for all python packages. The same script can be used
# to build and run test cases for specific python packages also.

############################################################
# Global Variables                                         #
############################################################
modules=("common" "libs" "platform" "tools" "dvp")
should_build=false
should_test=false
verbose=false
screenSize=$(tput cols)
equalFiller="="
greenColor=$(tput setaf 10)
orangeColor=$(tput setaf 208)
noColor=$(tput sgr0)

############################################################
# Help                                                     #
############################################################
Help() {
	# Display Help
	echo "Build and Run test cases for python modules common, libs, platform, tools and dvp."
	echo
	tput setaf 1
	echo "Syntax: sh build_project.sh -[h|b|t|v|m]"
	tput sgr0
	tput bold
	echo "  Options   |   Description                 |   Examples"
	tput sgr0
	echo "----------------------------------------------------------------------------------------------------"
	echo "     h      |   Print this Help.            |   sh build_project.sh -h"
	echo "----------------------------------------------------------------------------------------------------"
	echo "     b      |   Build the modules.          |   sh build_project.sh -b"
	echo "            |                               |   sh build_project.sh -b -m common"
	echo "----------------------------------------------------------------------------------------------------"
	echo "     t      |   Run tests for the modules.  |   sh build_project.sh -t"
	echo "            |                               |   sh build_project.sh -bt -m tools"
	echo "----------------------------------------------------------------------------------------------------"
	echo "     v      |   Verbose mode on             |   sh build_project.sh -t -v"
	echo "            |                               |   sh build_project.sh -bvt -m tools"
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

# Run operation for module
run_operations()  {
	module_name=$1
	current_path="$PWD"
	module_path="$(get_project_path)/$module_name"
	cd "$module_path" || exit
	if [ "$should_build" = true ]; then
		print_as_per_screen_size " $module_name build starts " "${orangeColor}" ${equalFiller} "${screenSize}"
		build_module
		print_as_per_screen_size " $module_name build complete " "${greenColor}" ${equalFiller} "${screenSize}"
	fi
	if [ "$should_test" = true ]; then
		print_as_per_screen_size " $module_name tests starts " "${orangeColor}" ${equalFiller} "${screenSize}"
		test_module
		print_as_per_screen_size " $module_name tests complete " "${greenColor}" ${equalFiller} "${screenSize}"
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
	if [ "$verbose" = true ]; then
		pip install -v -r requirements.txt
		pip install -v -e .
	else
		pip install -q -r requirements.txt --ignore-installed
		pip install -q -e .
	fi
}

# Test the module
test_module()  {
	if [ "$verbose" = true ]; then
		python -m pytest -v src/test/python
	else
		python -m pytest src/test/python
	fi
}

# Print the provided input in the center of screen by appending and prepending fillers.
print_as_per_screen_size() {
	input="$1"
	color=$2
	filler=$3
	columns=$4
	width="${#input}"
	adjust=$(((columns - width) / 2))
	printf "${filler}%.0s" $(seq $adjust)
	printf "${color}%s${noColor}" "${input}"
	if [[ $((width % 2)) -eq 0 ]]; then
		adjust=$((adjust + 1))
	fi
	printf "${filler}%.0s" $(seq $adjust)
}

# Get the options
while getopts ":hbtvm:" option; do
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
	v) # Verbose mode
		verbose=true ;;
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

if [ "$should_build" = true ] || [ "$should_test" = true ]; then
	if [ ${#multi[@]} -eq 0 ]; then
		multi=("${modules[@]}")
	fi

	for module in "${multi[@]}"; do
		run_operations "$module"
	done
fi
