cmake_minimum_required(VERSION 3.16)

add_library(domino_core STATIC
    core/types.c
    core/fixed.c
    core/fixed_debug.c
    core/rng.c
    app/startup.c
    cli/cli.c
    tui/tui.c
    gui/gui.c
    gui/style.c
    render/canvas.c
    render/pipeline.c
    render/backend_detect.c
    render/gui_prim.c
    render/soft/soft_config.c
    render/soft/soft_raster.c
    input/input.c
    input/ime.c
    state/state.c
    system/dsys_stub.c
    system/dsys_term.c
    $<$<BOOL:${WIN32}>:system/dsys_proc_winnt.c>
    $<$<BOOL:${WIN32}>:system/dsys_window_winnt.c>
    $<$<NOT:$<BOOL:${WIN32}>>:system/dsys_window_stub.c>
    $<$<NOT:$<BOOL:${WIN32}>>:system/dsys_proc_stub.c>
    pkg/repo.c
    sim/sim.c
)

if(WIN32)
    target_sources(domino_core PRIVATE system/dsys_terminal_detect_winnt.c)
elseif(UNIX)
    target_sources(domino_core PRIVATE system/dsys_terminal_detect_posix.c)
else()
    target_sources(domino_core PRIVATE system/dsys_terminal_detect_stub.c)
endif()

target_include_directories(domino_core PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
)

set_target_properties(domino_core PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

if(WIN32)
    target_link_libraries(domino_core PRIVATE user32 gdi32)
endif()
