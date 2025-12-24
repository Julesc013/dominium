cmake_minimum_required(VERSION 3.16)
project(DominiumDomino LANGUAGES C CXX)

enable_testing()

set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(DominiumBundleRuntime)
include(DominiumReproducible)
include(dominium_dist)

set(DOMINIUM_SOURCE_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")
set(DOMINIUM_GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated/include")
set(DOMINIUM_INCLUDE_DIR "${DOMINIUM_GENERATED_INCLUDE_DIR};${DOMINIUM_SOURCE_INCLUDE_DIR}")

# Generated baseline-safe config header (macros + integer literals only).
set(DOM_BUILD_ID "unknown" CACHE STRING "Build identifier embedded into binaries")
set(DOM_PROJECT_SEMVER "0.0.0" CACHE STRING "Project semantic version")

option(DOM_ENABLE_MODERN "Enable optional acceleration layers (never removes baseline correctness paths)" OFF)
option(DOM_ENABLE_AUDIO "Enable audio subsystem/modules (if present)" ON)
option(DOM_ENABLE_NET "Enable networking subsystem/modules (if present)" ON)
option(DOMUI_ENABLE_JSON_MIRROR "Enable deterministic JSON mirror writes for UI docs" ON)
option(DOMUI_ENABLE_CODEGEN "Enable DOMUI action codegen tools and build steps" ON)

option(DOM_DISALLOW_DOWNLOADS "Disallow any build-time network downloads" ON)
if(DOM_DISALLOW_DOWNLOADS)
    set(FETCHCONTENT_FULLY_DISCONNECTED ON CACHE BOOL "Disallow downloads via FetchContent" FORCE)
    set(FETCHCONTENT_UPDATES_DISCONNECTED ON CACHE BOOL "Disallow updates via FetchContent" FORCE)
endif()

if(WIN32)
    set(_dom_platform_default "win32")
elseif(UNIX)
    set(_dom_platform_default "posix_headless")
else()
    set(_dom_platform_default "null")
endif()
set(DOM_PLATFORM "${_dom_platform_default}" CACHE STRING "Dominium platform backend (win32|win32_headless|null|posix_headless|posix_x11|posix_wayland|cocoa)")
set_property(CACHE DOM_PLATFORM PROPERTY STRINGS win32 win32_headless null posix_headless posix_x11 posix_wayland cocoa)

option(DOM_BACKEND_SOFT "Enable DGFX software renderer backend" ON)
option(DOM_BACKEND_NULL "Enable DGFX null renderer backend (headless/CI)" OFF)
option(DOM_BACKEND_DX9 "Enable DGFX Direct3D 9 renderer backend" OFF)
option(DOM_BACKEND_DX11 "Enable DGFX Direct3D 11 renderer backend" OFF)
option(DOM_BACKEND_GL1 "Enable DGFX OpenGL 1.x renderer backend" OFF)
option(DOM_BACKEND_GL2 "Enable DGFX OpenGL 2.x renderer backend" OFF)
option(DOM_BACKEND_VK1 "Enable DGFX Vulkan 1.0 renderer backend" OFF)
option(DOM_BACKEND_METAL "Enable DGFX Metal renderer backend" OFF)
option(DOM_BACKEND_SDL2 "Enable DSYS SDL2 platform backend" OFF)
option(DOM_BACKEND_VECTOR2D "Enable vector2d acceleration layer" OFF)

set(DOMINO_CFG_BUILD_DEBUG 0)
set(DOMINO_CFG_BUILD_RELEASE 0)
set(DOMINO_CFG_BUILD_RELWITHDEBINFO 0)
set(DOMINO_CFG_BUILD_MINSIZEREL 0)

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(DOMINO_CFG_BUILD_DEBUG 1)
elseif(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(DOMINO_CFG_BUILD_RELEASE 1)
elseif(CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
    set(DOMINO_CFG_BUILD_RELWITHDEBINFO 1)
elseif(CMAKE_BUILD_TYPE STREQUAL "MinSizeRel")
    set(DOMINO_CFG_BUILD_MINSIZEREL 1)
endif()

set(DOMINO_CFG_PLATFORM_WIN32 0)
set(DOMINO_CFG_PLATFORM_UNIX 0)
set(DOMINO_CFG_PLATFORM_APPLE 0)
if(WIN32)
    set(DOMINO_CFG_PLATFORM_WIN32 1)
endif()
if(UNIX)
    set(DOMINO_CFG_PLATFORM_UNIX 1)
endif()
if(APPLE)
    set(DOMINO_CFG_PLATFORM_APPLE 1)
endif()

set(DOM_CFG_HOST_WIN32 0)
set(DOM_CFG_HOST_UNIX 0)
set(DOM_CFG_HOST_APPLE 0)
if(WIN32)
    set(DOM_CFG_HOST_WIN32 1)
endif()
if(UNIX)
    set(DOM_CFG_HOST_UNIX 1)
endif()
if(APPLE)
    set(DOM_CFG_HOST_APPLE 1)
endif()

set(DOM_CFG_PLATFORM_ID 0)
string(TOLOWER "${DOM_PLATFORM}" _dom_platform_lc)
if(_dom_platform_lc STREQUAL "win32")
    set(DOM_CFG_PLATFORM_ID 1)
elseif(_dom_platform_lc STREQUAL "win32_headless")
    set(DOM_CFG_PLATFORM_ID 2)
elseif(_dom_platform_lc STREQUAL "null")
    set(DOM_CFG_PLATFORM_ID 100)
elseif(_dom_platform_lc STREQUAL "posix_headless")
    set(DOM_CFG_PLATFORM_ID 200)
elseif(_dom_platform_lc STREQUAL "posix_x11")
    set(DOM_CFG_PLATFORM_ID 201)
elseif(_dom_platform_lc STREQUAL "posix_wayland")
    set(DOM_CFG_PLATFORM_ID 202)
elseif(_dom_platform_lc STREQUAL "cocoa")
    set(DOM_CFG_PLATFORM_ID 300)
else()
    message(FATAL_ERROR "Unsupported DOM_PLATFORM: '${DOM_PLATFORM}'")
endif()

set(DOM_CFG_BACKEND_SOFT 0)
if(DOM_BACKEND_SOFT)
    set(DOM_CFG_BACKEND_SOFT 1)
endif()

set(DOM_CFG_BACKEND_NULL 0)
if(DOM_BACKEND_NULL)
    set(DOM_CFG_BACKEND_NULL 1)
endif()

set(DOM_CFG_BACKEND_DX9 0)
if(DOM_BACKEND_DX9)
    set(DOM_CFG_BACKEND_DX9 1)
endif()

set(DOM_CFG_BACKEND_DX11 0)
if(DOM_BACKEND_DX11)
    set(DOM_CFG_BACKEND_DX11 1)
endif()

set(DOM_CFG_BACKEND_GL1 0)
if(DOM_BACKEND_GL1)
    set(DOM_CFG_BACKEND_GL1 1)
endif()

set(DOM_CFG_BACKEND_GL2 0)
if(DOM_BACKEND_GL2)
    set(DOM_CFG_BACKEND_GL2 1)
endif()

set(DOM_CFG_BACKEND_VK1 0)
if(DOM_BACKEND_VK1)
    set(DOM_CFG_BACKEND_VK1 1)
endif()

set(DOM_CFG_BACKEND_METAL 0)
if(DOM_BACKEND_METAL)
    set(DOM_CFG_BACKEND_METAL 1)
endif()

set(DOM_CFG_BACKEND_SDL2 0)
if(DOM_BACKEND_SDL2)
    set(DOM_CFG_BACKEND_SDL2 1)
endif()

set(DOM_CFG_BACKEND_VECTOR2D 0)
if(DOM_BACKEND_VECTOR2D)
    set(DOM_CFG_BACKEND_VECTOR2D 1)
endif()

# Build metadata (best-effort; no network).
set(DOM_BUILD_NUMBER "0")
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/.dominium_build_number")
    file(READ "${CMAKE_CURRENT_SOURCE_DIR}/.dominium_build_number" _dom_build_number_raw)
    string(STRIP "${_dom_build_number_raw}" _dom_build_number_stripped)
    if(NOT _dom_build_number_stripped STREQUAL "")
        set(DOM_BUILD_NUMBER "${_dom_build_number_stripped}")
    endif()
endif()

set(DOM_GIT_HASH "unknown")
set(DOM_GIT_HASH_SHORT "unknown")
find_program(DOM_GIT_EXECUTABLE NAMES git git.exe
    PATHS
        "C:/Program Files/Git/cmd"
        "C:/Program Files/Git/bin"
        "C:/msys64/usr/bin"
        "C:/msys64/ucrt64/bin"
)
if(DOM_GIT_EXECUTABLE)
    execute_process(
        COMMAND "${DOM_GIT_EXECUTABLE}" rev-parse HEAD
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        RESULT_VARIABLE _dom_git_res
        OUTPUT_VARIABLE _dom_git_out
        ERROR_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    if(_dom_git_res EQUAL 0 AND NOT _dom_git_out STREQUAL "")
        set(DOM_GIT_HASH "${_dom_git_out}")
        string(LENGTH "${DOM_GIT_HASH}" _dom_git_len)
        if(_dom_git_len GREATER_EQUAL 12)
            string(SUBSTRING "${DOM_GIT_HASH}" 0 12 DOM_GIT_HASH_SHORT)
        else()
            set(DOM_GIT_HASH_SHORT "${DOM_GIT_HASH}")
        endif()
    endif()
endif()

set(DOM_TOOLCHAIN_ID "unknown")
set(_dom_toolchain_id "")
if(DEFINED CMAKE_C_COMPILER_ID AND NOT CMAKE_C_COMPILER_ID STREQUAL "")
    if(DEFINED CMAKE_C_COMPILER_VERSION AND NOT CMAKE_C_COMPILER_VERSION STREQUAL "")
        set(_dom_toolchain_id "c=${CMAKE_C_COMPILER_ID}-${CMAKE_C_COMPILER_VERSION}")
    else()
        set(_dom_toolchain_id "c=${CMAKE_C_COMPILER_ID}")
    endif()
endif()
if(DEFINED CMAKE_CXX_COMPILER_ID AND NOT CMAKE_CXX_COMPILER_ID STREQUAL "")
    if(DEFINED CMAKE_CXX_COMPILER_VERSION AND NOT CMAKE_CXX_COMPILER_VERSION STREQUAL "")
        if(NOT _dom_toolchain_id STREQUAL "")
            set(_dom_toolchain_id "${_dom_toolchain_id};cxx=${CMAKE_CXX_COMPILER_ID}-${CMAKE_CXX_COMPILER_VERSION}")
        else()
            set(_dom_toolchain_id "cxx=${CMAKE_CXX_COMPILER_ID}-${CMAKE_CXX_COMPILER_VERSION}")
        endif()
    else()
        if(NOT _dom_toolchain_id STREQUAL "")
            set(_dom_toolchain_id "${_dom_toolchain_id};cxx=${CMAKE_CXX_COMPILER_ID}")
        else()
            set(_dom_toolchain_id "cxx=${CMAKE_CXX_COMPILER_ID}")
        endif()
    endif()
endif()
if(MSVC AND DEFINED MSVC_TOOLSET_VERSION AND NOT MSVC_TOOLSET_VERSION STREQUAL "")
    if(NOT _dom_toolchain_id STREQUAL "")
        set(_dom_toolchain_id "${_dom_toolchain_id};toolset=${MSVC_TOOLSET_VERSION}")
    else()
        set(_dom_toolchain_id "toolset=${MSVC_TOOLSET_VERSION}")
    endif()
endif()
if(NOT _dom_toolchain_id STREQUAL "")
    string(REPLACE " " "" _dom_toolchain_id "${_dom_toolchain_id}")
    set(DOM_TOOLCHAIN_ID "${_dom_toolchain_id}" CACHE STRING "Toolchain identifier embedded into binaries" FORCE)
endif()

if(NOT DEFINED DOM_BUILD_ID OR DOM_BUILD_ID STREQUAL "" OR DOM_BUILD_ID STREQUAL "unknown")
    set(_dom_build_id "unknown")
    if(NOT DOM_GIT_HASH_SHORT STREQUAL "unknown")
        if(NOT DOM_BUILD_NUMBER STREQUAL "0")
            set(_dom_build_id "b${DOM_BUILD_NUMBER}-${DOM_GIT_HASH_SHORT}")
        else()
            set(_dom_build_id "git-${DOM_GIT_HASH_SHORT}")
        endif()
    elseif(NOT DOM_BUILD_NUMBER STREQUAL "0")
        set(_dom_build_id "b${DOM_BUILD_NUMBER}")
    endif()
    set(DOM_BUILD_ID "${_dom_build_id}" CACHE STRING "Build identifier embedded into binaries" FORCE)
endif()

set(DOM_BUILD_STATE_FILE "${CMAKE_CURRENT_SOURCE_DIR}/.dominium_build_number")
set(DOM_BUILD_HEADER_FILE "${DOMINIUM_GENERATED_INCLUDE_DIR}/dominium/build_version.generated.h")
set(DOM_BUILD_NUMBER_FILE "${CMAKE_CURRENT_BINARY_DIR}/generated/build_number.txt")

add_custom_target(dom_update_build_number ALL
    COMMAND ${CMAKE_COMMAND}
        -DSTATE_FILE=${DOM_BUILD_STATE_FILE}
        -DHEADER_FILE=${DOM_BUILD_HEADER_FILE}
        -DNUMBER_FILE=${DOM_BUILD_NUMBER_FILE}
        -DPROJECT_SEMVER=${DOM_PROJECT_SEMVER}
        -P ${CMAKE_CURRENT_SOURCE_DIR}/scripts/update_build_number.cmake
    COMMENT "Incrementing global build number"
)
add_compile_definitions(DOM_BUILD_VERSION_GENERATED)

file(MAKE_DIRECTORY "${DOMINIUM_GENERATED_INCLUDE_DIR}/domino")
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/config_base.h.in"
    "${DOMINIUM_GENERATED_INCLUDE_DIR}/domino/config_base.h"
    @ONLY
)

# Configure-time header hygiene check for baseline-visible public headers.
include(BaselineHeaderCheck)
dominium_baseline_header_check("${DOMINIUM_SOURCE_INCLUDE_DIR}")

option(DOMINIUM_STATIC_GNU_RUNTIME "Link libgcc/libstdc++ statically on MinGW/MSYS" ON)
if(DOMINIUM_STATIC_GNU_RUNTIME AND (MINGW OR MSYS))
    add_link_options(-static-libgcc -static-libstdc++)
endif()

set(DOMINIUM_RUNTIME_SEARCH_DIRS "")
if(WIN32 AND (MINGW OR MSYS))
    get_filename_component(_dom_toolchain_bindir "${CMAKE_C_COMPILER}" DIRECTORY)
    list(APPEND DOMINIUM_RUNTIME_SEARCH_DIRS "${_dom_toolchain_bindir}")
    if(CMAKE_PREFIX_PATH)
        list(APPEND DOMINIUM_RUNTIME_SEARCH_DIRS ${CMAKE_PREFIX_PATH})
    endif()
endif()

option(DOMINIUM_ENABLE_PACKAGING "Enable packaging helper targets" OFF)

set(DOM_DIST_ROOT "${CMAKE_SOURCE_DIR}/dist" CACHE PATH "Dist output root")
set(DOM_DIST_OS "" CACHE STRING "Override dist os token")
set(DOM_DIST_ARCH "" CACHE STRING "Override dist arch token")
set(DOM_DIST_VARIANT "" CACHE STRING "Optional dist variant token (msvc, mingw, etc.)")
dominium_dist_init(
    DIST_ROOT "${DOM_DIST_ROOT}"
    DIST_OS "${DOM_DIST_OS}"
    DIST_ARCH "${DOM_DIST_ARCH}"
    DIST_VARIANT "${DOM_DIST_VARIANT}"
)

add_subdirectory(source/domino)
add_subdirectory(source/dominium)
add_subdirectory(tools)
add_subdirectory(source/tests)

if(WIN32)
    set(DOMUI_INDEX_PATH ${CMAKE_SOURCE_DIR}/tools/ui_index/ui_index.json)
    set(DOMUI_LAUNCHER_DOC ${CMAKE_SOURCE_DIR}/tools/launcher/ui/doc/launcher_ui_doc.tlv)
    set(DOMUI_SETUP_DOC ${CMAKE_SOURCE_DIR}/tools/setup/ui/doc/setup_ui_doc.tlv)

    add_custom_target(ui_scan_all
        COMMAND $<TARGET_FILE:dominium-ui-editor> --scan-ui --out ${DOMUI_INDEX_PATH}
        COMMENT "Scanning repo UI docs"
        VERBATIM
    )
    add_dependencies(ui_scan_all dominium-ui-editor)

    add_custom_target(ui_validate_all
        COMMAND $<TARGET_FILE:dominium-ui-editor> --headless-validate ${DOMUI_LAUNCHER_DOC} --targets win32_t1
        COMMAND $<TARGET_FILE:dominium-ui-editor> --headless-validate ${DOMUI_SETUP_DOC} --targets win32_t1
        COMMENT "Validating canonical launcher/setup UI docs"
        VERBATIM
    )
    add_dependencies(ui_validate_all dominium-ui-editor)
else()
    add_custom_target(ui_scan_all
        COMMAND ${CMAKE_COMMAND} -E echo "ui_scan_all: not supported on this platform"
    )
    add_custom_target(ui_validate_all
        COMMAND ${CMAKE_COMMAND} -E echo "ui_validate_all: not supported on this platform"
    )
    add_custom_target(ui_capability_test
        COMMAND ${CMAKE_COMMAND} -E echo "ui_capability_test: not supported on this platform"
    )
endif()

if(WIN32)
    add_custom_target(ui_capability_test
        DEPENDS
            ui_scan_all
            ui_regen_launcher
            ui_regen_setup
            ui_validate_all
    )
endif()

if(DOMINIUM_ENABLE_PACKAGING)
    add_subdirectory(scripts/packaging)
endif()

get_property(_dom_dist_targets GLOBAL PROPERTY DOM_DIST_ROLE_TARGETS)
if(NOT _dom_dist_targets)
    set(_dom_dist_targets "")
endif()

add_custom_target(dist_meta
    COMMAND ${CMAKE_COMMAND}
        -DDOM_DIST_ROOT=${DOM_DIST_ROOT}
        -DDOM_DIST_OS=${DOM_DIST_OS}
        -DDOM_DIST_ARCH=${DOM_DIST_ARCH}
        -DDOM_DIST_VARIANT=${DOM_DIST_VARIANT}
        -DDOM_DIST_CONFIG=$<CONFIG>
        -DDOM_DIST_GENERATOR=${CMAKE_GENERATOR}
        -DDOM_DIST_PROJECT=${CMAKE_PROJECT_NAME}
        -DDOM_BUILD_ID=${DOM_BUILD_ID}
        -DDOM_TOOLCHAIN_ID=${DOM_TOOLCHAIN_ID}
        -DDOM_GIT_HASH=${DOM_GIT_HASH}
        -DDOM_PROJECT_SEMVER=${DOM_PROJECT_SEMVER}
        -P ${CMAKE_SOURCE_DIR}/cmake/dominium_dist_meta.cmake
    DEPENDS ${_dom_dist_targets}
    COMMENT "Generating dist metadata"
)

set(CPACK_PACKAGE_NAME "dominium")
set(CPACK_PACKAGE_VENDOR "Dominium")
set(CPACK_PACKAGE_CONTACT "support@dominium.invalid")
set(CPACK_PACKAGE_VERSION "0.0.0")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "${CPACK_PACKAGE_CONTACT}")
set(CPACK_DEBIAN_PACKAGE_SECTION "games")
set(CPACK_RPM_PACKAGE_LICENSE "MIT")
set(CPACK_RPM_PACKAGE_URL "https://example.com/dominium")
include(CPack)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
