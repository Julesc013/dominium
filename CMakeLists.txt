cmake_minimum_required(VERSION 3.21...4.2)
cmake_policy(VERSION 3.21)
if(POLICY CMP0135)
    cmake_policy(SET CMP0135 NEW)
endif()
project(DominiumDomino LANGUAGES C CXX)

set(DOMINIUM_OUTPUT_BIN_DIR "${CMAKE_BINARY_DIR}/bin")
set(DOMINIUM_OUTPUT_LIB_DIR "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${DOMINIUM_OUTPUT_BIN_DIR}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${DOMINIUM_OUTPUT_LIB_DIR}")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${DOMINIUM_OUTPUT_LIB_DIR}")
foreach(_cfg IN ITEMS Debug Release RelWithDebInfo MinSizeRel)
    string(TOUPPER "${_cfg}" _cfg_upper)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${_cfg_upper} "${DOMINIUM_OUTPUT_BIN_DIR}")
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${_cfg_upper} "${DOMINIUM_OUTPUT_LIB_DIR}")
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${_cfg_upper} "${DOMINIUM_OUTPUT_LIB_DIR}")
endforeach()

option(DOM_BUILD_TESTS "Build tests" OFF)
option(DOM_BUILD_TOOLS "Build tools" OFF)
option(DOM_BUILD_SETUP "Build setup" ON)
option(DOM_BUILD_LAUNCHER "Build launcher" ON)
option(DOM_BUILD_GAME "Build game/client/server" ON)
option(DOM_PROJECTION "Generate IDE projection metadata and outputs" OFF)
option(DOM_TOOLCHAIN_STRICT "Fail configure on non-canonical toolchains/generators" OFF)

set(DOM_PROJECTION_ID "" CACHE STRING "IDE projection identifier")
set(DOM_PRODUCT "" CACHE STRING "IDE projection product (engine/game/client/server/launcher/setup/tools)")
set(DOM_PRODUCT_TARGET "" CACHE STRING "IDE projection target override (optional)")
set(DOM_UI_SHELL "" CACHE STRING "IDE projection UI shell path (or empty)")
set(DOM_TOOLCHAIN_TIER "" CACHE STRING "IDE projection toolchain tier")
set(DOM_TARGET_OS_FAMILY "" CACHE STRING "IDE projection OS family")
set(DOM_TARGET_OS_MIN "" CACHE STRING "IDE projection OS minimum")
set(DOM_TARGET_ARCH "" CACHE STRING "IDE projection architecture id")
set(DOM_LANG_MODE "" CACHE STRING "IDE projection language mode")
set(DOM_SDK_PIN "" CACHE STRING "IDE projection SDK pin")
set(DOM_CRT_POLICY "" CACHE STRING "IDE projection CRT policy")
set(DOM_IDE_OUT_DIR "" CACHE STRING "IDE projection output directory (under /ide)")
set(DOM_IDE_GENERATOR_OVERRIDE "" CACHE STRING "IDE projection generator label (optional)")

enable_testing()

if(WIN32 AND NOT MSVC)
    if(DOM_TOOLCHAIN_STRICT)
        message(FATAL_ERROR "Windows builds prefer the MSVC toolchain; set DOM_TOOLCHAIN_STRICT=OFF to allow others.")
    else()
        message(WARNING "Windows build on non-MSVC toolchain is best-effort.")
    endif()
endif()
if(APPLE)
    if(NOT CMAKE_GENERATOR STREQUAL "Xcode" AND NOT DOM_PROJECTION)
        if(DOM_TOOLCHAIN_STRICT)
            message(FATAL_ERROR "macOS builds prefer the Xcode generator; set DOM_TOOLCHAIN_STRICT=OFF to allow others.")
        else()
            message(WARNING "macOS build without Xcode generator is unverified.")
        endif()
    endif()
elseif(UNIX)
    if(NOT DOM_PROJECTION)
        if(NOT CMAKE_C_COMPILER_ID STREQUAL "GNU" AND NOT CMAKE_C_COMPILER_ID STREQUAL "Clang")
            if(DOM_TOOLCHAIN_STRICT)
                message(FATAL_ERROR "Linux builds prefer GCC or Clang; set DOM_TOOLCHAIN_STRICT=OFF to allow others.")
            else()
                message(WARNING "Linux build on non-GNU/Clang compiler is unverified.")
            endif()
        endif()
    endif()
endif()

set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(MSVC)
    # Allow parallel compilation to share PDBs without contention.
    add_compile_options(/FS)
endif()

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(DominiumBundleRuntime)
include(DominiumReproducible)
include(dist_output)
include(DomIntegration)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

execute_process(
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_cmake_no_global_includes.py
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    RESULT_VARIABLE _dom_cmake_sanity_res
)
if(NOT _dom_cmake_sanity_res EQUAL 0)
    message(FATAL_ERROR "CMake global include check failed; remove global include directories usage.")
endif()

set(DOC_RATIO_ENABLE ON CACHE BOOL "Enable documentation ratio quality gate")
set(DOC_RATIO_ROOTS "engine;game;client;server;launcher;setup;tools;libs;app" CACHE STRING "Roots to scan for documentation ratios")
if(DOC_RATIO_ROOTS STREQUAL "src;include")
    set(DOC_RATIO_ROOTS "engine;game;client;server;launcher;setup;tools;libs;app" CACHE STRING "Roots to scan for documentation ratios" FORCE)
endif()
set(DOC_RATIO_EXCLUDES "third_party;external;build;out;.git;generated" CACHE STRING "Path fragments excluded from documentation ratios")
set(DOC_RATIO_EXTS ".c;.h;.cpp;.hpp;.cc;.cxx;.hh;.hxx;.ipp;.inl" CACHE STRING "File extensions for documentation ratios")
set(DOC_RATIO_MIN_LINE "0.06" CACHE STRING "Minimum comment line ratio")
if(DOC_RATIO_MIN_LINE STREQUAL "0.20")
    set(DOC_RATIO_MIN_LINE "0.06" CACHE STRING "Minimum comment line ratio" FORCE)
endif()
set(DOC_RATIO_MAX_LINE "0.40" CACHE STRING "Maximum comment line ratio")
set(DOC_RATIO_MIN_WORD "0.14" CACHE STRING "Minimum comment word ratio")
if(DOC_RATIO_MIN_WORD STREQUAL "0.15")
    set(DOC_RATIO_MIN_WORD "0.14" CACHE STRING "Minimum comment word ratio" FORCE)
endif()
set(DOC_RATIO_MAX_WORD "0.30" CACHE STRING "Maximum comment word ratio")
set(DOC_RATIO_MIN_CHAR "0.09" CACHE STRING "Minimum comment character ratio")
if(DOC_RATIO_MIN_CHAR STREQUAL "0.10")
    set(DOC_RATIO_MIN_CHAR "0.09" CACHE STRING "Minimum comment character ratio" FORCE)
endif()
set(DOC_RATIO_MAX_CHAR "0.25" CACHE STRING "Maximum comment character ratio")

set(DOC_RATIO_MODE "warn")
if(DEFINED ENV{CI})
    set(_doc_ratio_ci "$ENV{CI}")
    string(TOLOWER "${_doc_ratio_ci}" _doc_ratio_ci_lc)
    if(NOT _doc_ratio_ci_lc STREQUAL "" AND NOT _doc_ratio_ci_lc STREQUAL "0" AND NOT _doc_ratio_ci_lc STREQUAL "false")
        set(DOC_RATIO_MODE "fail")
    endif()
endif()

set(_doc_ratio_args
    --mode ${DOC_RATIO_MODE}
    --format text
    --quiet
    --min-line ${DOC_RATIO_MIN_LINE}
    --max-line ${DOC_RATIO_MAX_LINE}
    --min-word ${DOC_RATIO_MIN_WORD}
    --max-word ${DOC_RATIO_MAX_WORD}
    --min-char ${DOC_RATIO_MIN_CHAR}
    --max-char ${DOC_RATIO_MAX_CHAR}
)
foreach(_doc_ratio_root IN LISTS DOC_RATIO_ROOTS)
    list(APPEND _doc_ratio_args --roots "${_doc_ratio_root}")
endforeach()
foreach(_doc_ratio_exclude IN LISTS DOC_RATIO_EXCLUDES)
    list(APPEND _doc_ratio_args --exclude "${_doc_ratio_exclude}")
endforeach()
foreach(_doc_ratio_ext IN LISTS DOC_RATIO_EXTS)
    list(APPEND _doc_ratio_args --ext "${_doc_ratio_ext}")
endforeach()

add_custom_target(doc_ratio_check
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/setup/packages/scripts/doc_ratio_check.py ${_doc_ratio_args}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking documentation ratios (mode=${DOC_RATIO_MODE})"
    VERBATIM
)

if(NOT TARGET all_quality_gates)
    add_custom_target(all_quality_gates ALL)
endif()
if(DOC_RATIO_ENABLE)
    add_dependencies(all_quality_gates doc_ratio_check)
endif()

add_custom_target(check_arch
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/ci/arch_checks.py --repo-root ${CMAKE_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Running architecture boundary checks"
)

add_test(NAME phase6_audit
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/ci/phase6_audit_checks.py --repo-root ${CMAKE_SOURCE_DIR}
)

add_custom_target(check_hygiene
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/ci/check_hygiene_scan.py --mode check --queue ${CMAKE_SOURCE_DIR}/docs/ci/HYGIENE_QUEUE.md
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking code/data hygiene queue consistency"
)

add_custom_target(check_comment_density
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/ci/check_comment_density.py --mode warn
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking comment density and doc blocks"
)

add_custom_target(check_todo_blockers
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/ci/check_todo_blockers.py --mode fail
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking TODO blocker policy"
)

add_custom_target(check_magic_numbers
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/ci/check_magic_numbers.py --mode warn
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking magic number policy"
)

add_custom_target(check_forbidden_enums
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/ci/check_forbidden_enums.py --mode fail
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking forbidden enum values"
)

add_custom_target(check_switch_on_taxonomy
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/ci/check_switch_on_taxonomy.py --mode warn
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking switch statements on taxonomy ids/types"
)

add_custom_target(check_ide_quarantine
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_ide_quarantine.py --repo-root ${CMAKE_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking IDE projection quarantine"
)

add_custom_target(check_ui_shell_purity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_ui_shell_purity.py --repo-root ${CMAKE_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking UI shell purity"
)

add_custom_target(check_abi_boundaries
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_abi_boundaries.py --repo-root ${CMAKE_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking ABI boundary rules"
)

add_custom_target(check_docs_sanity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_docs_sanity.py --repo-root ${CMAKE_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking documentation sanity"
)

add_custom_target(check_all)
add_dependencies(check_all
    all_quality_gates
    check_arch
    check_hygiene
    check_comment_density
    check_todo_blockers
    check_magic_numbers
    check_forbidden_enums
    check_switch_on_taxonomy
    check_ide_quarantine
    check_ui_shell_purity
    check_abi_boundaries
    check_docs_sanity
)

set(DOMINIUM_ENGINE_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/engine/include")
set(DOMINIUM_GAME_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/game/include")
set(DOMINIUM_SETUP_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/setup/include")
set(DOMINIUM_TOOLS_UI_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/tools/ui_shared/include")
set(DOMINIUM_GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated/include")
set(DOMINIUM_SOURCE_INCLUDE_DIR "${DOMINIUM_ENGINE_INCLUDE_DIR}")
set(DOMINIUM_INCLUDE_DIR "${DOMINIUM_GENERATED_INCLUDE_DIR};${DOMINIUM_ENGINE_INCLUDE_DIR}")

# Product version inputs (VERSION_* files; semver required).
function(dom_require_semver label value)
    string(REGEX MATCH "^[0-9]+\\.[0-9]+\\.[0-9]+$" _dom_semver_ok "${value}")
    if(NOT _dom_semver_ok)
        message(FATAL_ERROR "Invalid semver in ${label}: '${value}' (expected MAJOR.MINOR.PATCH)")
    endif()
endfunction()

function(dom_read_version path label out_var)
    if(NOT EXISTS "${path}")
        message(FATAL_ERROR "Missing ${label} file: ${path}")
    endif()
    file(READ "${path}" _dom_version_raw)
    string(STRIP "${_dom_version_raw}" _dom_version_stripped)
    if(_dom_version_stripped STREQUAL "")
        message(FATAL_ERROR "Empty ${label} value in ${path}")
    endif()
    dom_require_semver("${label}" "${_dom_version_stripped}")
    set(${out_var} "${_dom_version_stripped}" PARENT_SCOPE)
endfunction()

function(dom_parse_semver value prefix)
    string(REPLACE "." ";" _dom_semver_parts "${value}")
    list(LENGTH _dom_semver_parts _dom_semver_len)
    if(_dom_semver_len LESS 3)
        message(FATAL_ERROR "Invalid semver '${value}' for ${prefix}")
    endif()
    list(GET _dom_semver_parts 0 _dom_semver_major)
    list(GET _dom_semver_parts 1 _dom_semver_minor)
    list(GET _dom_semver_parts 2 _dom_semver_patch)
    set(${prefix}_MAJOR "${_dom_semver_major}" PARENT_SCOPE)
    set(${prefix}_MINOR "${_dom_semver_minor}" PARENT_SCOPE)
    set(${prefix}_PATCH "${_dom_semver_patch}" PARENT_SCOPE)
endfunction()

dom_read_version("${CMAKE_SOURCE_DIR}/VERSION_ENGINE" "VERSION_ENGINE" DOM_ENGINE_SEMVER)
dom_read_version("${CMAKE_SOURCE_DIR}/VERSION_GAME" "VERSION_GAME" DOM_GAME_SEMVER)
dom_read_version("${CMAKE_SOURCE_DIR}/VERSION_CLIENT" "VERSION_CLIENT" DOM_CLIENT_SEMVER)
dom_read_version("${CMAKE_SOURCE_DIR}/VERSION_SERVER" "VERSION_SERVER" DOM_SERVER_SEMVER)
dom_read_version("${CMAKE_SOURCE_DIR}/VERSION_LAUNCHER" "VERSION_LAUNCHER" DOM_LAUNCHER_SEMVER)
dom_read_version("${CMAKE_SOURCE_DIR}/VERSION_SETUP" "VERSION_SETUP" DOM_SETUP_SEMVER)
dom_read_version("${CMAKE_SOURCE_DIR}/VERSION_TOOLS" "VERSION_TOOLS" DOM_TOOLS_SEMVER)
dom_read_version("${CMAKE_SOURCE_DIR}/VERSION_SUITE" "VERSION_SUITE" DOM_SUITE_SEMVER)

dom_parse_semver("${DOM_ENGINE_SEMVER}" DOM_ENGINE_VERSION)
dom_parse_semver("${DOM_SUITE_SEMVER}" DOM_SUITE_VERSION)

# Generated baseline-safe config header (macros + integer literals only).
set(DOM_BUILD_ID "unknown" CACHE STRING "Build identifier embedded into binaries")
set(DOM_PROJECT_SEMVER "${DOM_SUITE_SEMVER}" CACHE STRING "Project semantic version" FORCE)
set(DOM_BUILD_SKU "auto" CACHE STRING "SKU override (auto|modern_desktop|headless_server|devtools|legacy_desktop)")
set(DOM_BUILD_MODE "" CACHE STRING "Optional build mode label (Debug/Release/DeterministicRelease)")
set(DOM_TOOLCHAIN_STDLIB "" CACHE STRING "Toolchain standard library label override")
set(DOM_TOOLCHAIN_RUNTIME "" CACHE STRING "Toolchain runtime/CRT/libc label override")
set(DOM_TOOLCHAIN_LINK "" CACHE STRING "Toolchain link mode override (static|dynamic)")

option(DOM_ENABLE_MODERN "Enable optional acceleration layers (never removes baseline correctness paths)" OFF)
option(DOM_ENABLE_AUDIO "Enable audio subsystem/modules (if present)" ON)
option(DOM_ENABLE_NET "Enable networking subsystem/modules (if present)" ON)
option(DOMUI_ENABLE_JSON_MIRROR "Enable deterministic JSON mirror writes for UI docs" ON)
option(DOMUI_ENABLE_CODEGEN "Enable DOMUI action codegen tools and build steps" ON)

option(SETUP_DEFAULT "Make Setup the default installer CLI/packaging path" ON)
option(SETUP_LEGACY_BUILD "Build legacy setup stack (deprecated)" ON)
option(SETUP_LEGACY_DEPRECATED_WARN "Warn when building legacy setup targets" ON)
option(ENABLE_NSIS_DEV_INSTALLER "Build development-only NSIS setup wrapper" OFF)

if(NOT DEFINED DOMINIUM_BUILD_SETUP)
    set(DOMINIUM_BUILD_SETUP ${SETUP_DEFAULT} CACHE BOOL "Build setup kernel/services/frontends")
endif()
if(NOT DEFINED DOMINIUM_BUILD_SETUP_LEGACY)
    set(DOMINIUM_BUILD_SETUP_LEGACY ${SETUP_LEGACY_BUILD} CACHE BOOL "Build legacy setup stack")
endif()

option(DOM_DISALLOW_DOWNLOADS "Disallow any build-time network downloads" ON)
if(DOM_DISALLOW_DOWNLOADS)
    set(FETCHCONTENT_FULLY_DISCONNECTED ON CACHE BOOL "Disallow downloads via FetchContent" FORCE)
    set(FETCHCONTENT_UPDATES_DISCONNECTED ON CACHE BOOL "Disallow updates via FetchContent" FORCE)
endif()

if(WIN32)
    set(_dom_platform_default "sdl2")
elseif(UNIX)
    set(_dom_platform_default "posix_headless")
else()
    set(_dom_platform_default "null")
endif()
set(DOM_PLATFORM "${_dom_platform_default}" CACHE STRING "Dominium platform backend (sdl2|win32|win32_headless|null|posix_headless|posix_x11|posix_wayland|cocoa)")
set_property(CACHE DOM_PLATFORM PROPERTY STRINGS sdl2 win32 win32_headless null posix_headless posix_x11 posix_wayland cocoa)

option(DOM_BACKEND_SOFT "Enable DGFX software renderer backend" ON)
option(DOM_BACKEND_NULL "Enable DGFX null renderer backend (headless/CI)" ON)
option(DOM_BACKEND_DX9 "Enable DGFX Direct3D 9 renderer backend" OFF)
option(DOM_BACKEND_DX11 "Enable DGFX Direct3D 11 renderer backend" OFF)
option(DOM_BACKEND_DX12 "Enable DGFX Direct3D 12 renderer backend" OFF)
option(DOM_BACKEND_GL1 "Enable DGFX OpenGL 1.x renderer backend" OFF)
option(DOM_BACKEND_GL2 "Enable DGFX OpenGL 2.x renderer backend" OFF)
option(DOM_BACKEND_GL4 "Enable DGFX OpenGL 4.x renderer backend" OFF)
option(DOM_BACKEND_VK1 "Enable DGFX Vulkan 1.0 renderer backend" OFF)
option(DOM_BACKEND_METAL "Enable DGFX Metal renderer backend" OFF)
option(DOM_BACKEND_SDL2 "Enable DSYS SDL2 platform backend" OFF)
option(DOM_FETCH_SDL2 "Fetch SDL2 when missing for DOM_PLATFORM=sdl2" OFF)
option(DOM_BACKEND_VECTOR2D "Enable vector2d acceleration layer" OFF)

if(DOM_BACKEND_GL2)
    if(NOT WIN32)
        message(FATAL_ERROR "DOM_BACKEND_GL2 is currently Windows-only (WGL path).")
    endif()
    find_package(OpenGL QUIET)
    if(NOT OpenGL_FOUND)
        message(FATAL_ERROR "DOM_BACKEND_GL2=ON requires OpenGL (WGL) headers/libs on Windows. Install OpenGL dev support or use the win32+DX9 preset.")
    endif()
endif()

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
if(_dom_platform_lc STREQUAL "sdl2")
    if(NOT DEFINED DOM_SDL2_ROOT)
        set(DOM_SDL2_ROOT "" CACHE PATH "Root path for SDL2 (headers + libraries)")
    endif()
    if(DOM_SDL2_ROOT STREQUAL "")
        set(_dom_sdl2_hint "")
        file(GLOB _dom_sdl2_glob
            "${CMAKE_SOURCE_DIR}/external/SDL2*"
            "${CMAKE_SOURCE_DIR}/deps/SDL2*"
            "${CMAKE_SOURCE_DIR}/third_party/SDL2*"
            "${CMAKE_SOURCE_DIR}/artifacts/SDL2*"
        )
        foreach(_dom_path IN LISTS _dom_sdl2_glob)
            if(EXISTS "${_dom_path}/include/SDL.h" OR EXISTS "${_dom_path}/include/SDL2/SDL.h")
                set(_dom_sdl2_hint "${_dom_path}")
                break()
            endif()
        endforeach()
        if(_dom_sdl2_hint)
            set(DOM_SDL2_ROOT "${_dom_sdl2_hint}" CACHE PATH "Root path for SDL2 (headers + libraries)" FORCE)
        endif()
    endif()
    if(NOT DOM_SDL2_INCLUDE_DIR AND NOT DOM_SDL2_LIBRARY)
        find_package(SDL2 CONFIG QUIET)
        if(TARGET SDL2::SDL2)
            set(DOM_SDL2_TARGET SDL2::SDL2)
            if(NOT DOM_SDL2_INCLUDE_DIR)
                get_target_property(DOM_SDL2_INCLUDE_DIR SDL2::SDL2 INTERFACE_INCLUDE_DIRECTORIES)
            endif()
        endif()
    endif()
    if(NOT DOM_SDL2_INCLUDE_DIR)
        find_path(DOM_SDL2_INCLUDE_DIR SDL.h
            PATHS ${DOM_SDL2_ROOT} ENV SDL2_DIR ENV SDL2_PATH
            PATH_SUFFIXES include include/SDL2 SDL2
        )
    endif()
    if(NOT DOM_SDL2_LIBRARY AND NOT DOM_SDL2_TARGET)
        find_library(DOM_SDL2_LIBRARY NAMES SDL2
            PATHS ${DOM_SDL2_ROOT} ENV SDL2_DIR ENV SDL2_PATH
            PATH_SUFFIXES lib lib/x64 lib/x86
        )
    endif()
    if((NOT DOM_SDL2_INCLUDE_DIR OR (NOT DOM_SDL2_LIBRARY AND NOT DOM_SDL2_TARGET)) AND DOM_FETCH_SDL2)
        if(FETCHCONTENT_FULLY_DISCONNECTED)
            message(FATAL_ERROR "DOM_FETCH_SDL2=ON but FetchContent is disconnected; set DOM_SDL2_ROOT (or SDL2_DIR/SDL2_PATH) explicitly.")
        endif()
        include(FetchContent)
        set(_dom_prev_warn_deprecated ${CMAKE_WARN_DEPRECATED})
        set(CMAKE_WARN_DEPRECATED OFF)
        set(SDL2_DISABLE_INSTALL ON CACHE BOOL "Disable SDL2 install targets" FORCE)
        set(SDL2_DISABLE_UNINSTALL ON CACHE BOOL "Disable SDL2 uninstall target" FORCE)
        set(SDL2_TESTS OFF CACHE BOOL "Disable SDL2 tests" FORCE)
        FetchContent_Declare(dom_sdl2
            URL https://github.com/libsdl-org/SDL/releases/download/release-2.30.5/SDL2-2.30.5.zip
        )
        FetchContent_MakeAvailable(dom_sdl2)
        if(DEFINED _dom_prev_warn_deprecated)
            set(CMAKE_WARN_DEPRECATED ${_dom_prev_warn_deprecated})
            unset(_dom_prev_warn_deprecated)
        else()
            unset(CMAKE_WARN_DEPRECATED)
        endif()
        if(TARGET SDL2::SDL2)
            set(DOM_SDL2_TARGET SDL2::SDL2)
        elseif(TARGET SDL2-static)
            set(DOM_SDL2_TARGET SDL2-static)
        elseif(TARGET SDL2)
            set(DOM_SDL2_TARGET SDL2)
        endif()
        if(NOT DOM_SDL2_INCLUDE_DIR AND DOM_SDL2_TARGET)
            get_target_property(DOM_SDL2_INCLUDE_DIR ${DOM_SDL2_TARGET} INTERFACE_INCLUDE_DIRECTORIES)
        endif()
    endif()
    if(NOT DOM_SDL2_INCLUDE_DIR OR (NOT DOM_SDL2_LIBRARY AND NOT DOM_SDL2_TARGET))
        message(FATAL_ERROR "DOM_PLATFORM=sdl2 requires SDL2 headers and libraries (SDL.h, SDL2). Set DOM_SDL2_ROOT (or SDL2_DIR/SDL2_PATH), or use a win32/posix preset explicitly.")
    endif()
    set(DOM_BACKEND_SDL2 ON CACHE BOOL "Enable DSYS SDL2 platform backend" FORCE)
endif()
if(_dom_platform_lc STREQUAL "win32")
    set(DOM_CFG_PLATFORM_ID 1)
elseif(_dom_platform_lc STREQUAL "sdl2")
    set(DOM_CFG_PLATFORM_ID 3)
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

set(DOM_CFG_BACKEND_DX12 0)
if(DOM_BACKEND_DX12)
    set(DOM_CFG_BACKEND_DX12 1)
endif()

set(DOM_CFG_BACKEND_GL1 0)
if(DOM_BACKEND_GL1)
    set(DOM_CFG_BACKEND_GL1 1)
endif()

set(DOM_CFG_BACKEND_GL2 0)
if(DOM_BACKEND_GL2)
    set(DOM_CFG_BACKEND_GL2 1)
endif()

set(DOM_CFG_BACKEND_GL4 0)
if(DOM_BACKEND_GL4)
    set(DOM_CFG_BACKEND_GL4 1)
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

if(NOT TARGET dom_platform_backend_${DOM_PLATFORM})
    add_library(dom_platform_backend_${DOM_PLATFORM} INTERFACE)
    set_property(TARGET dom_platform_backend_${DOM_PLATFORM} PROPERTY DOM_PLATFORM_BACKEND_NAME "${DOM_PLATFORM}")
endif()
dom_register_platform_backend("${DOM_PLATFORM}")

if(DOM_BACKEND_SOFT AND NOT TARGET dom_render_backend_soft)
    add_library(dom_render_backend_soft INTERFACE)
    set_property(TARGET dom_render_backend_soft PROPERTY DOM_RENDER_BACKEND_NAME "soft")
    set_property(TARGET dom_render_backend_soft PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("soft" AVAILABILITY "available")
endif()
if(DOM_BACKEND_NULL AND NOT TARGET dom_render_backend_null)
    add_library(dom_render_backend_null INTERFACE)
    set_property(TARGET dom_render_backend_null PROPERTY DOM_RENDER_BACKEND_NAME "null")
    set_property(TARGET dom_render_backend_null PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("null" AVAILABILITY "available")
endif()
if(DOM_BACKEND_DX9 AND NOT TARGET dom_render_backend_dx9)
    add_library(dom_render_backend_dx9 INTERFACE)
    set_property(TARGET dom_render_backend_dx9 PROPERTY DOM_RENDER_BACKEND_NAME "dx9")
    set_property(TARGET dom_render_backend_dx9 PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("dx9" AVAILABILITY "available")
endif()
if(DOM_BACKEND_DX11 AND NOT TARGET dom_render_backend_dx11)
    add_library(dom_render_backend_dx11 INTERFACE)
    set_property(TARGET dom_render_backend_dx11 PROPERTY DOM_RENDER_BACKEND_NAME "dx11")
    set_property(TARGET dom_render_backend_dx11 PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("dx11" AVAILABILITY "available")
endif()
if(DOM_BACKEND_DX12 AND NOT TARGET dom_render_backend_dx12)
    add_library(dom_render_backend_dx12 INTERFACE)
    set_property(TARGET dom_render_backend_dx12 PROPERTY DOM_RENDER_BACKEND_NAME "dx12")
    set_property(TARGET dom_render_backend_dx12 PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("dx12" AVAILABILITY "available")
endif()
if(DOM_BACKEND_GL1 AND NOT TARGET dom_render_backend_gl1)
    add_library(dom_render_backend_gl1 INTERFACE)
    set_property(TARGET dom_render_backend_gl1 PROPERTY DOM_RENDER_BACKEND_NAME "gl1")
    set_property(TARGET dom_render_backend_gl1 PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("gl1" AVAILABILITY "available")
endif()
if(DOM_BACKEND_GL2 AND NOT TARGET dom_render_backend_gl2)
    add_library(dom_render_backend_gl2 INTERFACE)
    set_property(TARGET dom_render_backend_gl2 PROPERTY DOM_RENDER_BACKEND_NAME "gl2")
    set_property(TARGET dom_render_backend_gl2 PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("gl2" AVAILABILITY "available")
endif()
if(DOM_BACKEND_GL4 AND NOT TARGET dom_render_backend_gl4)
    add_library(dom_render_backend_gl4 INTERFACE)
    set_property(TARGET dom_render_backend_gl4 PROPERTY DOM_RENDER_BACKEND_NAME "gl4")
    set_property(TARGET dom_render_backend_gl4 PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("gl4" AVAILABILITY "available")
endif()
if(DOM_BACKEND_VK1 AND NOT TARGET dom_render_backend_vk1)
    add_library(dom_render_backend_vk1 INTERFACE)
    set_property(TARGET dom_render_backend_vk1 PROPERTY DOM_RENDER_BACKEND_NAME "vk1")
    set_property(TARGET dom_render_backend_vk1 PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("vk1" AVAILABILITY "available")
endif()
if(DOM_BACKEND_METAL AND NOT TARGET dom_render_backend_metal)
    add_library(dom_render_backend_metal INTERFACE)
    set_property(TARGET dom_render_backend_metal PROPERTY DOM_RENDER_BACKEND_NAME "metal")
    set_property(TARGET dom_render_backend_metal PROPERTY DOM_RENDER_BACKEND_AVAILABILITY "available")
    dom_register_renderer_backend("metal" AVAILABILITY "available")
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

set(DOM_GIT_DIRTY 0)
if(DOM_GIT_EXECUTABLE)
    execute_process(
        COMMAND "${DOM_GIT_EXECUTABLE}" status --porcelain
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        RESULT_VARIABLE _dom_git_dirty_res
        OUTPUT_VARIABLE _dom_git_dirty_out
        ERROR_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    if(_dom_git_dirty_res EQUAL 0 AND NOT _dom_git_dirty_out STREQUAL "")
        set(DOM_GIT_DIRTY 1)
    endif()
endif()

set(DOM_BUILD_KIND "dev" CACHE STRING "Build lane kind (dev|ci|release|beta|rc|hotfix)")
set_property(CACHE DOM_BUILD_KIND PROPERTY STRINGS dev ci release beta rc hotfix)
if(DOM_BUILD_KIND STREQUAL "dev" AND DEFINED ENV{CI})
    string(TOLOWER "$ENV{CI}" _dom_ci_raw)
    if(NOT _dom_ci_raw STREQUAL "" AND NOT _dom_ci_raw STREQUAL "0" AND NOT _dom_ci_raw STREQUAL "false")
        set(DOM_BUILD_KIND "ci" CACHE STRING "Build lane kind (dev|ci|release|beta|rc|hotfix)" FORCE)
    endif()
endif()

set(DOM_BUILD_BII "${DOM_GIT_HASH_SHORT}")
if(DOM_BUILD_BII STREQUAL "" OR DOM_BUILD_BII STREQUAL "unknown")
    set(DOM_BUILD_BII "nogit")
endif()
if(DOM_GIT_DIRTY)
    set(DOM_BUILD_BII "${DOM_BUILD_BII}.dirty")
endif()

set(DOM_BUILD_GBN "none")
string(TIMESTAMP DOM_BUILD_TIMESTAMP "%Y-%m-%dT%H:%M:%SZ" UTC)
set(DOM_RELEASE_KINDS release beta rc hotfix)
set(DOM_IS_RELEASE_LANE OFF)
list(FIND DOM_RELEASE_KINDS "${DOM_BUILD_KIND}" _dom_release_kind_idx)
if(NOT _dom_release_kind_idx EQUAL -1)
    set(DOM_IS_RELEASE_LANE ON)
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

# Toolchain descriptor fields (build metadata).
set(_dom_tc_os "unknown")
if(WIN32)
    set(_dom_tc_os "winnt")
elseif(APPLE)
    set(_dom_tc_os "macosx")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Emscripten")
    set(_dom_tc_os "web")
elseif(ANDROID OR CMAKE_SYSTEM_NAME STREQUAL "Android")
    set(_dom_tc_os "android")
elseif(IOS OR CMAKE_SYSTEM_NAME STREQUAL "iOS")
    set(_dom_tc_os "ios")
elseif(CMAKE_SYSTEM_NAME MATCHES ".*BSD")
    set(_dom_tc_os "bsd")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(_dom_tc_os "linux")
elseif(DEFINED CMAKE_SYSTEM_NAME AND NOT CMAKE_SYSTEM_NAME STREQUAL "")
    string(TOLOWER "${CMAKE_SYSTEM_NAME}" _dom_tc_os)
endif()

set(_dom_tc_arch_raw "${CMAKE_SYSTEM_PROCESSOR}")
if(_dom_tc_arch_raw STREQUAL "")
    set(_dom_tc_arch_raw "${CMAKE_HOST_SYSTEM_PROCESSOR}")
endif()
string(TOLOWER "${_dom_tc_arch_raw}" _dom_tc_arch)
if(_dom_tc_arch MATCHES "^(amd64|x86_64|x64)$")
    set(_dom_tc_arch "x64")
elseif(_dom_tc_arch MATCHES "^(i[3-6]86|x86)$")
    set(_dom_tc_arch "x86")
elseif(_dom_tc_arch MATCHES "^(aarch64|arm64)$")
    set(_dom_tc_arch "arm64")
elseif(_dom_tc_arch MATCHES "^(wasm32)$")
    set(_dom_tc_arch "wasm")
elseif(_dom_tc_arch STREQUAL "")
    set(_dom_tc_arch "unknown")
endif()

set(_dom_tc_target "unknown")
if(NOT _dom_tc_os STREQUAL "unknown" AND NOT _dom_tc_arch STREQUAL "unknown")
    set(_dom_tc_target "${_dom_tc_os}-${_dom_tc_arch}")
endif()

set(_dom_tc_family "unknown")
if(MSVC AND CMAKE_C_COMPILER_ID STREQUAL "Clang")
    set(_dom_tc_family "clang-cl")
elseif(MSVC)
    set(_dom_tc_family "msvc")
elseif(MINGW OR MSYS)
    set(_dom_tc_family "mingw-w64")
elseif(CMAKE_C_COMPILER_ID STREQUAL "AppleClang")
    set(_dom_tc_family "apple-clang")
elseif(CMAKE_C_COMPILER_ID STREQUAL "Clang")
    set(_dom_tc_family "clang")
elseif(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    set(_dom_tc_family "gcc")
elseif(DEFINED CMAKE_C_COMPILER_ID AND NOT CMAKE_C_COMPILER_ID STREQUAL "")
    string(TOLOWER "${CMAKE_C_COMPILER_ID}" _dom_tc_family)
endif()

set(_dom_tc_version "unknown")
if(DEFINED CMAKE_C_COMPILER_VERSION AND NOT CMAKE_C_COMPILER_VERSION STREQUAL "")
    set(_dom_tc_version "${CMAKE_C_COMPILER_VERSION}")
endif()

set(_dom_tc_stdlib "${DOM_TOOLCHAIN_STDLIB}")
if(_dom_tc_stdlib STREQUAL "")
    if(MSVC)
        set(_dom_tc_stdlib "msvc-stl")
    elseif(CMAKE_C_COMPILER_ID STREQUAL "AppleClang")
        set(_dom_tc_stdlib "libc++")
    elseif(CMAKE_C_COMPILER_ID STREQUAL "Clang" AND APPLE)
        set(_dom_tc_stdlib "libc++")
    elseif(CMAKE_C_COMPILER_ID STREQUAL "Clang")
        set(_dom_tc_stdlib "libstdc++")
    elseif(CMAKE_C_COMPILER_ID STREQUAL "GNU")
        set(_dom_tc_stdlib "libstdc++")
    else()
        set(_dom_tc_stdlib "unknown")
    endif()
endif()

set(_dom_tc_runtime "${DOM_TOOLCHAIN_RUNTIME}")
if(_dom_tc_runtime STREQUAL "")
    if(WIN32)
        if(NOT DOM_CRT_POLICY STREQUAL "")
            set(_dom_tc_runtime "${DOM_CRT_POLICY}")
        elseif(DEFINED CMAKE_MSVC_RUNTIME_LIBRARY AND NOT CMAKE_MSVC_RUNTIME_LIBRARY STREQUAL "")
            if(CMAKE_MSVC_RUNTIME_LIBRARY MATCHES "DLL")
                set(_dom_tc_runtime "dynamic:msvc")
            else()
                set(_dom_tc_runtime "static:msvc")
            endif()
        else()
            set(_dom_tc_runtime "dynamic:msvc")
        endif()
    elseif(APPLE)
        set(_dom_tc_runtime "dynamic:macosx")
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        set(_dom_tc_runtime "dynamic:glibc")
    else()
        set(_dom_tc_runtime "unknown")
    endif()
endif()

set(_dom_tc_link "${DOM_TOOLCHAIN_LINK}")
if(_dom_tc_link STREQUAL "")
    if(_dom_tc_runtime MATCHES "static")
        set(_dom_tc_link "static")
    elseif(MINGW OR MSYS)
        if(DOMINIUM_STATIC_GNU_RUNTIME)
            set(_dom_tc_link "static")
        else()
            set(_dom_tc_link "dynamic")
        endif()
    else()
        set(_dom_tc_link "dynamic")
    endif()
endif()

set(_dom_tc_floor "unspecified")
if(DEFINED DOM_TARGET_OS_FAMILY AND NOT DOM_TARGET_OS_FAMILY STREQUAL "" AND
   DEFINED DOM_TARGET_OS_MIN AND NOT DOM_TARGET_OS_MIN STREQUAL "")
    set(_dom_tc_floor "${DOM_TARGET_OS_FAMILY}:${DOM_TARGET_OS_MIN}")
elseif(DEFINED DOM_TARGET_OS_FAMILY AND NOT DOM_TARGET_OS_FAMILY STREQUAL "")
    set(_dom_tc_floor "${DOM_TARGET_OS_FAMILY}:unspecified")
elseif(DEFINED DOM_TARGET_OS_MIN AND NOT DOM_TARGET_OS_MIN STREQUAL "")
    set(_dom_tc_floor "unspecified:${DOM_TARGET_OS_MIN}")
endif()

set(_dom_tc_config "unknown")
if(DEFINED DOM_BUILD_MODE AND NOT DOM_BUILD_MODE STREQUAL "")
    set(_dom_tc_config "${DOM_BUILD_MODE}")
elseif(DEFINED CMAKE_BUILD_TYPE AND NOT CMAKE_BUILD_TYPE STREQUAL "")
    set(_dom_tc_config "${CMAKE_BUILD_TYPE}")
elseif(CMAKE_CONFIGURATION_TYPES)
    set(_dom_tc_config "multi")
endif()

set(DOM_TOOLCHAIN_FAMILY "${_dom_tc_family}")
set(DOM_TOOLCHAIN_VERSION "${_dom_tc_version}")
set(DOM_TOOLCHAIN_STDLIB "${_dom_tc_stdlib}")
set(DOM_TOOLCHAIN_RUNTIME "${_dom_tc_runtime}")
set(DOM_TOOLCHAIN_LINK "${_dom_tc_link}")
set(DOM_TOOLCHAIN_OS "${_dom_tc_os}")
set(DOM_TOOLCHAIN_ARCH "${_dom_tc_arch}")
set(DOM_TOOLCHAIN_TARGET "${_dom_tc_target}")
set(DOM_TOOLCHAIN_OS_FLOOR "${_dom_tc_floor}")
set(DOM_TOOLCHAIN_CONFIG "${_dom_tc_config}")

set(_dom_force_build_id 0)
if(DOM_BUILD_KIND STREQUAL "dev" OR DOM_BUILD_KIND STREQUAL "ci")
    set(_dom_force_build_id 1)
endif()
if(_dom_force_build_id OR NOT DEFINED DOM_BUILD_ID OR DOM_BUILD_ID STREQUAL "" OR DOM_BUILD_ID STREQUAL "unknown")
    set(_dom_build_id "${DOM_BUILD_KIND}.${DOM_BUILD_BII}")
    set(DOM_BUILD_ID "${_dom_build_id}" CACHE STRING "Build identifier embedded into binaries" FORCE)
endif()

set(DOM_BUILD_STATE_FILE "${CMAKE_CURRENT_SOURCE_DIR}/.dominium_build_number")
set(DOM_BUILD_HEADER_FILE "${DOMINIUM_GENERATED_INCLUDE_DIR}/dominium/build_version.generated.h")
set(DOM_BUILD_NUMBER_FILE "${CMAKE_CURRENT_BINARY_DIR}/generated/build_number.txt")

add_custom_target(dom_update_build_number ALL
    COMMAND ${CMAKE_COMMAND}
        -DDOM_BUILD_NUMBER_BUMP=0
        -DSTATE_FILE=${DOM_BUILD_STATE_FILE}
        -DHEADER_FILE=${DOM_BUILD_HEADER_FILE}
        -DNUMBER_FILE=${DOM_BUILD_NUMBER_FILE}
        -DPROJECT_SEMVER=${DOM_PROJECT_SEMVER}
        -DDOM_BUILD_KIND=${DOM_BUILD_KIND}
        -DDOM_BUILD_BII=${DOM_BUILD_BII}
        -DDOM_BUILD_GBN=${DOM_BUILD_GBN}
        -DDOM_BUILD_ID=${DOM_BUILD_ID}
        -DDOM_BUILD_TIMESTAMP=${DOM_BUILD_TIMESTAMP}
        -P ${CMAKE_CURRENT_SOURCE_DIR}/setup/packages/scripts/update_build_number.cmake
    COMMENT "Refreshing build number header (no bump)"
)
add_custom_target(dom_bump_build_number
    COMMAND ${CMAKE_COMMAND}
        -DDOM_BUILD_NUMBER_BUMP=1
        -DSTATE_FILE=${DOM_BUILD_STATE_FILE}
        -DHEADER_FILE=${DOM_BUILD_HEADER_FILE}
        -DNUMBER_FILE=${DOM_BUILD_NUMBER_FILE}
        -DPROJECT_SEMVER=${DOM_PROJECT_SEMVER}
        -DDOM_BUILD_KIND=${DOM_BUILD_KIND}
        -DDOM_BUILD_BII=${DOM_BUILD_BII}
        -DDOM_BUILD_GBN=${DOM_BUILD_GBN}
        -DDOM_BUILD_ID=${DOM_BUILD_ID}
        -DDOM_BUILD_TIMESTAMP=${DOM_BUILD_TIMESTAMP}
        -P ${CMAKE_CURRENT_SOURCE_DIR}/setup/packages/scripts/update_build_number.cmake
    COMMENT "Bumping global build number"
)
set(DOM_TESTX_TIMEOUT "1200" CACHE STRING "Per-test timeout seconds for TestX gate")
set(_dom_testx_ctest_cmd ${CMAKE_CTEST_COMMAND} --output-on-failure)
if(DOM_TESTX_TIMEOUT)
    list(APPEND _dom_testx_ctest_cmd --timeout ${DOM_TESTX_TIMEOUT})
endif()
if(CMAKE_CONFIGURATION_TYPES)
    list(APPEND _dom_testx_ctest_cmd -C $<CONFIG>)
endif()
add_custom_target(testx_all
    COMMAND ${_dom_testx_ctest_cmd}
    COMMAND ${CMAKE_COMMAND}
        -DDOM_BUILD_NUMBER_BUMP=1
        -DSTATE_FILE=${DOM_BUILD_STATE_FILE}
        -DHEADER_FILE=${DOM_BUILD_HEADER_FILE}
        -DNUMBER_FILE=${DOM_BUILD_NUMBER_FILE}
        -DPROJECT_SEMVER=${DOM_PROJECT_SEMVER}
        -DDOM_BUILD_KIND=${DOM_BUILD_KIND}
        -DDOM_BUILD_BII=${DOM_BUILD_BII}
        -DDOM_BUILD_GBN=${DOM_BUILD_GBN}
        -DDOM_BUILD_ID=${DOM_BUILD_ID}
        -DDOM_BUILD_TIMESTAMP=${DOM_BUILD_TIMESTAMP}
        -P ${CMAKE_CURRENT_SOURCE_DIR}/setup/packages/scripts/update_build_number.cmake
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMENT "Run TestX and bump build number on success"
)
add_compile_definitions(DOM_BUILD_VERSION_GENERATED)
add_compile_definitions(DOMINO_VERSION_GENERATED)
add_compile_definitions(DOM_PRODUCT_VERSIONS_GENERATED)

file(MAKE_DIRECTORY "${DOMINIUM_GENERATED_INCLUDE_DIR}/domino")
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/config_base.h.in"
    "${DOMINIUM_GENERATED_INCLUDE_DIR}/domino/config_base.h"
    @ONLY
)
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/domino_version.generated.h.in"
    "${DOMINIUM_GENERATED_INCLUDE_DIR}/domino/version.generated.h"
    @ONLY
)
file(MAKE_DIRECTORY "${DOMINIUM_GENERATED_INCLUDE_DIR}/dominium")
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/product_versions.generated.h.in"
    "${DOMINIUM_GENERATED_INCLUDE_DIR}/dominium/product_versions.generated.h"
    @ONLY
)
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(DOM_TOOLCHAIN_DESCRIPTOR_JSON "${CMAKE_CURRENT_BINARY_DIR}/generated/toolchain_descriptor.json")
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchain_descriptor.json.in"
    "${DOM_TOOLCHAIN_DESCRIPTOR_JSON}"
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
option(DOM_DIST_SEED_RUNTIME "Generate minimal install state + home layout under dist leaf" ON)
set(DOM_DIST_INSTALL_TYPE "portable" CACHE STRING "Dist seed install type (portable|user|system)")
set(DOM_DIST_BUILD_CHANNEL "dev" CACHE STRING "Dist seed build channel")
dist_init(
    DIST_ROOT "${DOM_DIST_ROOT}"
    DIST_OS "${DOM_DIST_OS}"
    DIST_ARCH "${DOM_DIST_ARCH}"
    DIST_VARIANT "${DOM_DIST_VARIANT}"
)

file(MAKE_DIRECTORY
    "${CMAKE_SOURCE_DIR}/build/msvc-debug"
    "${CMAKE_SOURCE_DIR}/build/msvc-release"
    "${CMAKE_SOURCE_DIR}/build/msys2-debug"
    "${CMAKE_SOURCE_DIR}/build/msys2-release"
)

add_subdirectory(libs)
add_subdirectory(engine)
add_subdirectory(app)
add_subdirectory(libs/ui_backends/win32)
add_subdirectory(tools/ui_shared/src/ui_ir)
add_subdirectory(tools/ui_bind)
if(WIN32)
    if(NOT TARGET ui_bind_phase)
        add_custom_target(ui_bind_phase
            COMMAND ${CMAKE_COMMAND} -E echo "ui_bind_phase: tool_ui_bind target missing; UI bind phase cannot run."
            COMMAND ${CMAKE_COMMAND} -E false
        )
    endif()
endif()
if(DOM_BUILD_GAME)
    add_subdirectory(game)
    add_subdirectory(client)
    add_subdirectory(server)
    if(DOM_BUILD_TESTS)
        add_subdirectory(game/tests/phase6)
    endif()
endif()
if(DOM_BUILD_SETUP)
    add_subdirectory(setup)
endif()
if(DOM_BUILD_LAUNCHER)
    add_subdirectory(launcher)
endif()
if(DOM_BUILD_TOOLS)
    add_subdirectory(tools)
endif()

if(DOM_BUILD_TESTS)
    add_subdirectory(tests)
endif()

function(dom_add_existing_deps target)
    foreach(_dep IN LISTS ARGN)
        if(TARGET ${_dep})
            add_dependencies(${target} ${_dep})
        endif()
    endforeach()
endfunction()

add_custom_target(all_libs)
dom_add_existing_deps(all_libs
    appcore
    build_identity
    domino_engine
    dominium_game
    dominium_app_runtime
    domino_ui_ir
    launcher_core
    setup_core
    shared_ui_win32
)

add_custom_target(all_apps)
dom_add_existing_deps(all_apps
    dominium_client
    dominium_server
    launcher_cli
    launcher_tui
    launcher_gui
    setup_cli
    setup_tui
    setup_gui
)

add_custom_target(all_tools)
dom_add_existing_deps(all_tools
    tool_ui_bind
    domui_validate
    tool_ui_doc_annotate
    coredata_compile
    coredata_validate
)

add_custom_target(all_renderers)
dom_add_existing_deps(all_renderers domino_engine)

add_custom_target(all_runtime)
add_dependencies(all_runtime all_libs all_apps all_tools all_renderers)
if(TARGET build_identity AND TARGET dom_update_build_number)
    add_dependencies(build_identity dom_update_build_number)
endif()

if(DOM_PROJECTION)
    list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/ide")
    include(IdeCommon)
    include(IdeToolchainMatrix)
    include(IdeGenerateVs)
    include(IdeGenerateXcode)
    include(IdeGenerateLegacyVc6)
    include(IdeGenerateLegacyVc71)
    include(IdeGenerateCodeWarrior)
    include(IdeProjectionManifest)
    dom_ide_generate_projection()
endif()

function(dom_assert_no_link target)
    if(NOT TARGET ${target})
        return()
    endif()
    get_target_property(_dom_links ${target} LINK_LIBRARIES)
    if(_dom_links STREQUAL "LINK_LIBRARIES-NOTFOUND")
        set(_dom_links "")
    endif()
    get_target_property(_dom_iface_links ${target} INTERFACE_LINK_LIBRARIES)
    if(_dom_iface_links STREQUAL "INTERFACE_LINK_LIBRARIES-NOTFOUND")
        set(_dom_iface_links "")
    endif()
    set(_dom_all_links ${_dom_links} ${_dom_iface_links})
    foreach(_dom_forbid IN LISTS ARGN)
        list(FIND _dom_all_links ${_dom_forbid} _dom_idx)
        if(NOT _dom_idx EQUAL -1)
            message(FATAL_ERROR "Boundary violation: target '${target}' links forbidden target '${_dom_forbid}'.")
        endif()
    endforeach()
endfunction()

dom_assert_no_link(domino_engine
    dominium_game
    game::dominium
    libs_base
    libs_crypto
    libs_fsmodel
    libs_netproto
    libs_contracts
    libs::base
    libs::crypto
    libs::fsmodel
    libs::netproto
    libs::contracts
    launcher_core
    launcher::launcher
    setup_core
    setup::setup
    tools_shared
    tools::shared
    dominium-tools
    tools::host
)
dom_assert_no_link(dominium_game
    libs_base
    libs_crypto
    libs_fsmodel
    libs_netproto
    libs_contracts
    libs::base
    libs::crypto
    libs::fsmodel
    libs::netproto
    libs::contracts
    launcher_core
    launcher::launcher
    setup_core
    setup::setup
)

if(TARGET coredata_compile)
    add_custom_target(coredata_build
        COMMAND $<TARGET_FILE:coredata_compile>
            --input-root=${CMAKE_SOURCE_DIR}/data/core
            --output-pack-id=base_cosmo
            --output-version=${DOM_PROJECT_SEMVER}
            --output-root=${CMAKE_SOURCE_DIR}/repo/packs
            --emit-manifest=1
            --strict=1
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        DEPENDS coredata_compile
        COMMENT "Building coredata pack"
    )
endif()

if(WIN32 AND TARGET dominium-ui-editor)
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

if(WIN32 AND TARGET ui_scan_all AND NOT TARGET ui_capability_test)
    add_custom_target(ui_capability_test
        DEPENDS
            ui_scan_all
            ui_regen_launcher
            ui_regen_setup
            ui_validate_all
    )
endif()

if(DOM_BUILD_TESTS)
    if(TARGET launcher_cli)
        add_test(NAME launcher_help COMMAND $<TARGET_FILE:launcher_cli> --help)
    endif()
    if(TARGET setup_cli)
        add_test(NAME setup_help COMMAND $<TARGET_FILE:setup_cli> --help)
    endif()
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
        -DDOM_DIST_SEED_RUNTIME=${DOM_DIST_SEED_RUNTIME}
        -P ${CMAKE_SOURCE_DIR}/cmake/dominium_dist_meta.cmake
    DEPENDS ${_dom_dist_targets}
    COMMENT "Generating dist metadata"
)
if(TARGET dist_seed)
    add_dependencies(dist_meta dist_seed)
endif()

add_custom_target(verify_dist
    COMMAND ${CMAKE_COMMAND}
        -DDOM_DIST_ROOT=${DOM_DIST_ROOT}
        -DDOM_DIST_LEAF=${DOM_DIST_LEAF}
        -DDOM_DIST_VARIANT=${DOM_DIST_VARIANT}
        -DDOM_DIST_SEED_RUNTIME=${DOM_DIST_SEED_RUNTIME}
        -P ${CMAKE_SOURCE_DIR}/tools/validate_dist.cmake
    COMMENT "Validating dist layout"
)
add_dependencies(verify_dist dist_meta)

add_custom_target(validate_dist DEPENDS verify_dist)

set(DOM_PKG_ARCH "${DOM_DIST_ARCH}")
if(DOM_PKG_ARCH STREQUAL "x64")
    set(DOM_PKG_ARCH "x86_64")
elseif(DOM_PKG_ARCH STREQUAL "x86")
    set(DOM_PKG_ARCH "x86_32")
endif()

set(DOM_PKG_ABI "abi:${DOM_DIST_OS}:${DOM_TOOLCHAIN_FAMILY}")
if(WIN32 AND MSVC)
    set(DOM_PKG_ABI "abi:winnt:msvc-v180")
endif()

set(DOM_PKG_PLATFORM_ROOT "${DOM_DIST_ROOT}/pkg/${DOM_DIST_OS}/${DOM_PKG_ARCH}")
set(DOM_PKG_OUTPUT_DIR "${DOM_PKG_PLATFORM_ROOT}/pkgs")
set(DOM_PKG_INDEX_DIR "${DOM_PKG_PLATFORM_ROOT}/index")
set(DOM_PKG_INDEX_JSON "${DOM_PKG_INDEX_DIR}/pkg_index.json")
set(DOM_PKG_INDEX_TLV "${DOM_PKG_INDEX_DIR}/pkg_index.tlv")
set(DOM_DIST_META_PLATFORM_ROOT "${DOM_DIST_ROOT}/meta/${DOM_DIST_OS}/${DOM_PKG_ARCH}")
set(DOM_BUILD_MANIFEST_JSON "${DOM_DIST_META_PLATFORM_ROOT}/build_manifest.json")
set(DOM_BUILD_MANIFEST_TLV "${DOM_DIST_META_PLATFORM_ROOT}/build_manifest.tlv")

add_custom_target(pkg_pack_all
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/distribution/pkg_pack_all.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --build-bin ${CMAKE_BINARY_DIR}/bin
        --build-lib ${CMAKE_BINARY_DIR}/lib
        --dist-tools ${DOM_DIST_BIN_TOOLS}
        --out-dir ${DOM_PKG_OUTPUT_DIR}
        --platform ${DOM_DIST_OS}
        --arch ${DOM_PKG_ARCH}
        --abi ${DOM_PKG_ABI}
        --pkg-version ${DOM_PROJECT_SEMVER}
    DEPENDS ${_dom_dist_targets}
    COMMENT "Packing dompkg artifacts into dist/pkg"
)
if(WIN32 AND TARGET ui_bind_phase)
    add_dependencies(pkg_pack_all ui_bind_phase)
endif()

add_custom_target(pkg_verify_all
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/distribution/pkg_verify_all.py
        --pkg-dir ${DOM_PKG_OUTPUT_DIR}
    DEPENDS pkg_pack_all
    COMMENT "Verifying dompkg artifacts"
)

add_custom_target(pkg_index_all
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/distribution/tool_pkg_index.py
        --pkg-dir ${DOM_PKG_OUTPUT_DIR}
        --out ${DOM_PKG_INDEX_JSON}
        --tlv-out ${DOM_PKG_INDEX_TLV}
        --verify
    DEPENDS pkg_pack_all
    COMMENT "Generating package index artifacts"
)

add_custom_target(dist_build_manifest
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/distribution/build_manifest.py
        --index-json ${DOM_PKG_INDEX_JSON}
        --out-json ${DOM_BUILD_MANIFEST_JSON}
        --out-tlv ${DOM_BUILD_MANIFEST_TLV}
        --build-id ${DOM_BUILD_ID}
        --platform ${DOM_DIST_OS}
        --arch ${DOM_PKG_ARCH}
        --abi ${DOM_PKG_ABI}
        --compression-default deflate
        --compression-required deflate
        --compression-optional zstd
        --zstd-threshold-bytes 1073741824
        --signature-policy dev_optional
    DEPENDS pkg_index_all
    COMMENT "Generating distribution build manifest"
)

add_custom_target(setup_install_smoke
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/distribution/setup_install_smoke.py
        --repo-root ${CMAKE_SOURCE_DIR}
    COMMENT "Running deterministic setup smoke"
)

add_custom_target(launcher_run_smoke
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/distribution/launcher_run_smoke.py
        --repo-root ${CMAKE_SOURCE_DIR}
    COMMENT "Running deterministic launcher smoke"
)

add_custom_target(smoke_run_apps
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/ci/smoke_run_apps.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --build-root ${CMAKE_BINARY_DIR}
        --output ${CMAKE_BINARY_DIR}/smoke_run_apps.json
    DEPENDS all_runtime
    COMMENT "Running bounded application smoke checks"
)

add_custom_target(install_from_pkg_cache
    COMMAND ${CMAKE_COMMAND} -E echo "install_from_pkg_cache: delegated to setup_install_smoke"
    DEPENDS setup_install_smoke
)

set(DOM_VERIFY_FAST_TIMEOUT "300" CACHE STRING "Per-test timeout seconds for verify_fast")
set(_dom_verify_fast_ctest_cmd ${CMAKE_CTEST_COMMAND} --output-on-failure)
if(DOM_VERIFY_FAST_TIMEOUT)
    list(APPEND _dom_verify_fast_ctest_cmd --timeout ${DOM_VERIFY_FAST_TIMEOUT})
endif()
if(CMAKE_CONFIGURATION_TYPES)
    list(APPEND _dom_verify_fast_ctest_cmd -C $<CONFIG>)
endif()

add_custom_target(verify_fast
    COMMAND ${_dom_verify_fast_ctest_cmd} -L smoke
    COMMAND ${_dom_verify_fast_ctest_cmd} -L portability
    COMMAND ${_dom_verify_fast_ctest_cmd} -L buildmeta
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMENT "Running bounded verification suite (fast lane)"
)
add_dependencies(verify_fast
    all_quality_gates
    check_arch
    check_abi_boundaries
    check_ui_shell_purity
    smoke_run_apps
)
if(WIN32 AND TARGET ui_bind_phase)
    add_dependencies(verify_fast ui_bind_phase)
endif()

add_custom_target(verify_full DEPENDS verify_fast testx_all)

add_custom_target(dom_dist_release_lane_guard
    COMMAND ${CMAKE_COMMAND}
        -DDOM_BUILD_KIND=${DOM_BUILD_KIND}
        -DDOM_BUILD_GBN=${DOM_BUILD_GBN}
        -P ${CMAKE_SOURCE_DIR}/cmake/check_release_lane.cmake
    COMMENT "Validating release lane gate for dist targets"
)

add_custom_target(dist_pack DEPENDS dom_dist_release_lane_guard pkg_pack_all)
add_custom_target(dist_index DEPENDS dom_dist_release_lane_guard pkg_index_all)
add_custom_target(dist_verify DEPENDS dom_dist_release_lane_guard pkg_verify_all)
add_custom_target(dist_smoke DEPENDS dom_dist_release_lane_guard setup_install_smoke launcher_run_smoke)
add_custom_target(dist_all DEPENDS dist_pack dist_index dist_verify dist_build_manifest dist_smoke)

set(CPACK_PACKAGE_NAME "dominium")
set(CPACK_PACKAGE_VENDOR "Dominium")
set(CPACK_PACKAGE_CONTACT "support@dominium.invalid")
set(CPACK_PACKAGE_VERSION "0.0.0")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "${CPACK_PACKAGE_CONTACT}")
set(CPACK_DEBIAN_PACKAGE_SECTION "games")
set(CPACK_RPM_PACKAGE_LICENSE "MIT")
set(CPACK_RPM_PACKAGE_URL "https://example.com/dominium")
include(CPack)

if(DOM_BUILD_TESTS)
    dom_apply_default_test_labels()
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
