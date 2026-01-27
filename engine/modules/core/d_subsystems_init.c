/*
FILE: source/domino/core/d_subsystems_init.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_subsystems_init
RESPONSIBILITY: Implements `d_subsystems_init`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "core/d_subsystem.h"
#include "res/d_res.h"
#include "env/d_env.h"
#include "world/d_litho.h"
#include "hydro/d_hydro.h"
#include "build/d_build.h"
#include "core/d_org.h"
#include "policy/d_policy.h"
#include "research/d_research_state.h"
#include "econ/d_econ_metrics.h"
#include "trans/d_trans.h"
#include "struct/d_struct.h"
#include "vehicle/d_vehicle.h"
#include "job/d_job.h"
#include "net/d_net.h"
#include "replay/d_replay.h"
#include "scale/d_macro_capsule_subsys.h"
#include "scale/d_macro_schedule_subsys.h"
#include "scale/d_macro_event_queue_subsys.h"

static int g_subsystems_initialized = 0;

static void d_subsystems_register_models(void) {
    u32 i;
    u32 count = d_subsystem_count();
    for (i = 0u; i < count; ++i) {
        const d_subsystem_desc *desc = d_subsystem_get_by_index(i);
        if (desc && desc->register_models) {
            desc->register_models();
        }
    }
}

void d_subsystems_init(void) {
    if (g_subsystems_initialized) {
        return;
    }
    d_res_init();
    d_env_init();
    d_litho_init();
    d_hydro_init();
    d_build_register_subsystem();
    d_trans_register_subsystem();
    d_org_register_subsystem();
    d_policy_register_subsystem();
    d_research_register_subsystem();
    d_struct_init();
    d_econ_register_subsystem();
    d_vehicle_init();
    d_job_init();
    d_net_register_subsystem();
    d_replay_register_subsystem();
    d_macro_capsule_register_subsystem();
    d_macro_schedule_register_subsystem();
    d_macro_event_queue_register_subsystem();
    d_subsystems_register_models();
    g_subsystems_initialized = 1;
}
