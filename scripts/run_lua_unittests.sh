#!/bin/bash

# This scripts run all Lua scripts implemented in lua/test directory


readonly script_dir=$(dirname "$(readlink -f "$0")")
readonly base_dir=$(readlink -f "$script_dir/..")
readonly lua_path="$base_dir/lua"


if ! cd "$lua_path"
then
  echo  "Lua scripts path is not correct: " $lua_path
  exit  2
fi

n_test=0
n_success=0
n_fail=0
readonly tests="$(find './test/' -name '*.lua')"
for unittest in $tests
do
    ((n_test+=1))
    if  lua  "$unittest" -v
    then
        ((n_success+=1))
    else
        ((n_fail+=1))
    fi
    echo
done

echo -n "Ran $n_test tests, $n_success successes, $n_fail failures"
echo ""