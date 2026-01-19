/*
FILE: game/core/orchestration/macro_due_emit.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / orchestration
RESPONSIBILITY: Work IR emission for macro due-scheduler hooks (internal).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Deterministic task emission order and IDs.
*/
#ifndef DOMINIUM_CORE_ORCH_MACRO_DUE_EMIT_H
#define DOMINIUM_CORE_ORCH_MACRO_DUE_EMIT_H

#include "dominium/sim/macro_due_scheduler_hooks.h"
#include "dominium/fidelity.h"
#include "../execution/work_graph_builder.h"
#include "../execution/access_set_builder.h"

int dom_macro_due_emit_tasks(const dom_macro_due_hooks* hooks,
                             dom_act_time_t act_now,
                             dom_act_time_t act_target,
                             dom_work_graph_builder* graph_builder,
                             dom_access_set_builder* access_builder,
                             u64 system_id,
                             dom_fidelity_tier fidelity_tier);

#endif /* DOMINIUM_CORE_ORCH_MACRO_DUE_EMIT_H */
