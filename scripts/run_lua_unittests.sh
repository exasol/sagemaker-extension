#!/bin/bash

# This scripts run all Lua scripts implemented in lua/test directory


readonly script_dir=$(dirname "$(readlink -f "$0")")
readonly base_dir=$(readlink -f "$script_dir/..")
readonly lua_dir="$base_dir/exasol_sagemaker_extension/lua"

if ! cd "$lua_dir"
then
  echo  "Lua scripts path is not correct: " $lua_dir
  exit  2
fi



n_test=0
n_success=0
n_fail=0
readonly test_module_path="$lua_dir/test"
readonly src_module_path="$lua_dir/src"
readonly tests="$(find "$test_module_path" -name '*.lua')"
for unittest in $tests
do
    ((n_test+=1))
    if LUA_PATH="$src_module_path/?.lua;$(luarocks path --lr-path)"  lua  "$unittest" -v
    then
        ((n_success+=1))
    else
        ((n_fail+=1))
    fi
    echo ""
done

echo -n "Ran $n_test tests, $n_success successes, $n_fail failures"
exit 0