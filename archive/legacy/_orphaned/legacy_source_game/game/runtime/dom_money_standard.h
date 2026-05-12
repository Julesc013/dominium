/*
FILE: source/dominium/game/runtime/dom_money_standard.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/money_standard
RESPONSIBILITY: Deterministic money standard registry and rendering helpers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; floating-point money.
*/
#ifndef DOM_MONEY_STANDARD_H
#define DOM_MONEY_STANDARD_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_MONEY_OK = 0,
    DOM_MONEY_ERR = -1,
    DOM_MONEY_INVALID_ARGUMENT = -2,
    DOM_MONEY_DUPLICATE_ID = -3,
    DOM_MONEY_INVALID_DATA = -4,
    DOM_MONEY_NOT_FOUND = -5
};

typedef u64 dom_money_standard_id;

typedef struct dom_money_standard_desc {
    const char *id;
    u32 id_len;
    dom_money_standard_id id_hash;
    const char *base_asset_id;
    u32 base_asset_id_len;
    u64 base_asset_id_hash;
    u32 denom_scale;
    u32 rounding_mode;
    const char *display_name;
    u32 display_name_len;
    const char *convert_rule_id;
    u32 convert_rule_id_len;
    u64 convert_rule_id_hash;
} dom_money_standard_desc;

typedef struct dom_money_standard_info {
    dom_money_standard_id id_hash;
    u64 base_asset_id_hash;
    u32 denom_scale;
    u32 rounding_mode;
    const char *id;
    u32 id_len;
    const char *display_name;
    u32 display_name_len;
    const char *convert_rule_id;
    u32 convert_rule_id_len;
    u64 convert_rule_id_hash;
} dom_money_standard_info;

typedef struct dom_money_rendered {
    i64 whole;
    u32 minor;
    u32 scale;
    int negative;
} dom_money_rendered;

typedef void (*dom_money_standard_iter_fn)(const dom_money_standard_info *info,
                                           void *user);

typedef struct dom_money_standard_registry dom_money_standard_registry;

dom_money_standard_registry *dom_money_standard_registry_create(void);
void dom_money_standard_registry_destroy(dom_money_standard_registry *registry);

int dom_money_standard_registry_register(dom_money_standard_registry *registry,
                                         const dom_money_standard_desc *desc);
int dom_money_standard_registry_get(const dom_money_standard_registry *registry,
                                    dom_money_standard_id id_hash,
                                    dom_money_standard_info *out_info);
int dom_money_standard_registry_iterate(const dom_money_standard_registry *registry,
                                        dom_money_standard_iter_fn fn,
                                        void *user);
u32 dom_money_standard_registry_count(const dom_money_standard_registry *registry);

int dom_money_standard_render(const dom_money_standard_registry *registry,
                              dom_money_standard_id id_hash,
                              i64 amount,
                              dom_money_rendered *out);
int dom_money_standard_parse(const dom_money_standard_registry *registry,
                             dom_money_standard_id id_hash,
                             const dom_money_rendered *in,
                             i64 *out_amount);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_MONEY_STANDARD_H */
