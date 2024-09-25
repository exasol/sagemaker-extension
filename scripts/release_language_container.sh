#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$1"
echo "Building the language container in $1"
poetry run export_slc "$1"
