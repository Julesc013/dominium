/*
FILE: source/dominium/game/core/game_stub.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/core/game_stub
RESPONSIBILITY: Implements `game_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include "domino/sys.h"
#include "domino/sim.h"
#include "domino/mod.h"

int main(int argc, char** argv)
{
    (void)argc; (void)argv;
    domino_sys_context* sys = NULL;
    domino_sys_desc sdesc;
    dm_mod_context* mod;
    dm_sim_context* sim;

    sdesc.profile_hint = DOMINO_SYS_PROFILE_AUTO;
    if (domino_sys_init(&sdesc, &sys) != 0 || !sys) {
        return 1;
    }

    mod = dm_mod_create();
    sim = dm_sim_create(NULL);
    domino_sys_log(sys, DOMINO_LOG_INFO, "game", "Dominium game stub");
    dm_sim_tick(sim, 0);
    dm_mod_destroy(mod);
    dm_sim_destroy(sim);
    domino_sys_shutdown(sys);
    return 0;
}
