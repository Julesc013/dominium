cmake_minimum_required(VERSION 3.16)

if(NOT UNIX OR APPLE)
    return()
endif()

set(DSU_LINUX_INSTALLER_COMMON_SRC
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/args_parse.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/invocation_builder.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/ui_flow.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/tui.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/bridge_core.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/log_forward.c
)

add_library(dsu_linux_installer_common STATIC
    ${DSU_LINUX_INSTALLER_COMMON_SRC}
)
target_include_directories(dsu_linux_installer_common PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/../common/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/include
    ${PROJECT_SOURCE_DIR}/include
)
target_link_libraries(dsu_linux_installer_common
    PRIVATE
        setup_kernel
        setup_services_impl_platform
)
set_target_properties(dsu_linux_installer_common PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(dominium-setup-tui
    ${CMAKE_CURRENT_LIST_DIR}/../tui/dominium-setup-tui.c
)
target_include_directories(dominium-setup-tui PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/../common/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/include
    ${PROJECT_SOURCE_DIR}/include
)
target_link_libraries(dominium-setup-tui
    PRIVATE
        dsu_linux_installer_common
        setup_kernel
        setup_services_impl_platform
)
set_target_properties(dominium-setup-tui PROPERTIES
    OUTPUT_NAME "dominium-setup-tui"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
dominium_bundle_runtime(dominium-setup-tui)

add_executable(dominium-setup-gui
    ${CMAKE_CURRENT_LIST_DIR}/../gui/dominium-setup-gui.c
)
target_include_directories(dominium-setup-gui PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/../common/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/include
    ${PROJECT_SOURCE_DIR}/include
)
target_link_libraries(dominium-setup-gui
    PRIVATE
        dsu_linux_installer_common
        setup_kernel
        setup_services_impl_platform
)
set_target_properties(dominium-setup-gui PROPERTIES
    OUTPUT_NAME "dominium-setup-gui"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
dominium_bundle_runtime(dominium-setup-gui)

if(NOT DOMINIUM_ENABLE_PACKAGING)
    return()
endif()

find_program(DOMINIUM_PYTHON NAMES python3 python)
find_program(DOMINIUM_SH NAMES sh bash)
find_program(DOMINIUM_DPKG_DEB NAMES dpkg-deb)
find_program(DOMINIUM_RPMBUILD NAMES rpmbuild)
if(NOT DOMINIUM_PYTHON)
    message(WARNING "python not found; linux packaging targets disabled")
    return()
endif()

set(DSU_LINUX_PACKAGING_ROOT "${CMAKE_CURRENT_LIST_DIR}/../packaging")
set(DSU_LINUX_ARTIFACT_ROOT "${CMAKE_BINARY_DIR}/dist/linux/artifact_root")
set(DSU_LINUX_OUT_DIR "${CMAKE_BINARY_DIR}/dist/linux")

string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" _dsu_cpu)
if(_dsu_cpu MATCHES "^(amd64|x86_64)$")
    set(DSU_LINUX_ARCH "x64")
    set(DSU_LINUX_DEB_ARCH "amd64")
    set(DSU_LINUX_RPM_ARCH "x86_64")
elseif(_dsu_cpu MATCHES "^(aarch64|arm64)$")
    set(DSU_LINUX_ARCH "arm64")
    set(DSU_LINUX_DEB_ARCH "arm64")
    set(DSU_LINUX_RPM_ARCH "aarch64")
elseif(_dsu_cpu MATCHES "i[3-6]86")
    set(DSU_LINUX_ARCH "x86")
    set(DSU_LINUX_DEB_ARCH "i386")
    set(DSU_LINUX_RPM_ARCH "i686")
else()
    set(DSU_LINUX_ARCH "${CMAKE_SYSTEM_PROCESSOR}")
    set(DSU_LINUX_DEB_ARCH "${CMAKE_SYSTEM_PROCESSOR}")
    set(DSU_LINUX_RPM_ARCH "${CMAKE_SYSTEM_PROCESSOR}")
endif()

set(DSU_LINUX_VERSION "${DOM_PROJECT_SEMVER}")
if(NOT DSU_LINUX_VERSION)
    set(DSU_LINUX_VERSION "0.0.0")
endif()

set(_dsu_manifest_template "${CMAKE_SOURCE_DIR}/assets/setup/manifests/product.template.json")
set(_dsu_pipeline "${CMAKE_SOURCE_DIR}/scripts/packaging/pipeline.py")
set(_dsu_artifact_stamp "${DSU_LINUX_ARTIFACT_ROOT}/.artifact_stamp")
set(_dsu_dry_root "${DSU_LINUX_ARTIFACT_ROOT}/_dry_run")

add_custom_command(
    OUTPUT "${_dsu_artifact_stamp}"
    COMMAND "${CMAKE_COMMAND}" -E rm -rf "${DSU_LINUX_ARTIFACT_ROOT}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${DSU_LINUX_ARTIFACT_ROOT}"
    COMMAND "${DOMINIUM_PYTHON}" "${_dsu_pipeline}"
        assemble
        --build-dir "${CMAKE_BINARY_DIR}"
        --out "${DSU_LINUX_ARTIFACT_ROOT}"
        --version "${DSU_LINUX_VERSION}"
        --manifest-template "${_dsu_manifest_template}"
    COMMAND "${CMAKE_COMMAND}" -E rm -rf "${_dsu_dry_root}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${_dsu_dry_root}/install_root"
    COMMAND "${CMAKE_COMMAND}" -E chdir "${DSU_LINUX_ARTIFACT_ROOT}"
        "${DSU_LINUX_ARTIFACT_ROOT}/setup/dominium-setup"
        --deterministic 1
        export-invocation
        --manifest "setup/manifests/product.dsumanifest"
        --op install
        --scope portable
        --install-root "${_dsu_dry_root}/install_root"
        --ui-mode cli
        --frontend-id linux-cmake
        --out "${_dsu_dry_root}/invocation.dsuinv"
    COMMAND "${CMAKE_COMMAND}" -E chdir "${DSU_LINUX_ARTIFACT_ROOT}"
        "${DSU_LINUX_ARTIFACT_ROOT}/setup/dominium-setup"
        --deterministic 1
        plan
        --manifest "setup/manifests/product.dsumanifest"
        --invocation "${_dsu_dry_root}/invocation.dsuinv"
        --out "${_dsu_dry_root}/plan.dsuplan"
    COMMAND "${CMAKE_COMMAND}" -E chdir "${DSU_LINUX_ARTIFACT_ROOT}"
        "${DSU_LINUX_ARTIFACT_ROOT}/setup/dominium-setup"
        --deterministic 1
        apply
        --plan "${_dsu_dry_root}/plan.dsuplan"
        --dry-run
    COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_artifact_stamp}"
    DEPENDS
        dominium-setup
        dominium-setup-tui
        dominium-setup-gui
        dominium-setup-linux
        dominium-launcher
        dominium_game
        "${_dsu_pipeline}"
        "${_dsu_manifest_template}"
    COMMENT "Assembling Linux artifact_root"
    VERBATIM
)

add_custom_target(linux_artifact_${DSU_LINUX_ARCH}
    DEPENDS "${_dsu_artifact_stamp}"
)

set(_dsu_tarball_stamp "${DSU_LINUX_OUT_DIR}/.tarball_${DSU_LINUX_ARCH}.stamp")
add_custom_command(
    OUTPUT "${_dsu_tarball_stamp}"
    COMMAND "${CMAKE_COMMAND}"
        -DARTIFACT_ROOT="${DSU_LINUX_ARTIFACT_ROOT}"
        -DOUT_DIR="${DSU_LINUX_OUT_DIR}"
        -DVERSION="${DSU_LINUX_VERSION}"
        -DARCH="${DSU_LINUX_ARCH}"
        -DREPO_ROOT="${CMAKE_SOURCE_DIR}"
        -DPYTHON_EXECUTABLE="${DOMINIUM_PYTHON}"
        -P "${DSU_LINUX_PACKAGING_ROOT}/tarball/build_tarball.cmake"
    COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_tarball_stamp}"
    DEPENDS
        "${_dsu_artifact_stamp}"
        "${DSU_LINUX_PACKAGING_ROOT}/tarball/build_tarball.cmake"
    COMMENT "Building Linux tarball"
    VERBATIM
)

add_custom_target(linux_tarball_${DSU_LINUX_ARCH}
    DEPENDS "${_dsu_tarball_stamp}"
)

set(_dsu_deb_stamp "${DSU_LINUX_OUT_DIR}/.deb_${DSU_LINUX_ARCH}.stamp")
if(DOMINIUM_SH AND DOMINIUM_DPKG_DEB)
    add_custom_command(
        OUTPUT "${_dsu_deb_stamp}"
        COMMAND "${DOMINIUM_SH}" "${DSU_LINUX_PACKAGING_ROOT}/deb/build_deb.sh"
            --artifact-root "${DSU_LINUX_ARTIFACT_ROOT}"
            --out "${DSU_LINUX_OUT_DIR}"
            --version "${DSU_LINUX_VERSION}"
            --arch "${DSU_LINUX_DEB_ARCH}"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_deb_stamp}"
        DEPENDS
            "${_dsu_artifact_stamp}"
            "${DSU_LINUX_PACKAGING_ROOT}/deb/build_deb.sh"
            "${DSU_LINUX_PACKAGING_ROOT}/deb/debian/control"
            "${DSU_LINUX_PACKAGING_ROOT}/deb/debian/postinst"
            "${DSU_LINUX_PACKAGING_ROOT}/deb/debian/prerm"
            "${DSU_LINUX_PACKAGING_ROOT}/deb/debian/postrm"
        COMMENT "Building Linux deb"
        VERBATIM
    )
else()
    add_custom_command(
        OUTPUT "${_dsu_deb_stamp}"
        COMMAND "${CMAKE_COMMAND}" -E echo "deb build skipped (missing sh or dpkg-deb)"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_deb_stamp}"
    )
endif()

add_custom_target(linux_deb_${DSU_LINUX_ARCH}
    DEPENDS "${_dsu_deb_stamp}"
)

set(_dsu_rpm_stamp "${DSU_LINUX_OUT_DIR}/.rpm_${DSU_LINUX_ARCH}.stamp")
if(DOMINIUM_SH AND DOMINIUM_RPMBUILD)
    add_custom_command(
        OUTPUT "${_dsu_rpm_stamp}"
        COMMAND "${DOMINIUM_SH}" "${DSU_LINUX_PACKAGING_ROOT}/rpm/build_rpm.sh"
            --artifact-root "${DSU_LINUX_ARTIFACT_ROOT}"
            --out "${DSU_LINUX_OUT_DIR}"
            --version "${DSU_LINUX_VERSION}"
            --arch "${DSU_LINUX_RPM_ARCH}"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_rpm_stamp}"
        DEPENDS
            "${_dsu_artifact_stamp}"
            "${DSU_LINUX_PACKAGING_ROOT}/rpm/build_rpm.sh"
            "${DSU_LINUX_PACKAGING_ROOT}/rpm/dominium.spec"
        COMMENT "Building Linux rpm"
        VERBATIM
    )
else()
    add_custom_command(
        OUTPUT "${_dsu_rpm_stamp}"
        COMMAND "${CMAKE_COMMAND}" -E echo "rpm build skipped (missing sh or rpmbuild)"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_rpm_stamp}"
    )
endif()

add_custom_target(linux_rpm_${DSU_LINUX_ARCH}
    DEPENDS "${_dsu_rpm_stamp}"
)

add_custom_target(package-linux)
add_dependencies(package-linux
    linux_tarball_${DSU_LINUX_ARCH}
)
if(DOMINIUM_SH AND DOMINIUM_DPKG_DEB)
    add_dependencies(package-linux linux_deb_${DSU_LINUX_ARCH})
endif()
if(DOMINIUM_SH AND DOMINIUM_RPMBUILD)
    add_dependencies(package-linux linux_rpm_${DSU_LINUX_ARCH})
endif()
