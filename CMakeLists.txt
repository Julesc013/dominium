# =====================================================================
# Dominium — Root CMakeLists.txt (Deterministic, MVP-focused)
# =====================================================================
cmake_minimum_required(VERSION 3.15)

project(Dominium
    VERSION 0.1.0
    LANGUAGES C CXX
)

# ---------------------------------------------------------------------
# 0. GLOBAL LANGUAGE + STANDARD POLICY (C89 / C++98)
# ---------------------------------------------------------------------
set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------
# 1. BUILD MODES (Debug / Release / DeterministicRelease)
# ---------------------------------------------------------------------
if(NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_CONFIGURATION_TYPES "Debug;Release;DeterministicRelease" CACHE STRING "" FORCE)
endif()

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    # Default to DeterministicRelease; allow overriding via -DDOM_BUILD_MODE=...
    set(CMAKE_BUILD_TYPE "${DOM_BUILD_MODE}" CACHE STRING "Build type" FORCE)
endif()

set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -DDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -DDEBUG")

if(MSVC)
    set(CMAKE_C_FLAGS_DETERMINISTICRELEASE "/O2 /fp:precise /GR- /EHsc-")
    set(CMAKE_CXX_FLAGS_DETERMINISTICRELEASE "/O2 /fp:precise /GR- /EHsc-")
else()
    set(CMAKE_C_FLAGS_DETERMINISTICRELEASE "-O2 -ffloat-store -fno-fast-math -fno-unsafe-math-optimizations -fno-strict-aliasing")
    set(CMAKE_CXX_FLAGS_DETERMINISTICRELEASE "-O2 -ffloat-store -fno-fast-math -fno-unsafe-math-optimizations -fno-strict-aliasing")
endif()

add_compile_definitions(
    $<$<CONFIG:Debug>:DOM_BUILD_MODE_DEBUG=1>
    $<$<CONFIG:Release>:DOM_BUILD_MODE_RELEASE=1>
    $<$<CONFIG:DeterministicRelease>:DOM_BUILD_MODE_DETERMINISTIC=1>
)

# ---------------------------------------------------------------------
# 2. CONFIG OPTIONS (PLATFORM + BACKENDS + UPS)
# ---------------------------------------------------------------------
set(DOM_PLATFORM "win32" CACHE STRING "Platform backend (win32;win32_sdl2;posix_sdl2;macos_cocoa;retro)")
set_property(CACHE DOM_PLATFORM PROPERTY STRINGS win32 win32_sdl2 posix_sdl2 macos_cocoa retro)

set(DOM_BUILD_MODE "DeterministicRelease" CACHE STRING "Dominium build mode (Debug|Release|DeterministicRelease)")
set_property(CACHE DOM_BUILD_MODE PROPERTY STRINGS Debug Release DeterministicRelease)

set(DOM_CANONICAL_UPS "60" CACHE STRING "Canonical UPS target for determinism (see BUILDING.md)")

option(DOM_BACKEND_DX9       "Enable DirectX 9 renderer backend" ON)
option(DOM_BACKEND_GL1       "Enable OpenGL 1.x renderer backend" ON)
option(DOM_BACKEND_GL2       "Enable OpenGL 2.x renderer backend" ON)
option(DOM_BACKEND_VECTOR2D  "Enable vector-only renderer backend" ON)
option(DOM_BACKEND_SDL2      "Enable SDL2 platform/audio glue" ON)

option(DOM_ENABLE_AUDIO      "Enable audio subsystem" ON)
option(DOM_ENABLE_NET        "Enable networking subsystem" ON)

# ---------------------------------------------------------------------
# 3. WARNING POLICY (COMPATIBLE WITH MSVC 2010 / GCC 4.x)
# ---------------------------------------------------------------------
if(MSVC)
    set(_dom_warning_flags
        /W4
        /WX-
        /D_CRT_SECURE_NO_WARNINGS
        /permissive-
        $<$<COMPILE_LANGUAGE:CXX>:/GR->
        $<$<COMPILE_LANGUAGE:CXX>:/D_HAS_EXCEPTIONS=0>
    )
else()
    set(_dom_warning_flags
        -Wall
        -Wextra
        -Wpedantic
        -Wno-unused-parameter
        $<$<COMPILE_LANGUAGE:C>:-Wdeclaration-after-statement>
        $<$<COMPILE_LANGUAGE:C>:-Wvla>
        $<$<COMPILE_LANGUAGE:C>:-Wlong-long>
        $<$<AND:$<COMPILE_LANGUAGE:C>,$<C_COMPILER_ID:Clang>>:-Wc99-extensions>
        $<$<COMPILE_LANGUAGE:CXX>:-Wlong-long>
        $<$<AND:$<COMPILE_LANGUAGE:CXX>,$<CXX_COMPILER_ID:Clang>>:-Wc++98-compat-pedantic>
        $<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>
        $<$<COMPILE_LANGUAGE:CXX>:-fno-rtti>
    )
endif()

add_compile_options(${_dom_warning_flags})

# ---------------------------------------------------------------------
# 4. TARGET-SCOPED DEFINES
# ---------------------------------------------------------------------
add_compile_definitions(
    DOM_CANONICAL_UPS=${DOM_CANONICAL_UPS}
    DOM_RENDER_DX9=$<BOOL:${DOM_BACKEND_DX9}>
    DOM_RENDER_GL1=$<BOOL:${DOM_BACKEND_GL1}>
    DOM_RENDER_GL2=$<BOOL:${DOM_BACKEND_GL2}>
    DOM_RENDER_VECTOR2D=$<BOOL:${DOM_BACKEND_VECTOR2D}>
    DOM_USE_SDL2=$<BOOL:${DOM_BACKEND_SDL2}>
    DOM_FEATURE_AUDIO=$<BOOL:${DOM_ENABLE_AUDIO}>
    DOM_FEATURE_NET=$<BOOL:${DOM_ENABLE_NET}>
)

if(DOM_PLATFORM STREQUAL "win32" OR DOM_PLATFORM STREQUAL "win32_sdl2")
    add_compile_definitions(DOM_PLATFORM_WIN32=1)
elseif(DOM_PLATFORM STREQUAL "posix_sdl2")
    add_compile_definitions(DOM_PLATFORM_LINUX=1)
elseif(DOM_PLATFORM STREQUAL "macos_cocoa")
    add_compile_definitions(DOM_PLATFORM_MACOS=1)
else()
    add_compile_definitions(DOM_PLATFORM_RETRO=1)
endif()

# ---------------------------------------------------------------------
# 5. BUILD METADATA (GLOBAL BUILD NUMBER)
# ---------------------------------------------------------------------
set(DOM_GENERATED_DIR "${CMAKE_BINARY_DIR}/generated")
set(DOM_BUILD_HEADER "${DOM_GENERATED_DIR}/dom_build_version.h")
set(DOM_BUILD_NUMBER_FILE "${DOM_GENERATED_DIR}/build_number.txt")
set(DOM_BUILD_STATE_FILE "${CMAKE_SOURCE_DIR}/.dominium_build_number")

add_custom_target(dom_build_metadata ALL
    COMMAND ${CMAKE_COMMAND} -E make_directory "${DOM_GENERATED_DIR}"
    COMMAND ${CMAKE_COMMAND}
        -DSTATE_FILE=${DOM_BUILD_STATE_FILE}
        -DHEADER_FILE=${DOM_BUILD_HEADER}
        -DNUMBER_FILE=${DOM_BUILD_NUMBER_FILE}
        -DPROJECT_SEMVER=${PROJECT_VERSION}
        -P ${CMAKE_SOURCE_DIR}/scripts/update_build_number.cmake
    BYPRODUCTS "${DOM_BUILD_HEADER}" "${DOM_BUILD_NUMBER_FILE}"
    COMMENT "Updating global Dominium build number"
    VERBATIM
)

# ---------------------------------------------------------------------
# 6. SUBDIRECTORIES (NO GLOBBING, EXPLICIT SOURCES)
# ---------------------------------------------------------------------
add_subdirectory(engine/core)
add_subdirectory(engine/sim)
add_subdirectory(engine/render)
add_subdirectory(engine/audio)
add_subdirectory(engine/platform/win32)
add_subdirectory(engine/ui)

# ---------------------------------------------------------------------
# 7. ENGINE AGGREGATE LIB
# ---------------------------------------------------------------------
add_library(dom_engine STATIC engine/dom_engine_stub.c)
target_link_libraries(dom_engine
    PUBLIC
        dom_core
        dom_sim
        dom_render
        dom_audio
        dom_ui
        dom_platform_win32
)
target_include_directories(dom_engine PUBLIC ${CMAKE_SOURCE_DIR}/engine)

# ---------------------------------------------------------------------
# 8. GAME TARGETS (MVP: CLIENT, SERVER, LAUNCHER)
# ---------------------------------------------------------------------
add_subdirectory(game/client)
add_subdirectory(game/server)
add_subdirectory(game/launcher)
add_subdirectory(packaging)

# ---------------------------------------------------------------------
# 9. TOOLS AND TESTS
# ---------------------------------------------------------------------
add_subdirectory(tools)
add_subdirectory(tests)

# ---------------------------------------------------------------------
# 10. BUILD NUMBER DEPENDENCIES
# ---------------------------------------------------------------------
function(dom_require_build_number target_name)
    if(TARGET ${target_name})
        add_dependencies(${target_name} dom_build_metadata)
    endif()
endfunction()

dom_require_build_number(dom_core)
dom_require_build_number(dom_sim)
dom_require_build_number(dom_render)
dom_require_build_number(dom_audio)
dom_require_build_number(dom_platform_win32)
dom_require_build_number(dom_ui)
dom_require_build_number(dom_engine)
dom_require_build_number(dom_client)
dom_require_build_number(dom_server)
dom_require_build_number(dom_tests)
dom_require_build_number(dom_tools_editor)
dom_require_build_number(dom_launcher-win32-software)
dom_require_build_number(dom_launcher-posix-sdl2-software)
dom_require_build_number(dom_launcher-macosx-software)

# ---------------------------------------------------------------------
# 11. STATUS
# ---------------------------------------------------------------------
message(STATUS "Dominium build summary")
message(STATUS "  DOM_PLATFORM            = ${DOM_PLATFORM}")
message(STATUS "  DOM_BUILD_MODE          = ${DOM_BUILD_MODE}")
message(STATUS "  DOM_CANONICAL_UPS       = ${DOM_CANONICAL_UPS}")
message(STATUS "  Backends: DX9=${DOM_BACKEND_DX9} GL1=${DOM_BACKEND_GL1} GL2=${DOM_BACKEND_GL2} VECTOR2D=${DOM_BACKEND_VECTOR2D} SDL2=${DOM_BACKEND_SDL2}")
message(STATUS "  Audio=${DOM_ENABLE_AUDIO} Net=${DOM_ENABLE_NET}")
