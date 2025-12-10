cmake_minimum_required(VERSION 3.16)

set(DOMINO_CORE_SOURCES
    dnumeric.c
    dworld.c
    dfield.c
    daggregate.c
    dorbit.c
    dbody.c
    dspace_env.c
    dspace_graph.c
    dclimate.c
    dweather.c
    dhydro.c
    dbiome.c
    dvehicle.c
    dtransport.c
    dmatter.c
    dnet.c
    denergy.c
    dzone.c
    dactor.c
    dknowledge.c
    djob.c
    deconomy.c
    dsim.c
    dmachine.c
    drecipe.c
    dblueprint.c
    dresearch.c
)

add_library(domino_core STATIC ${DOMINO_CORE_SOURCES})
target_include_directories(domino_core
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_compile_features(domino_core PRIVATE c_std_90)

option(DOMINO_USE_SDL2_BACKEND "Use SDL2 dsys backend" OFF)
option(DOMINO_USE_SDL1_BACKEND "Use SDL1 dsys backend" OFF)
option(DOMINO_USE_X11_BACKEND "Use X11 dsys backend" OFF)
option(DOMINO_USE_WAYLAND_BACKEND "Use Wayland dsys backend" OFF)
option(DOMINO_USE_POSIX_BACKEND "Use POSIX headless dsys backend" OFF)
option(DOMINO_USE_DOS16_BACKEND "Use DOS16 dsys backend" OFF)
option(DOMINO_USE_DOS32_BACKEND "Use DOS32 dsys backend" OFF)
option(DOMINO_USE_WIN16_BACKEND "Use Win16 dsys backend" OFF)
option(DOMINO_USE_CPM86_BACKEND "Use CP/M-86 dsys backend" OFF)
option(DSYS_BACKEND_POSIX "Alias for enabling the POSIX dsys backend" OFF)
option(DSYS_BACKEND_SDL1 "Alias for enabling the SDL1 dsys backend" OFF)
option(DOMINO_USE_COCOA_BACKEND "Use macOS Cocoa dsys backend" OFF)
option(DSYS_BACKEND_COCOA "Alias for enabling the macOS Cocoa dsys backend" OFF)
option(DOMINO_USE_CARBON_BACKEND "Use macOS Carbon dsys backend" OFF)
option(DSYS_BACKEND_CARBON "Alias for enabling the macOS Carbon dsys backend" OFF)
option(DSYS_BACKEND_DOS16 "Alias for enabling the DOS16 dsys backend" OFF)
option(DSYS_BACKEND_DOS32 "Alias for enabling the DOS32 dsys backend" OFF)
option(DSYS_BACKEND_WIN16 "Alias for enabling the Win16 dsys backend" OFF)
option(DSYS_BACKEND_CPM86 "Alias for enabling the CP/M-86 dsys backend" OFF)
option(DSYS_BACKEND_WAYLAND "Alias for enabling the Wayland dsys backend" OFF)

if(DSYS_BACKEND_POSIX)
    set(DOMINO_USE_POSIX_BACKEND ON CACHE BOOL "Use POSIX headless dsys backend" FORCE)
endif()
if(DSYS_BACKEND_SDL1)
    set(DOMINO_USE_SDL1_BACKEND ON CACHE BOOL "Use SDL1 dsys backend" FORCE)
endif()
if(DSYS_BACKEND_COCOA)
    set(DOMINO_USE_COCOA_BACKEND ON CACHE BOOL "Use macOS Cocoa dsys backend" FORCE)
endif()
if(DSYS_BACKEND_CARBON)
    set(DOMINO_USE_CARBON_BACKEND ON CACHE BOOL "Use macOS Carbon dsys backend" FORCE)
endif()
if(DSYS_BACKEND_DOS16)
    set(DOMINO_USE_DOS16_BACKEND ON CACHE BOOL "Use DOS16 dsys backend" FORCE)
endif()
if(DSYS_BACKEND_DOS32)
    set(DOMINO_USE_DOS32_BACKEND ON CACHE BOOL "Use DOS32 dsys backend" FORCE)
endif()
if(DSYS_BACKEND_WIN16)
    set(DOMINO_USE_WIN16_BACKEND ON CACHE BOOL "Use Win16 dsys backend" FORCE)
endif()
if(DSYS_BACKEND_CPM86)
    set(DOMINO_USE_CPM86_BACKEND ON CACHE BOOL "Use CP/M-86 dsys backend" FORCE)
endif()
if(DSYS_BACKEND_WAYLAND)
    set(DOMINO_USE_WAYLAND_BACKEND ON CACHE BOOL "Use Wayland dsys backend" FORCE)
endif()

set(_dsys_backend_count 0)
foreach(_backend DOMINO_USE_SDL1_BACKEND DOMINO_USE_SDL2_BACKEND DOMINO_USE_X11_BACKEND DOMINO_USE_WAYLAND_BACKEND DOMINO_USE_POSIX_BACKEND DOMINO_USE_COCOA_BACKEND DOMINO_USE_CARBON_BACKEND DOMINO_USE_DOS32_BACKEND DOMINO_USE_DOS16_BACKEND DOMINO_USE_WIN16_BACKEND DOMINO_USE_CPM86_BACKEND)
    if(${${_backend}})
        math(EXPR _dsys_backend_count "${_dsys_backend_count}+1")
    endif()
endforeach()
if(_dsys_backend_count GREATER 1)
    message(FATAL_ERROR "Select only one dsys backend (SDL1, SDL2, X11, Wayland, POSIX, Cocoa, Carbon, DOS32, DOS16, CP/M-86, or Win16)")
endif()

# Domino engine stack
add_subdirectory(system)
add_subdirectory(render)
add_subdirectory(sim)
add_subdirectory(mod)
add_subdirectory(launcher)

set(DOMINO_ENGINE_SOURCES
    system/sys.c
    audio/audio.c
    ui/ui.c
    input/input.c
    core/fs_util.c
    core/core.c
    core/pkg.c
    core/inst.c
    core/sim.c
    core/canvas.c
    core/model_table.c
    core/model_tree.c
    core/view.c
    core/event.c
    core/mod_loader.c
    core/launcher_ext_loader.c
)

if(DOMINO_USE_SDL1_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/sdl1/sdl1_sys.c
    )
    find_package(SDL REQUIRED)
elseif(DOMINO_USE_DOS16_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/dos16/dos16_sys.c
    )
elseif(DOMINO_USE_DOS32_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/dos32/dos32_sys.c
    )
elseif(DOMINO_USE_CPM86_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/cpm86/cpm86_sys.c
    )
elseif(DOMINO_USE_WIN16_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/win16/win16_sys.c
    )
elseif(DOMINO_USE_SDL2_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/sdl2/sdl2_sys.c
    )
    find_package(SDL2 REQUIRED)
elseif(DOMINO_USE_WAYLAND_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/wayland/wayland_sys.c
    )
elseif(DOMINO_USE_X11_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/x11/x11_sys.c
    )
    find_package(X11 REQUIRED)
elseif(DOMINO_USE_POSIX_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/posix/posix_sys.c
    )
elseif(DOMINO_USE_CARBON_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/carbon/carbon_sys.c
    )
elseif(DOMINO_USE_COCOA_BACKEND)
    list(APPEND DOMINO_ENGINE_SOURCES
        system/plat/cocoa/cocoa_sys.c
        system/plat/cocoa/cocoa_sys_objc.m
    )
    find_library(COCOA_FRAMEWORK Cocoa REQUIRED)
    find_library(APPKIT_FRAMEWORK AppKit REQUIRED)
    find_library(FOUNDATION_FRAMEWORK Foundation REQUIRED)
endif()

add_library(domino_engine STATIC ${DOMINO_ENGINE_SOURCES})
target_include_directories(domino_engine
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_link_libraries(domino_engine
    PUBLIC
        domino_gfx
)
target_compile_features(domino_engine PRIVATE c_std_90)
if(DOMINO_USE_SDL1_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_SDL1)
    if(TARGET SDL::SDL)
        target_link_libraries(domino_engine PRIVATE SDL::SDL)
    else()
        target_include_directories(domino_engine PRIVATE ${SDL_INCLUDE_DIR} ${SDL_INCLUDE_DIRS})
        target_link_libraries(domino_engine PRIVATE ${SDL_LIBRARY})
    endif()
    if(SDLMAIN_LIBRARY)
        target_link_libraries(domino_engine PRIVATE ${SDLMAIN_LIBRARY})
    endif()
elseif(DOMINO_USE_DOS16_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_DOS16)
elseif(DOMINO_USE_DOS32_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_DOS32)
elseif(DOMINO_USE_CPM86_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_CPM86)
elseif(DOMINO_USE_SDL2_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_SDL2)
    if(TARGET SDL2::SDL2)
        target_link_libraries(domino_engine PRIVATE SDL2::SDL2)
        if(TARGET SDL2::SDL2main)
            target_link_libraries(domino_engine PRIVATE SDL2::SDL2main)
        endif()
    else()
        target_include_directories(domino_engine PRIVATE ${SDL2_INCLUDE_DIRS})
        target_link_libraries(domino_engine PRIVATE ${SDL2_LIBRARIES})
    endif()
elseif(DOMINO_USE_WAYLAND_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_WAYLAND)
    find_library(WAYLAND_CLIENT_LIB wayland-client)
    if(WAYLAND_CLIENT_LIB)
        target_link_libraries(domino_engine PRIVATE ${WAYLAND_CLIENT_LIB})
    else()
        target_link_libraries(domino_engine PRIVATE wayland-client)
    endif()
elseif(DOMINO_USE_X11_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_X11)
    if(TARGET X11::X11)
        target_link_libraries(domino_engine PRIVATE X11::X11)
    else()
        target_include_directories(domino_engine PRIVATE ${X11_INCLUDE_DIR})
        target_link_libraries(domino_engine PRIVATE ${X11_LIBRARIES})
    endif()
elseif(DOMINO_USE_POSIX_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_POSIX)
elseif(DOMINO_USE_CARBON_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_CARBON)
    find_library(CARBON_FRAMEWORK Carbon REQUIRED)
    target_link_libraries(domino_engine PRIVATE ${CARBON_FRAMEWORK})
elseif(DOMINO_USE_COCOA_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_COCOA)
    target_link_libraries(domino_engine PRIVATE ${APPKIT_FRAMEWORK} ${COCOA_FRAMEWORK} ${FOUNDATION_FRAMEWORK})
    set_source_files_properties(system/plat/cocoa/cocoa_sys_objc.m PROPERTIES
        LANGUAGE OBJC
        COMPILE_FLAGS "-fobjc-arc"
    )
elseif(DOMINO_USE_WIN16_BACKEND)
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_WIN16)
else()
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_NULL)
endif()

install(TARGETS domino_engine
    ARCHIVE DESTINATION lib
)

install(DIRECTORY ${DOMINIUM_INCLUDE_DIR}/domino
    DESTINATION include
)
