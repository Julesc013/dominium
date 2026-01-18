/*
FILE: include/dominium/rules/war/loss_accounting.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic loss accounting helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Loss application is deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_LOSS_ACCOUNTING_H
#define DOMINIUM_RULES_WAR_LOSS_ACCOUNTING_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/war/engagement.h"
#include "dominium/rules/war/morale_state.h"
#include "dominium/rules/war/readiness_state.h"
#include "dominium/rules/war/security_force.h"

#ifdef __cplusplus
extern "C" {
#endif

int loss_accounting_apply_equipment_losses(security_force* force,
                                           const engagement_equipment_loss* losses,
                                           u32 loss_count);
int loss_accounting_apply_readiness(readiness_registry* registry,
                                    u64 readiness_id,
                                    i32 delta,
                                    dom_act_time_t act_time);
int loss_accounting_apply_morale(morale_registry* registry,
                                 u64 morale_id,
                                 i32 delta);
int loss_accounting_apply_legitimacy(legitimacy_registry* registry,
                                     u64 legitimacy_id,
                                     i32 delta);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_LOSS_ACCOUNTING_H */
