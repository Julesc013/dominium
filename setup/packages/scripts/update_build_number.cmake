#
# update_build_number.cmake
#
# Increments the repository-wide build number and emits a generated header
# plus a plain-text file for other tooling. This script is intended to be
# invoked from CMake via:
#   cmake -DSTATE_FILE=<path> -DHEADER_FILE=<path> -DNUMBER_FILE=<path> \
#         -DPROJECT_SEMVER=<semver> -P scripts/update_build_number.cmake
# Set -DDOM_BUILD_NUMBER_BUMP=1 to increment; defaults to no increment.
#

if(NOT DEFINED STATE_FILE)
    message(FATAL_ERROR "STATE_FILE is required")
endif()

if(NOT DEFINED HEADER_FILE)
    message(FATAL_ERROR "HEADER_FILE is required")
endif()

if(NOT DEFINED NUMBER_FILE)
    set(NUMBER_FILE "")
endif()

if(NOT DEFINED PROJECT_SEMVER)
    set(PROJECT_SEMVER "0.0.0")
endif()

if(NOT DEFINED DOM_BUILD_NUMBER_BUMP)
    set(DOM_BUILD_NUMBER_BUMP "0")
endif()
string(TOLOWER "${DOM_BUILD_NUMBER_BUMP}" _dom_build_bump_lc)
set(_dom_do_bump 1)
if(_dom_build_bump_lc STREQUAL "" OR _dom_build_bump_lc STREQUAL "0" OR
   _dom_build_bump_lc STREQUAL "off" OR _dom_build_bump_lc STREQUAL "false")
    set(_dom_do_bump 0)
endif()

# ---------------------------------------------------------------------------
# Load and increment the persistent build number
# ---------------------------------------------------------------------------
set(_current 0)
if(EXISTS "${STATE_FILE}")
    file(READ "${STATE_FILE}" _raw_state)
    string(REGEX MATCH "^[0-9]+" _state_match "${_raw_state}")
    if(NOT _state_match STREQUAL "")
        set(_current "${_state_match}")
    endif()
endif()

if(_dom_do_bump)
    math(EXPR BUILD_NUMBER "${_current} + 1")
    # Persist the new build number immediately to avoid reuse on concurrent targets
    file(WRITE "${STATE_FILE}" "${BUILD_NUMBER}\n")
else()
    set(BUILD_NUMBER "${_current}")
    if(NOT EXISTS "${STATE_FILE}")
        file(WRITE "${STATE_FILE}" "${BUILD_NUMBER}\n")
    endif()
endif()

# ---------------------------------------------------------------------------
# Parse semantic version parts (fall back to 0 if missing)
# ---------------------------------------------------------------------------
string(REPLACE "." ";" _semver_parts "${PROJECT_SEMVER}")
set(DOM_SEMVER_MAJOR 0)
set(DOM_SEMVER_MINOR 0)
set(DOM_SEMVER_PATCH 0)

list(LENGTH _semver_parts _semver_len)
if(_semver_len GREATER 0)
    list(GET _semver_parts 0 DOM_SEMVER_MAJOR)
endif()
if(_semver_len GREATER 1)
    list(GET _semver_parts 1 DOM_SEMVER_MINOR)
endif()
if(_semver_len GREATER 2)
    list(GET _semver_parts 2 DOM_SEMVER_PATCH)
endif()

set(DOM_VERSION_BUILD "${PROJECT_SEMVER}+build.${BUILD_NUMBER}")

# ---------------------------------------------------------------------------
# Emit generated header and plain-text build number
# ---------------------------------------------------------------------------
get_filename_component(_header_dir "${HEADER_FILE}" DIRECTORY)
if(NOT _header_dir STREQUAL "")
    file(MAKE_DIRECTORY "${_header_dir}")
endif()

set(_header_contents "/* Auto-generated: do not edit manually. */
#pragma once
#define DOM_VERSION_MAJOR ${DOM_SEMVER_MAJOR}
#define DOM_VERSION_MINOR ${DOM_SEMVER_MINOR}
#define DOM_VERSION_PATCH ${DOM_SEMVER_PATCH}
#define DOM_BUILD_NUMBER ${BUILD_NUMBER}
#define DOM_VERSION_SEMVER \"${PROJECT_SEMVER}\"
#define DOM_VERSION_BUILD_STR \"${DOM_VERSION_BUILD}\"
")

file(WRITE "${HEADER_FILE}" "${_header_contents}")

if(NOT NUMBER_FILE STREQUAL "")
    get_filename_component(_number_dir "${NUMBER_FILE}" DIRECTORY)
    if(NOT _number_dir STREQUAL "")
        file(MAKE_DIRECTORY "${_number_dir}")
    endif()
    file(WRITE "${NUMBER_FILE}"
"build_number=${BUILD_NUMBER}
version=${PROJECT_SEMVER}
version_build=${DOM_VERSION_BUILD}
")
endif()
