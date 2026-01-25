/*
FILE: include/dominium/physical/machine_ops.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Defines machine wear, maintenance, and failure handling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Machine wear and failure progression are deterministic.
*/
#ifndef DOMINIUM_PHYSICAL_MACHINE_OPS_H
#define DOMINIUM_PHYSICAL_MACHINE_OPS_H

#include "domino/core/types.h"
#include "dominium/physical/physical_audit.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_machine_status {
    DOM_MACHINE_OPERATIONAL = 0,
    DOM_MACHINE_DEGRADED = 1,
    DOM_MACHINE_FAILED = 2
} dom_machine_status;

typedef struct dom_machine_state {
    u64 machine_id;
    u32 wear_level;
    u32 wear_limit;
    u32 status;
    u32 failure_mode_id;
} dom_machine_state;

void dom_machine_init(dom_machine_state* machine,
                      u64 machine_id,
                      u32 wear_limit);
void dom_machine_operate(dom_machine_state* machine,
                         u32 wear_amount,
                         dom_physical_audit_log* audit,
                         dom_act_time_t now_act);
void dom_machine_overload(dom_machine_state* machine,
                          u32 wear_amount,
                          dom_physical_audit_log* audit,
                          dom_act_time_t now_act);
void dom_machine_repair(dom_machine_state* machine,
                        u32 repair_amount,
                        dom_physical_audit_log* audit,
                        dom_act_time_t now_act);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_MACHINE_OPS_H */
