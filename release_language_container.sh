#!/usr/bin/env bash
set -euo pipefail

./build_language_container.sh

mkdir -p "$1"
echo "Copying container from .build_output/cache/exports to $1"
cp .build_output/cache/exports/exasol_sagemaker_extension_container-release-*.tar.gz "$1"/exasol_sagemaker_extension_container.tar.gz
cp .build_output/cache/exports/exasol_sagemaker_extension_container-release-*.tar.gz.sha512sum "$1"/exasol_sagemaker_extension_container.tar.gz.sha512sum
