#!/bin/bash

# This script finds and runs Lua unit tests, collects coverage and runs static code analysis.

readonly script_dir=$(dirname "$(readlink -f "$0")")
if [[ -v $1 ]]
then
    readonly base_dir="$1"
else
    readonly base_dir=$(readlink -f "$script_dir/..")
fi

readonly exit_ok=0
readonly exit_software=2
readonly src_module_path="$base_dir/exasol_sagemaker_extension/lua/src"
readonly test_module_path="$base_dir/exasol_sagemaker_extension/lua/test"
readonly target_dir="$base_dir/target"
readonly reports_dir="$target_dir/luaunit-reports"
readonly luacov_dir="$target_dir/luacov-reports"

function create_target_directories {
    mkdir -p "$reports_dir"
    mkdir -p "$luacov_dir"
}

##
# Run the unit tests and collect code coverage.
#
# Return error status in case there were failures.
#
function run_tests {
    cd "$test_module_path" || exit
    readonly tests="$(find . -name '*.lua')"
    test_suites=0
    failures=0
    successes=0
    for testcase in $tests
    do
        ((test_suites++))

        if LUA_PATH="$src_module_path/?.lua;$(luarocks path --lr-path)" \
            lua -lluacov "$testcase" -o junit -n "$reports_dir/$testcase"
        then
            ((successes++))
        else
            ((failures++))
        fi
        echo
    done
    echo -n "Ran $test_suites test suites. $successes successes, "
    if [[ "$failures" -eq 0 ]]
    then
        echo -e "\e[1m\e[32m$failures failures\e[0m."
        return "$exit_ok"
    else
        echo -e "\e[1m\e[31m$failures failures\e[0m."
        return "$exit_software"
    fi
}

##
# Collect the coverage results into a single file.
#
# Return exit status of coverage collector.
#
function collect_coverage_results {
    echo
    echo "Collecting code coverage results"
    luacov
    return "$?"
}

##
# Move the coverage results into the target directory.
#
# Return exit status of `mv` command.
#
function move_coverage_results {
    echo "Moving coverage results to $luacov_dir"
    mv "$test_module_path"/luacov.*.out "$luacov_dir"
    return "$?"
}

##
# Print the summary section of the code coverage report to the console
#
function print_coverage_summary {
    echo
    grep --after 500 'File\s*Hits' "$luacov_dir/luacov.report.out"
}

##
# Analyze the Lua code with "luacheck".
#
# Return exit status of code coverage.
#
function run_static_code_analysis {
    echo
    echo "Running static code analysis"
    echo
    luacheck "$src_module_path" "$test_module_path" --codes \
      --ignore 111 --ignore 112  --ignore 113 --ignore 142
    return "$?"
}

create_target_directories
run_tests \
&& collect_coverage_results \
&& move_coverage_results \
&& print_coverage_summary \
&& run_static_code_analysis \
|| exit "$exit_software"

exit "$exit_ok"