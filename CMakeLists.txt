# =====================================================================
# Dominium — Root CMakeLists.txt
# Deterministic, multi-target, multi-platform build configuration
# =====================================================================
cmake_minimum_required(VERSION 3.16)

# ---------------------------------------------------------------------
# 1. PROJECT METADATA
# ---------------------------------------------------------------------
project(Dominium
    VERSION 0.1.0
    LANGUAGES C CXX
)

# Enforce strict C89 / C++98 across all engine and game targets.
set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Disable in-source builds (enforce /build).
if("${CMAKE_SOURCE_DIR}" STREQUAL "${CMAKE_BINARY_DIR}")
    message(FATAL_ERROR "In-source builds are forbidden. Use a separate build directory.")
endif()

# ---------------------------------------------------------------------
# 2. GLOBAL OPTIONS / SWITCHES
# ---------------------------------------------------------------------
option(DOM_BUILD_ENGINE_ONLY          "Build engine only, no game client/server"         OFF)
option(DOM_BUILD_CLIENT               "Build game client binary"                        ON)
option(DOM_BUILD_SERVER               "Build dedicated server binary"                   ON)
option(DOM_BUILD_TOOLS                "Build tools (editor, devkit, pipelines)"         ON)
option(DOM_BUILD_TESTS                "Build tests (unit, integration, replay)"         ON)
option(DOM_ENABLE_NET                 "Enable networking support"                       ON)
option(DOM_ENABLE_AUDIO               "Enable audio backends"                           ON)
option(DOM_ENABLE_GL1                 "Enable OpenGL 1.x renderer backend"              ON)
option(DOM_ENABLE_GL2                 "Enable OpenGL 2.x renderer backend"              ON)
option(DOM_ENABLE_DX9                 "Enable DirectX 9 renderer backend (Windows)"     ON)
option(DOM_ENABLE_DX11                "Enable DirectX 11 renderer backend (Windows)"    OFF)
option(DOM_ENABLE_SOFTWARE_RENDER     "Enable software/vector renderer backend"         ON)
option(DOM_ENABLE_EDITORS             "Build map/world/blueprint editors"               ON)
option(DOM_STRICT_DETERMINISM_CHECKS  "Enable additional determinism diagnostics"       ON)
option(DOM_ENABLE_LTO                 "Enable link-time optimization where available"   OFF)

# Retro / legacy ports are built via separate build systems; CMake is for
# modern platforms only (Win32/Win64, Linux, macOS, etc).
option(DOM_BUILD_RETRO_STUBS          "Build stubs/helpers for retro ports"             ON)

# ---------------------------------------------------------------------
# 3. GLOBAL COMPILER / WARNING POLICY
# ---------------------------------------------------------------------
include(CheckCCompilerFlag)
include(CheckCXXCompilerFlag)

macro(dom_add_flag_if_supported _lang _flag)
    if("${_lang}" STREQUAL "C")
        string(REPLACE "-" "_" _safe "${_flag}")
        string(REPLACE "=" "_" _safe "${_safe}")
        set(_var "HAVE_FLAG_C_${_safe}")
        check_c_compiler_flag("${_flag}" ${_var})
        if(${_var})
            add_compile_options("$<$<COMPILE_LANGUAGE:C>:${_flag}>")
        endif()
    elseif("${_lang}" STREQUAL "CXX")
        string(REPLACE "-" "_" _safe "${_flag}")
        string(REPLACE "=" "_" _safe "${_safe}")
        set(_var "HAVE_FLAG_CXX_${_safe}")
        check_cxx_compiler_flag("${_flag}" ${_var})
        if(${_var})
            add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:${_flag}>")
        endif()
    endif()
endmacro()

# Warnings: strict, but avoid compiler-specific breakage.
if(MSVC)
    add_compile_options(
        /W4           # high warning level
        /WX-          # do NOT treat warnings as errors by default
        /permissive-  # standard-conformance mode
        /D_CRT_SECURE_NO_WARNINGS
    )
else()
    dom_add_flag_if_supported(C   "-Wall")
    dom_add_flag_if_supported(C   "-Wextra")
    dom_add_flag_if_supported(C   "-Wpedantic")
    dom_add_flag_if_supported(C   "-Wshadow")
    dom_add_flag_if_supported(C   "-Wstrict-prototypes")
    dom_add_flag_if_supported(C   "-Wno-unused-parameter")

    dom_add_flag_if_supported(CXX "-Wall")
    dom_add_flag_if_supported(CXX "-Wextra")
    dom_add_flag_if_supported(CXX "-Wpedantic")
    dom_add_flag_if_supported(CXX "-Wshadow")
    dom_add_flag_if_supported(CXX "-Wnon-virtual-dtor")
endif()

# Optional LTO
if(DOM_ENABLE_LTO)
    include(CheckIPOSupported)
    check_ipo_supported(RESULT ipo_supported OUTPUT ipo_error)
    if(ipo_supported)
        set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ON)
    else()
        message(WARNING "LTO requested but not supported: ${ipo_error}")
    endif()
endif()

# ---------------------------------------------------------------------
# 4. GLOBAL DEFINES (DETERMINISM + PLATFORM)
# ---------------------------------------------------------------------
add_compile_definitions(
    DOM_BUILD_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    DOM_BUILD_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    DOM_BUILD_VERSION_PATCH=${PROJECT_VERSION_PATCH}
)

if(DOM_STRICT_DETERMINISM_CHECKS)
    add_compile_definitions(DOM_STRICT_DETERMINISM=1)
else()
    add_compile_definitions(DOM_STRICT_DETERMINISM=0)
endif()

if(WIN32)
    add_compile_definitions(DOM_PLATFORM_WIN32=1)
elseif(APPLE)
    add_compile_definitions(DOM_PLATFORM_MACOS=1)
elseif(UNIX)
    add_compile_definitions(DOM_PLATFORM_LINUX=1)
else()
    add_compile_definitions(DOM_PLATFORM_UNKNOWN=1)
endif()

if(DOM_ENABLE_NET)
    add_compile_definitions(DOM_FEATURE_NET=1)
else()
    add_compile_definitions(DOM_FEATURE_NET=0)
endif()

if(DOM_ENABLE_AUDIO)
    add_compile_definitions(DOM_FEATURE_AUDIO=1)
else()
    add_compile_definitions(DOM_FEATURE_AUDIO=0)
endif()

# Render backend feature flags
add_compile_definitions(
    DOM_RENDER_GL1=$<BOOL:${DOM_ENABLE_GL1}>
    DOM_RENDER_GL2=$<BOOL:${DOM_ENABLE_GL2}>
    DOM_RENDER_DX9=$<BOOL:${DOM_ENABLE_DX9}>
    DOM_RENDER_DX11=$<BOOL:${DOM_ENABLE_DX11}>
    DOM_RENDER_SOFTWARE=$<BOOL:${DOM_ENABLE_SOFTWARE_RENDER}>
)

# ---------------------------------------------------------------------
# 5. GLOBAL INCLUDE PATHS
# ---------------------------------------------------------------------
include_directories(
    ${CMAKE_SOURCE_DIR}/engine
    ${CMAKE_SOURCE_DIR}/engine/core
    ${CMAKE_SOURCE_DIR}/engine/sim
    ${CMAKE_SOURCE_DIR}/engine/render
    ${CMAKE_SOURCE_DIR}/engine/audio
    ${CMAKE_SOURCE_DIR}/engine/net
    ${CMAKE_SOURCE_DIR}/engine/ui
    ${CMAKE_SOURCE_DIR}/engine/platform
    ${CMAKE_SOURCE_DIR}/game
    ${CMAKE_SOURCE_DIR}/external/include
)

# ---------------------------------------------------------------------
# 6. THIRD-PARTY LIBRARIES (DECLARATIVE)
# ---------------------------------------------------------------------
add_subdirectory(external)

# external/CMakeLists.txt is responsible for:
# - Declaring imported targets (e.g., SDL2::SDL2, etc.)
# - Setting any required compile definitions for external libs
# - NEVER leaking platform headers into /engine core

# ---------------------------------------------------------------------
# 7. ENGINE TARGETS
# ---------------------------------------------------------------------
add_subdirectory(engine)

# /engine/CMakeLists.txt must:
# - Create STATIC libraries for:
#   * dom_core      (core utilities, logging, mem, rng, fixed-point)
#   * dom_sim       (deterministic simulation)
#   * dom_render    (renderer abstraction + backends)
#   * dom_audio     (audio abstraction)
#   * dom_net       (network protocol)
#   * dom_ui        (UI primitives)
#   * dom_platform  (per-OS platform layer)
# - Expose them as:
#   * dom_engine_full (INTERFACE / OBJECT meta-target aggregating all)

# ---------------------------------------------------------------------
# 8. GAME TARGETS (CLIENT, SERVER, LAUNCHER)
# ---------------------------------------------------------------------
if(NOT DOM_BUILD_ENGINE_ONLY)
    add_subdirectory(game)

    # /game/CMakeLists.txt must:
    # - Define:
    #   * dom_client  (GUI client)
    #   * dom_server  (headless server)
    #   * dom_launcher (optional launcher/selector)
    # - Link them to dom_engine_full and relevant third-party libs
endif()

# ---------------------------------------------------------------------
# 9. TOOLS (EDITOR, DEVKIT, PIPELINE)
# ---------------------------------------------------------------------
if(DOM_BUILD_TOOLS)
    add_subdirectory(tools)

    # /tools/CMakeLists.txt must:
    # - Build editor binaries (map/world/blueprint)
    # - Build devkit utilities for mods
    # - Build asset pipeline tools (import/convert/pack)
    # - Ensure no determinism-critical logic lives only in tools
endif()

# ---------------------------------------------------------------------
# 10. TESTS (UNIT, INTEGRATION, REPLAY)
# ---------------------------------------------------------------------
if(DOM_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)

    # /tests/CMakeLists.txt must:
    # - Define unit test executables
    # - Define integration/replay determinism tests
    # - Register tests with ctest
endif()

# ---------------------------------------------------------------------
# 11. PACKAGING / INSTALL RULES (MODERN ONLY)
# ---------------------------------------------------------------------
add_subdirectory(packaging)

# /package/CMakeLists.txt must:
# - Define install targets for:
#   * dom_client, dom_server, dom_launcher
#   * engine DLLs/shared libs (if any)
#   * data packs under appropriate paths
# - Provide CPACK configuration for modern OS installers
# - Retro image layouts handled separately under /package/retro

# ---------------------------------------------------------------------
# 12. SCRIPTS / META AUTOMATION
# ---------------------------------------------------------------------
add_subdirectory(scripts)

# /scripts/CMakeLists.txt should:
# - Expose optional helper targets (lint, format, codegen, regen-specs)
# - Not be required for basic build

# ---------------------------------------------------------------------
# 13. PORTS (RETRO / ALT TARGET STUBS)
# ---------------------------------------------------------------------
if(DOM_BUILD_RETRO_STUBS)
    add_subdirectory(ports)

    # /ports/CMakeLists.txt:
    # - Does not build full retro binaries
    # - Builds small helper libs/tools for retro projects
    # - Keeps retro build systems isolated (e.g. .mak, .dsp, .mcp)
endif()

# ---------------------------------------------------------------------
# 14. SUMMARY
# ---------------------------------------------------------------------
message(STATUS "---------------------------------------------------")
message(STATUS " Dominium build configuration")
message(STATUS "   Version         : ${PROJECT_VERSION}")
message(STATUS "   Engine only     : ${DOM_BUILD_ENGINE_ONLY}")
message(STATUS "   Client          : ${DOM_BUILD_CLIENT}")
message(STATUS "   Server          : ${DOM_BUILD_SERVER}")
message(STATUS "   Tools           : ${DOM_BUILD_TOOLS}")
message(STATUS "   Tests           : ${DOM_BUILD_TESTS}")
message(STATUS "   Net             : ${DOM_ENABLE_NET}")
message(STATUS "   Audio           : ${DOM_ENABLE_AUDIO}")
message(STATUS "   GL1             : ${DOM_ENABLE_GL1}")
message(STATUS "   GL2             : ${DOM_ENABLE_GL2}")
message(STATUS "   DX9             : ${DOM_ENABLE_DX9}")
message(STATUS "   DX11            : ${DOM_ENABLE_DX11}")
message(STATUS "   Software render : ${DOM_ENABLE_SOFTWARE_RENDER}")
message(STATUS "   Strict determin.: ${DOM_STRICT_DETERMINISM_CHECKS}")
message(STATUS "---------------------------------------------------")