#!/bin/bash

# This script packages Lua modules into a single file and generates the CREATE SCRIPT
# statement sql by inserting the packaged module inside the sql script.



readonly script_dir=$(dirname "$(readlink -f "$0")")
readonly base_dir=$(readlink -f "$script_dir/..")

readonly lua_src_dir="$base_dir/lua/src"
readonly target_dir="$base_dir/target"
readonly bundled_sources_path="$target_dir/bundle_sources.lua"
readonly bundled_exaerror_path="$target_dir/bundle_exaerror.lua"
readonly bundled_final_path="$target_dir/bundle_final.lua"
readonly create_script_template_path="$base_dir/scripts/create_statement_exporting_template.sql"
readonly create_script_path="$target_dir/create_statement_exporting.sql"

mkdir -p "$target_dir"

if ! cd "$lua_src_dir"
then
  echo  "Lua src scripts path is not correct: " lua_src_dir
  exit  2
fi

function bundle_scripts {
  if amalg.lua -o "$bundled_sources_path" -s execute_exporter.lua aws_s3_handler  \
    && amalg.lua -o "$bundled_exaerror_path" -s "$bundled_sources_path" exaerror \
    && amalg.lua -o "$bundled_final_path" -s "$bundled_exaerror_path" message_expander
  then
    echo "Saved the packaged Lua module to " "$target_dir/main.lua"
    return 0
  else
    echo "Error: Lua modules couldn't be packaged"
    exit 2
  fi
}

function insert_bundle_into_sql_script {
  template_script=$(cat $create_script_template_path)
  bundled_script=$(cat $bundled_final_path)
  echo "${template_script/"BUNDLED_SCRIPT"/$bundled_script}" > $create_script_path

  echo "Generated create script sql to " $create_script_path
}

if bundle_scripts
then
  insert_bundle_into_sql_script
fi

exit 0