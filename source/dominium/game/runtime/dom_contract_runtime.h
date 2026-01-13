/*
FILE: source/dominium/game/runtime/dom_contract_runtime.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/contract_runtime
RESPONSIBILITY: Deterministic contract runtime scheduling via engine ledger.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_CONTRACT_RUNTIME_H
#define DOM_CONTRACT_RUNTIME_H

#include "domino/core/dom_ledger.h"
#include "domino/core/dom_time_core.h"
#include "runtime/dom_contract_templates.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_CONTRACT_RUNTIME_OK = 0,
    DOM_CONTRACT_RUNTIME_ERR = -1,
    DOM_CONTRACT_RUNTIME_INVALID_ARGUMENT = -2,
    DOM_CONTRACT_RUNTIME_TEMPLATE_NOT_FOUND = -3,
    DOM_CONTRACT_RUNTIME_ROLE_MISSING = -4,
    DOM_CONTRACT_RUNTIME_ROLE_DUPLICATE = -5,
    DOM_CONTRACT_RUNTIME_OVERFLOW = -6,
    DOM_CONTRACT_RUNTIME_LEDGER_ERROR = -7
};

typedef struct dom_contract_role_binding_desc {
    const char *role_id;
    u32 role_id_len;
    dom_contract_role_id role_id_hash;
    dom_account_id_t account_id;
} dom_contract_role_binding_desc;

typedef struct dom_contract_instance_desc {
    const char *template_id;
    u32 template_id_len;
    dom_contract_template_id template_id_hash;
    const dom_contract_role_binding_desc *role_bindings;
    u32 role_binding_count;
    dom_act_time_t start_act;
} dom_contract_instance_desc;

typedef struct dom_contract_schedule_result {
    u32 obligation_count;
    dom_obligation_id_t first_obligation_id;
} dom_contract_schedule_result;

int dom_contract_runtime_schedule(dom_ledger *ledger,
                                  const dom_contract_template_registry *templates,
                                  const dom_contract_instance_desc *desc,
                                  dom_contract_schedule_result *out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_CONTRACT_RUNTIME_H */
