cmake_minimum_required(VERSION 3.16)

# Packaging helpers (deterministic staging + portable archives).
#
# This directory is only added when `DOMINIUM_ENABLE_PACKAGING=ON`.
# Packaging must not change runtime behavior; it only stages already-built binaries/data.

set(DOMINIUM_DIST_DIR "${CMAKE_BINARY_DIR}/dist/stage" CACHE PATH "Staging directory for portable packages (bundle root)")
set(DOMINIUM_PACKAGE_DIR "${CMAKE_BINARY_DIR}/dist/packages" CACHE PATH "Output directory for portable packages")
set(DOMINIUM_PACKAGE_VERSION "${DOM_BUILD_ID}" CACHE STRING "Version string used in portable package names and repo/products/<version> layout")

if(DOMINIUM_PACKAGE_VERSION STREQUAL "" OR DOMINIUM_PACKAGE_VERSION STREQUAL "unknown")
    set(DOMINIUM_PACKAGE_VERSION "0.0.0" CACHE STRING "Version string used in portable package names and repo/products/<version> layout" FORCE)
endif()

find_program(DOMINIUM_PYTHON NAMES python3 python)
if(NOT DOMINIUM_PYTHON)
    message(WARNING "python not found; packaging helper targets disabled")
    return()
endif()

set(_dom_conf_bin_dir "${CMAKE_BINARY_DIR}/dist/_configured/bin")
file(MAKE_DIRECTORY "${_dom_conf_bin_dir}")

if(WIN32)
    set(DOM_LAUNCHER_BINARY "dominium-launcher.exe")
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/scripts/dominium.cmd.in"
        "${_dom_conf_bin_dir}/dominium.cmd"
        @ONLY
    )
else()
    set(DOM_LAUNCHER_BINARY "dominium-launcher")
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/scripts/dominium.sh.in"
        "${_dom_conf_bin_dir}/dominium"
        @ONLY
    )
    file(CHMOD "${_dom_conf_bin_dir}/dominium"
        PERMISSIONS
            OWNER_READ OWNER_WRITE OWNER_EXECUTE
            GROUP_READ GROUP_EXECUTE
            WORLD_READ WORLD_EXECUTE)
endif()

set(DOMINIUM_DIST_STAMP "${DOMINIUM_DIST_DIR}/.stage_stamp")
add_custom_command(
    OUTPUT "${DOMINIUM_DIST_STAMP}"
    COMMAND "${CMAKE_COMMAND}"
        -DSTAGE_DIR="${DOMINIUM_DIST_DIR}"
        -DVERSION="${DOMINIUM_PACKAGE_VERSION}"
        -DLAUNCHER_BIN="$<TARGET_FILE:dominium-launcher>"
        -DGAME_BIN="$<TARGET_FILE:dominium_game>"
        -DSETUP_BIN="$<TARGET_FILE:dominium-setup>"
        -DCONFIGURED_BIN_DIR="${_dom_conf_bin_dir}"
        -DSOURCE_DIR="${CMAKE_SOURCE_DIR}"
        -P "${CMAKE_CURRENT_SOURCE_DIR}/stage_dist.cmake"
    DEPENDS
        dominium-launcher
        dominium_game
        dominium-setup
        "${CMAKE_CURRENT_SOURCE_DIR}/stage_dist.cmake"
        "${CMAKE_CURRENT_SOURCE_DIR}/scripts/dominium.cmd.in"
        "${CMAKE_CURRENT_SOURCE_DIR}/scripts/dominium.sh.in"
    COMMENT "Staging Dominium portable dist into ${DOMINIUM_DIST_DIR}"
    VERBATIM
)

add_custom_target(dominium_stage_dist
    DEPENDS "${DOMINIUM_DIST_STAMP}"
)

file(MAKE_DIRECTORY "${DOMINIUM_PACKAGE_DIR}")

set(_package_root_name "Dominium-${DOMINIUM_PACKAGE_VERSION}")

if(WIN32)
    set(_portable_zip "${DOMINIUM_PACKAGE_DIR}/${_package_root_name}-portable-win32.zip")
    add_custom_command(
        OUTPUT "${_portable_zip}"
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_PACKAGE_DIR}"
        COMMAND "${DOMINIUM_PYTHON}" "${CMAKE_CURRENT_SOURCE_DIR}/make_deterministic_archive.py"
            --format zip
            --input "${DOMINIUM_DIST_DIR}"
            --output "${_portable_zip}"
            --root-name "${_package_root_name}"
        DEPENDS "${DOMINIUM_DIST_STAMP}" "${CMAKE_CURRENT_SOURCE_DIR}/make_deterministic_archive.py"
        COMMENT "Building portable ZIP: ${_portable_zip}"
        VERBATIM
    )
    add_custom_target(dominium_portable_zip DEPENDS "${_portable_zip}")
endif()

if(UNIX AND NOT APPLE)
    set(_portable_tgz "${DOMINIUM_PACKAGE_DIR}/${_package_root_name}-portable-linux.tar.gz")
    add_custom_command(
        OUTPUT "${_portable_tgz}"
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_PACKAGE_DIR}"
        COMMAND "${DOMINIUM_PYTHON}" "${CMAKE_CURRENT_SOURCE_DIR}/make_deterministic_archive.py"
            --format tar.gz
            --input "${DOMINIUM_DIST_DIR}"
            --output "${_portable_tgz}"
            --root-name "${_package_root_name}"
        DEPENDS "${DOMINIUM_DIST_STAMP}" "${CMAKE_CURRENT_SOURCE_DIR}/make_deterministic_archive.py"
        COMMENT "Building portable tarball: ${_portable_tgz}"
        VERBATIM
    )
    add_custom_target(dominium_portable_tgz DEPENDS "${_portable_tgz}")
endif()

if(APPLE)
    # Portable tarball for macOS (app bundle creation handled in macos/).
    set(_portable_tgz "${DOMINIUM_PACKAGE_DIR}/${_package_root_name}-portable-macos.tar.gz")
    add_custom_command(
        OUTPUT "${_portable_tgz}"
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_PACKAGE_DIR}"
        COMMAND "${DOMINIUM_PYTHON}" "${CMAKE_CURRENT_SOURCE_DIR}/make_deterministic_archive.py"
            --format tar.gz
            --input "${DOMINIUM_DIST_DIR}"
            --output "${_portable_tgz}"
            --root-name "${_package_root_name}"
        DEPENDS "${DOMINIUM_DIST_STAMP}" "${CMAKE_CURRENT_SOURCE_DIR}/make_deterministic_archive.py"
        COMMENT "Building portable tarball: ${_portable_tgz}"
        VERBATIM
    )
    add_custom_target(dominium_portable_tgz DEPENDS "${_portable_tgz}")
endif()

# Platform-specific installers/bundles (optional; do not affect portability targets).
if(WIN32)
    add_subdirectory(windows)
endif()
if(APPLE)
    add_subdirectory(macos)
endif()
if(UNIX AND NOT APPLE)
    add_subdirectory(linux)
endif()

