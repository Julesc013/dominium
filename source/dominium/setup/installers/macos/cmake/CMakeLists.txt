cmake_minimum_required(VERSION 3.16)

if(NOT APPLE)
    return()
endif()

set(DSU_MACOS_INSTALLER_COMMON_SRC
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/args_parse.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/invocation_builder.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/ui_flow.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/tui.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/bridge_core.c
    ${CMAKE_CURRENT_LIST_DIR}/../common/src/log_forward.c
)

add_library(dsu_macos_installer_common STATIC
    ${DSU_MACOS_INSTALLER_COMMON_SRC}
)
target_include_directories(dsu_macos_installer_common PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/../common/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/include
    ${PROJECT_SOURCE_DIR}/include
)
target_link_libraries(dsu_macos_installer_common
    PRIVATE
        dsu_core
)
set_target_properties(dsu_macos_installer_common PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(dominium-setup-tui
    ${CMAKE_CURRENT_LIST_DIR}/../tui/dominium-setup-tui-macos.c
)
target_include_directories(dominium-setup-tui PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/../common/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/include
    ${PROJECT_SOURCE_DIR}/include
)
target_link_libraries(dominium-setup-tui
    PRIVATE
        dsu_macos_installer_common
        dsu_core
)
set_target_properties(dominium-setup-tui PROPERTIES
    OUTPUT_NAME "dominium-setup-tui"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
dominium_bundle_runtime(dominium-setup-tui)

add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/../gui/macos_gui_app
    ${CMAKE_CURRENT_BINARY_DIR}/macos_gui_app)

if(NOT DOMINIUM_ENABLE_PACKAGING)
    return()
endif()

find_program(DOMINIUM_PYTHON NAMES python3 python)
find_program(DOMINIUM_SH NAMES sh bash)
find_program(DOMINIUM_PKGBUILD NAMES pkgbuild)
find_program(DOMINIUM_PRODUCTBUILD NAMES productbuild)
find_program(DOMINIUM_HDIUTIL NAMES hdiutil)
if(NOT DOMINIUM_PYTHON)
    message(WARNING "python not found; macOS packaging targets disabled")
    return()
endif()

set(DSU_MACOS_PACKAGING_ROOT "${CMAKE_CURRENT_LIST_DIR}/../packaging")
set(DSU_MACOS_ARTIFACT_ROOT "${CMAKE_BINARY_DIR}/dist/macos/artifact_root")
set(DSU_MACOS_OUT_DIR "${CMAKE_BINARY_DIR}/dist/macos")

string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" _dsu_cpu)
if(_dsu_cpu MATCHES "^(arm64|aarch64)$")
    set(DSU_MACOS_ARCH "arm64")
    set(DSU_MACOS_PLATFORM "macos-arm64")
elseif(_dsu_cpu MATCHES "^(x86_64|amd64)$")
    set(DSU_MACOS_ARCH "x64")
    set(DSU_MACOS_PLATFORM "macos-x64")
else()
    set(DSU_MACOS_ARCH "${CMAKE_SYSTEM_PROCESSOR}")
    set(DSU_MACOS_PLATFORM "macos-x64")
endif()

set(DSU_MACOS_VERSION "${DOM_PROJECT_SEMVER}")
if(NOT DSU_MACOS_VERSION)
    set(DSU_MACOS_VERSION "0.0.0")
endif()

set(_dsu_manifest_template "${CMAKE_SOURCE_DIR}/assets/setup/manifests/product.template.json")
set(_dsu_pipeline "${CMAKE_SOURCE_DIR}/scripts/packaging/pipeline.py")
set(_dsu_artifact_stamp "${DSU_MACOS_ARTIFACT_ROOT}/.artifact_stamp")
set(_dsu_dry_root "${DSU_MACOS_ARTIFACT_ROOT}/_dry_run")

add_custom_command(
    OUTPUT "${_dsu_artifact_stamp}"
    COMMAND "${CMAKE_COMMAND}" -E rm -rf "${DSU_MACOS_ARTIFACT_ROOT}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${DSU_MACOS_ARTIFACT_ROOT}"
    COMMAND "${DOMINIUM_PYTHON}" "${_dsu_pipeline}"
        assemble
        --build-dir "${CMAKE_BINARY_DIR}"
        --out "${DSU_MACOS_ARTIFACT_ROOT}"
        --version "${DSU_MACOS_VERSION}"
        --manifest-template "${_dsu_manifest_template}"
    COMMAND "${CMAKE_COMMAND}" -E rm -rf "${_dsu_dry_root}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${_dsu_dry_root}/install_root"
    COMMAND "${CMAKE_COMMAND}" -E chdir "${DSU_MACOS_ARTIFACT_ROOT}"
        "${DSU_MACOS_ARTIFACT_ROOT}/setup/dominium-setup"
        --deterministic 1
        export-invocation
        --manifest "setup/manifests/product.dsumanifest"
        --op install
        --scope portable
        --platform "${DSU_MACOS_PLATFORM}"
        --install-root "${_dsu_dry_root}/install_root"
        --ui-mode cli
        --frontend-id macos-cmake
        --out "${_dsu_dry_root}/invocation.dsuinv"
    COMMAND "${CMAKE_COMMAND}" -E chdir "${DSU_MACOS_ARTIFACT_ROOT}"
        "${DSU_MACOS_ARTIFACT_ROOT}/setup/dominium-setup"
        --deterministic 1
        plan
        --manifest "setup/manifests/product.dsumanifest"
        --invocation "${_dsu_dry_root}/invocation.dsuinv"
        --out "${_dsu_dry_root}/plan.dsuplan"
    COMMAND "${CMAKE_COMMAND}" -E chdir "${DSU_MACOS_ARTIFACT_ROOT}"
        "${DSU_MACOS_ARTIFACT_ROOT}/setup/dominium-setup"
        --deterministic 1
        apply
        --plan "${_dsu_dry_root}/plan.dsuplan"
        --dry-run
    COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_artifact_stamp}"
    DEPENDS
        dominium-setup
        dominium-setup-tui
        dominium-setup-gui
        dominium-setup-macos
        dominium-launcher
        dominium_game
        "${_dsu_pipeline}"
        "${_dsu_manifest_template}"
    COMMENT "Assembling macOS artifact_root"
    VERBATIM
)

add_custom_target(macos_artifact_${DSU_MACOS_ARCH}
    DEPENDS "${_dsu_artifact_stamp}"
)

set(_dsu_pkg_stamp "${DSU_MACOS_OUT_DIR}/.pkg_${DSU_MACOS_ARCH}.stamp")
if(DOMINIUM_SH AND DOMINIUM_PKGBUILD AND DOMINIUM_PRODUCTBUILD)
    add_custom_command(
        OUTPUT "${_dsu_pkg_stamp}"
        COMMAND "${DOMINIUM_SH}" "${DSU_MACOS_PACKAGING_ROOT}/pkg/scripts/build_pkg.sh"
            --artifact-root "${DSU_MACOS_ARTIFACT_ROOT}"
            --out "${DSU_MACOS_OUT_DIR}"
            --version "${DSU_MACOS_VERSION}"
            --identifier "com.dominium.setup"
            --platform "${DSU_MACOS_PLATFORM}"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_pkg_stamp}"
        DEPENDS
            "${_dsu_artifact_stamp}"
            "${DSU_MACOS_PACKAGING_ROOT}/pkg/scripts/build_pkg.sh"
            "${DSU_MACOS_PACKAGING_ROOT}/pkg/scripts/postinstall"
            "${DSU_MACOS_PACKAGING_ROOT}/pkg/Distribution.xml"
        COMMENT "Building macOS PKG"
        VERBATIM
    )
else()
    add_custom_command(
        OUTPUT "${_dsu_pkg_stamp}"
        COMMAND "${CMAKE_COMMAND}" -E echo "pkg build skipped (missing pkgbuild/productbuild or sh)"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_pkg_stamp}"
    )
endif()

add_custom_target(package-macos-pkg
    DEPENDS "${_dsu_pkg_stamp}"
)

set(_dsu_dmg_stamp "${DSU_MACOS_OUT_DIR}/.dmg_${DSU_MACOS_ARCH}.stamp")
if(DOMINIUM_SH AND DOMINIUM_HDIUTIL)
    add_custom_command(
        OUTPUT "${_dsu_dmg_stamp}"
        COMMAND "${DOMINIUM_SH}" "${DSU_MACOS_PACKAGING_ROOT}/dmg/build_dmg.sh"
            --artifact-root "${DSU_MACOS_ARTIFACT_ROOT}"
            --out "${DSU_MACOS_OUT_DIR}"
            --version "${DSU_MACOS_VERSION}"
            --pkg "${DSU_MACOS_OUT_DIR}/DominiumSetup-${DSU_MACOS_VERSION}.pkg"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_dmg_stamp}"
        DEPENDS
            "${_dsu_artifact_stamp}"
            "${_dsu_pkg_stamp}"
            "${DSU_MACOS_PACKAGING_ROOT}/dmg/build_dmg.sh"
        COMMENT "Building macOS DMG"
        VERBATIM
    )
else()
    add_custom_command(
        OUTPUT "${_dsu_dmg_stamp}"
        COMMAND "${CMAKE_COMMAND}" -E echo "dmg build skipped (missing hdiutil or sh)"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_dsu_dmg_stamp}"
    )
endif()

add_custom_target(package-macos-dmg
    DEPENDS "${_dsu_dmg_stamp}"
)

add_custom_target(package-macos)
add_dependencies(package-macos package-macos-pkg package-macos-dmg)
