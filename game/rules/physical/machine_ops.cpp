/*
FILE: game/rules/physical/machine_ops.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Implements machine wear, maintenance, and failure handling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Machine wear and failure progression are deterministic.
*/
#include "dominium/physical/machine_ops.h"
#include "dominium/physical/physical_process.h"

#include <string.h>

void dom_machine_init(dom_machine_state* machine,
                      u64 machine_id,
                      u32 wear_limit)
{
    if (!machine) {
        return;
    }
    memset(machine, 0, sizeof(*machine));
    machine->machine_id = machine_id;
    machine->wear_limit = wear_limit;
    machine->wear_level = 0u;
    machine->status = DOM_MACHINE_OPERATIONAL;
    machine->failure_mode_id = 0u;
}

static void dom_machine_update_status(dom_machine_state* machine)
{
    if (!machine) {
        return;
    }
    if (machine->wear_level >= machine->wear_limit) {
        machine->status = DOM_MACHINE_FAILED;
        machine->failure_mode_id = DOM_PHYS_FAIL_CAPACITY;
    } else if (machine->wear_level > (machine->wear_limit / 2u)) {
        machine->status = DOM_MACHINE_DEGRADED;
    } else {
        machine->status = DOM_MACHINE_OPERATIONAL;
    }
}

void dom_machine_operate(dom_machine_state* machine,
                         u32 wear_amount,
                         dom_physical_audit_log* audit,
                         dom_act_time_t now_act)
{
    if (!machine || wear_amount == 0u) {
        return;
    }
    machine->wear_level += wear_amount;
    dom_machine_update_status(machine);
    if (audit) {
        dom_physical_audit_set_context(audit, now_act, 0u);
        dom_physical_audit_record(audit,
                                  0u,
                                  DOM_PHYS_EVENT_MACHINE_WEAR,
                                  machine->machine_id,
                                  0u,
                                  (i64)wear_amount);
        if (machine->status == DOM_MACHINE_FAILED) {
            dom_physical_audit_record(audit,
                                      0u,
                                      DOM_PHYS_EVENT_MACHINE_FAIL,
                                      machine->machine_id,
                                      0u,
                                      (i64)machine->wear_level);
        }
    }
}

void dom_machine_overload(dom_machine_state* machine,
                          u32 wear_amount,
                          dom_physical_audit_log* audit,
                          dom_act_time_t now_act)
{
    dom_machine_operate(machine, wear_amount, audit, now_act);
}

void dom_machine_repair(dom_machine_state* machine,
                        u32 repair_amount,
                        dom_physical_audit_log* audit,
                        dom_act_time_t now_act)
{
    if (!machine || repair_amount == 0u) {
        return;
    }
    if (repair_amount >= machine->wear_level) {
        machine->wear_level = 0u;
    } else {
        machine->wear_level -= repair_amount;
    }
    dom_machine_update_status(machine);
    if (audit) {
        dom_physical_audit_set_context(audit, now_act, 0u);
        dom_physical_audit_record(audit,
                                  0u,
                                  DOM_PHYS_EVENT_MAINTENANCE,
                                  machine->machine_id,
                                  0u,
                                  (i64)repair_amount);
    }
}
