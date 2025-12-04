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
    add_compile_options(
        /W4
        /WX-
        /D_CRT_SECURE_NO_WARNINGS
    )
else()
    add_compile_options(
        -Wall
        -Wextra
        -Wpedantic
        -Wno-unused-parameter
    )
endif()

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
# 5. SUBDIRECTORIES (NO GLOBBING, EXPLICIT SOURCES)
# ---------------------------------------------------------------------
add_subdirectory(engine/core)
add_subdirectory(engine/sim)
add_subdirectory(engine/render)
add_subdirectory(engine/audio)
add_subdirectory(engine/platform/win32)
add_subdirectory(engine/ui)

# ---------------------------------------------------------------------
# 6. ENGINE AGGREGATE LIB
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
# 7. GAME TARGETS (MVP: CLIENT, SERVER, LAUNCHER)
# ---------------------------------------------------------------------
add_subdirectory(game/client)
add_subdirectory(game/server)
add_subdirectory(game/launcher)
add_subdirectory(packaging)

# ---------------------------------------------------------------------
# 8. TOOLS AND TESTS
# ---------------------------------------------------------------------
add_subdirectory(tools)
add_subdirectory(tests)

# ---------------------------------------------------------------------
# 9. STATUS
# ---------------------------------------------------------------------
message(STATUS "Dominium build summary")
message(STATUS "  DOM_PLATFORM            = ${DOM_PLATFORM}")
message(STATUS "  DOM_BUILD_MODE          = ${DOM_BUILD_MODE}")
message(STATUS "  DOM_CANONICAL_UPS       = ${DOM_CANONICAL_UPS}")
message(STATUS "  Backends: DX9=${DOM_BACKEND_DX9} GL1=${DOM_BACKEND_GL1} GL2=${DOM_BACKEND_GL2} VECTOR2D=${DOM_BACKEND_VECTOR2D} SDL2=${DOM_BACKEND_SDL2}")
message(STATUS "  Audio=${DOM_ENABLE_AUDIO} Net=${DOM_ENABLE_NET}")
