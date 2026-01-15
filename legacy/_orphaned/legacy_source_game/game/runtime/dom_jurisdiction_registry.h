/*
FILE: source/dominium/game/runtime/dom_jurisdiction_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/jurisdiction_registry
RESPONSIBILITY: Deterministic jurisdiction economic policy registry.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; floating point; nondeterministic inputs.
*/
#ifndef DOM_JURISDICTION_REGISTRY_H
#define DOM_JURISDICTION_REGISTRY_H

#include <string>

extern "C" {
#include "domino/core/types.h"
}

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_JURIS_OK = 0,
    DOM_JURIS_ERR = -1,
    DOM_JURIS_INVALID_ARGUMENT = -2,
    DOM_JURIS_DUPLICATE_ID = -3,
    DOM_JURIS_NOT_FOUND = -4
};

typedef u64 dom_jurisdiction_id;

typedef struct dom_jurisdiction_policy_desc {
    const char *id;
    u32 id_len;
    dom_jurisdiction_id id_hash;
    dom_account_id_t revenue_account_id;
    dom_account_id_t spending_account_id;
    dom_account_id_t reserve_account_id;
    u64 money_standard_id_hash;
    u32 flags;
} dom_jurisdiction_policy_desc;

typedef struct dom_jurisdiction_registry dom_jurisdiction_registry;

dom_jurisdiction_registry *dom_jurisdiction_registry_create(void);
void dom_jurisdiction_registry_destroy(dom_jurisdiction_registry *registry);

int dom_jurisdiction_registry_register(dom_jurisdiction_registry *registry,
                                       const dom_jurisdiction_policy_desc *desc);
int dom_jurisdiction_registry_get(const dom_jurisdiction_registry *registry,
                                  dom_jurisdiction_id id_hash,
                                  dom_jurisdiction_policy_desc *out_desc);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_JURISDICTION_REGISTRY_H */
