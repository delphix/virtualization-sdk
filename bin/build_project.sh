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
coverage=false
flake8=false
screenSize=$(tput cols)
equalFiller="="
greenColor=$(tput setaf 10)
orangeColor=$(tput setaf 208)
noColor=$(tput sgr0)
blackColor=$(tput setaf 0)
blueColor=$(tput setaf 31)

############################################################
# Help                                                     #
############################################################
Help() {
  # Display Help
  tput setaf 11
  echo "Build and Run test cases for python modules common, libs, platform, tools and dvp."
  tput setaf 1
  echo "Syntax: sh build_project.sh -[h|b|t|v|m]"
  print_separator
  tput bold
  echo "  ${blueColor}Options${blackColor}   |   ${blueColor}Description${blackColor}                 |   ${blueColor}Examples${noColor}"
  print_separator
  echo "     h${blackColor}      |   ${orangeColor}Print this Help.          ${blackColor}  |   ${greenColor}sh build_project.sh -h${noColor}"
  print_separator
  echo "     b${blackColor}      |   ${orangeColor}Build the modules.        ${blackColor}  |   ${greenColor}sh build_project.sh -b${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}                          ${blackColor}  |   ${greenColor}sh build_project.sh -b -m common${noColor}"
  print_separator
  echo "     t${blackColor}      |   ${orangeColor}Run tests for the modules.${blackColor}  |   ${greenColor}sh build_project.sh -t${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}                          ${blackColor}  |   ${greenColor}sh build_project.sh -bt -m tools${noColor}"
  print_separator
  echo "     v${blackColor}      |   ${orangeColor}Verbose mode on           ${blackColor}  |   ${greenColor}sh build_project.sh -t -v${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}                          ${blackColor}  |   ${greenColor}sh build_project.sh -bvt -m tools${noColor}"
  print_separator
  echo "     c${blackColor}      |   ${orangeColor}Test Coverage mode on     ${blackColor}  |   ${greenColor}sh build_project.sh -t -c${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}                          ${blackColor}  |   ${greenColor}sh build_project.sh -bct -m tools${noColor}"
  print_separator
  echo "     f${blackColor}      |   ${orangeColor}Flake8 validation mode on ${blackColor}  |   ${greenColor}sh build_project.sh -f${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}                          ${blackColor}  |   ${greenColor}sh build_project.sh -bft -m tools${noColor}"
  print_separator
  echo "     m${blackColor}      |   ${orangeColor}provide a list of modules.${blackColor}  |   ${greenColor}sh build_project.sh -bt -m common -m libs${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}Valid python modules:     ${blackColor}  |   ${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}  - common                ${blackColor}  |   ${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}  - libs                  ${blackColor}  |   ${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}  - platform              ${blackColor}  |   ${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}  - tools                 ${blackColor}  |   ${noColor}"
  echo "      ${blackColor}      |   ${orangeColor}  - dvp                   ${blackColor}  |   ${noColor}"
  print_separator
}

print_separator() {
  echo \
    "${blackColor}----------------------------------------------------------------------------------------------------${noColor}"
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
run_operations() {
  module_name=$1
  current_path="$PWD"
  module_path="$(get_project_path)/$module_name"
  cd "$module_path" || exit
  if [ "$should_build" = true ]; then
    echo
    print_as_per_screen_size " $module_name build starts " "${orangeColor}" ${equalFiller} "${screenSize}"
    build_module
    print_as_per_screen_size " $module_name build complete " "${greenColor}" ${equalFiller} "${screenSize}"
  fi
  if [ "$flake8" = true ]; then
    echo
    print_as_per_screen_size " $module_name Flake8 Main starts " "${orangeColor}" ${equalFiller} "${screenSize}"
    python -m flake8 "$module_path/src/test/python" --max-line-length 88
    print_as_per_screen_size " $module_name Flake8 Main complete " "${greenColor}" ${equalFiller} "${screenSize}"
    echo
    print_as_per_screen_size " $module_name Flake8 Test starts " "${orangeColor}" ${equalFiller} "${screenSize}"
    python -m flake8 "$module_path/src/main/python" --max-line-length 88
    print_as_per_screen_size " $module_name Flake8 Test complete " "${greenColor}" ${equalFiller} "${screenSize}"
  fi
  if [ "$should_test" = true ]; then
    echo
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
build_module() {
  python setup.py clean --all
  if [ "$verbose" = true ]; then
    pip install -r requirements.txt -v
    pip install -e . -v
  else
    pip install -r requirements.txt -q
    pip install -e . -q
  fi
}

# Test the module
test_module() {
  cmd=[]
  if [ "$coverage" = true ]; then
    cmd=( coverage run -m pytest )
  else
    cmd=( python -m pytest )
  fi
  if [ "$verbose" = true ]; then
    cmd=( ${cmd[@]} -v)
  fi
  cmd=( ${cmd[@]} src/test/python)
  echo "Test command is ${cmd[*]}"
  ${cmd[@]}
}

# Print the provided input in the center of screen by appending and prepending fillers.
print_as_per_screen_size() {
  columns=$4
  width="${#1}"
  adjust=$(((columns - width) / 2))
  printf "${3}%.0s" $(seq $adjust)
  printf "${2}%s${noColor}" "${1}"
  adjust=$((columns - (adjust + width)))
  printf "${3}%.0s" $(seq $adjust)
  printf "\n"
}

# Get the options
while getopts ":hbftvcm:" option; do
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
  c) # Coverage mode
    coverage=true ;;
  f) # Run flake8 mode
    flake8=true ;;
  \?) # Invalid options.
    echo "Error: Invalid option"
    Help
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

if [ "$should_build" = true ] || [ "$should_test" = true ] || [ "$flake8" = true ]; then
  if [ ${#multi[@]} -eq 0 ]; then
    multi=("${modules[@]}")
  fi

  paths=()
  current_path="$PWD"
  for module in "${multi[@]}"; do
    run_operations "$module"
    paths=( ${paths[@]} "${current_path}/${module}/.coverage")
  done

  if [ "$coverage" = true ]; then
    echo "Paths to combine for coverage are [${paths[*]}]."
    coverage combine ${paths[@]}
    coverage report -m -i
  fi
fi
