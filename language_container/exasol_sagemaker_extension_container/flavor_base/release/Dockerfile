FROM exasol/script-language-container:python-3.8-minimal-EXASOL-6.2.0-release_Y5KJTLX3TPPOSDA2SQMX6QGAAMY5BG5SFY2MMXLMQ5RM6T53UFTA

COPY release/dist /project
RUN pip install /project/*.whl


RUN mkdir -p /build_info/actual_installed_packages/release && \
    /scripts/list_installed_scripts/list_installed_apt.sh > /build_info/actual_installed_packages/release/apt_get_packages && \
    /scripts/list_installed_scripts/list_installed_pip.sh python3.8 > /build_info/actual_installed_packages/release/python3_pip_packages
