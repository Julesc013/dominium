/*
FILE: source/dominium/game/runtime/dom_contract_templates.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/contract_templates
RESPONSIBILITY: Deterministic contract template registry (obligation schedules).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_CONTRACT_TEMPLATES_H
#define DOM_CONTRACT_TEMPLATES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_CONTRACT_TEMPLATE_OK = 0,
    DOM_CONTRACT_TEMPLATE_ERR = -1,
    DOM_CONTRACT_TEMPLATE_INVALID_ARGUMENT = -2,
    DOM_CONTRACT_TEMPLATE_DUPLICATE_ID = -3,
    DOM_CONTRACT_TEMPLATE_INVALID_DATA = -4,
    DOM_CONTRACT_TEMPLATE_NOT_FOUND = -5
};

typedef u64 dom_contract_template_id;
typedef u64 dom_contract_role_id;

typedef struct dom_contract_obligation_desc {
    const char *role_from_id;
    u32 role_from_id_len;
    dom_contract_role_id role_from_hash;
    const char *role_to_id;
    u32 role_to_id_len;
    dom_contract_role_id role_to_hash;
    const char *asset_id;
    u32 asset_id_len;
    u64 asset_id_hash;
    i64 amount;
    u64 offset_ticks;
} dom_contract_obligation_desc;

typedef struct dom_contract_template_desc {
    const char *id;
    u32 id_len;
    dom_contract_template_id id_hash;
    const dom_contract_obligation_desc *obligations;
    u32 obligation_count;
} dom_contract_template_desc;

typedef struct dom_contract_obligation {
    dom_contract_role_id role_from_hash;
    dom_contract_role_id role_to_hash;
    u64 asset_id_hash;
    i64 amount;
    u64 offset_ticks;
    const char *role_from_id;
    u32 role_from_id_len;
    const char *role_to_id;
    u32 role_to_id_len;
    const char *asset_id;
    u32 asset_id_len;
} dom_contract_obligation;

typedef struct dom_contract_template_info {
    dom_contract_template_id id_hash;
    const char *id;
    u32 id_len;
    const dom_contract_obligation *obligations;
    u32 obligation_count;
} dom_contract_template_info;

typedef void (*dom_contract_template_iter_fn)(const dom_contract_template_info *info,
                                              void *user);

typedef struct dom_contract_template_registry dom_contract_template_registry;

dom_contract_template_registry *dom_contract_template_registry_create(void);
void dom_contract_template_registry_destroy(dom_contract_template_registry *registry);

int dom_contract_template_registry_register(dom_contract_template_registry *registry,
                                            const dom_contract_template_desc *desc);
int dom_contract_template_registry_get(const dom_contract_template_registry *registry,
                                       dom_contract_template_id id_hash,
                                       dom_contract_template_info *out_info);
int dom_contract_template_registry_iterate(const dom_contract_template_registry *registry,
                                           dom_contract_template_iter_fn fn,
                                           void *user);
u32 dom_contract_template_registry_count(const dom_contract_template_registry *registry);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_CONTRACT_TEMPLATES_H */
