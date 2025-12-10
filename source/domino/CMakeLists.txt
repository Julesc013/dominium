cmake_minimum_required(VERSION 3.16)

add_library(domino_core STATIC
    core/types.c
    core/fixed.c
    core/fixed_debug.c
    core/rng.c
    cli/cli.c
    tui/tui.c
    gui/gui.c
    gui/style.c
    render/gui_prim.c
    system/dsys_stub.c
    system/dsys_term.c
    $<$<BOOL:${WIN32}>:system/dsys_proc_winnt.c>
    $<$<NOT:$<BOOL:${WIN32}>>:system/dsys_proc_stub.c>
    pkg/repo.c
    sim/sim.c
)

target_include_directories(domino_core PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
)

set_target_properties(domino_core PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
