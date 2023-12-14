#!/usr/bin/env bash
set -euo pipefail
./build_language_container.sh

mkdir .build_output/exported_container -p
cp .build_output/cache/exports/exasol_sagemaker_extension_container-release-*.tar.gz .build_output/exported_container/exasol_sagemaker_extension_container.tar.gz
cp .build_output/cache/exports/exasol_sagemaker_extension_container-release-*.tar.gz.sha512sum .build_output/exported_container/exasol_sagemaker_extension_container.tar.gz.sha512sum
