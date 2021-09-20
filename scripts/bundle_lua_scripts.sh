#!/bin/bash

# This script packages Lua modules into a single file



readonly script_dir=$(dirname "$(readlink -f "$0")")
readonly base_dir=$(readlink -f "$script_dir/..")
readonly lua_src_dir="$base_dir/lua/src"
readonly target_dir="$base_dir/target"

mkdir -p "$target_dir"

if ! cd "$lua_src_dir"
then
  echo  "Lua src scripts path is not correct: " lua_src_dir
  exit  2
fi

if amalg.lua -o "$target_dir/main.lua" -s execute_exporter.lua aws_s3_handler
then
  echo "Saved the packaged Lua module to " "$target_dir/main.lua"
  exit 0
else
  exit 2
fi

