/*
FILE: source/domino/dsim.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dsim
RESPONSIBILITY: Implements `dsim`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dsim.h"
#include "domino/dzone.h"
#include "domino/dnet.h"
#include "domino/dactor.h"
#include "domino/dvehicle.h"
#include "domino/dmachine.h"
#include "domino/dresearch.h"
#include "domino/djob.h"

void dsim_tick(SimTick t)
{
    dzone_tick(t);
    dnet_power_step(1);
    dnet_fluid_step(1);
    dnet_gas_step(1);
    dnet_heat_step(1);
    dnet_signal_step(1);
    dnet_data_step(1);
    dnet_comm_step(1);
    dactor_tick_all(t);
    dvehicle_tick_all(t, 1);
    dmachine_tick_all(t);
    dresearch_tick(t);
    djob_tick(t);
}
