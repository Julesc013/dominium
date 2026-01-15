/*
FILE: source/dominium/game/runtime/dom_tax_rules.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/tax_rules
RESPONSIBILITY: Deterministic tax rule registry and obligation scheduling.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; floating point; nondeterministic inputs.
*/
#ifndef DOM_TAX_RULES_H
#define DOM_TAX_RULES_H

#include <string>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/dom_ledger.h"
#include "domino/core/dom_time_core.h"
}

#include "runtime/dom_jurisdiction_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_TAX_OK = 0,
    DOM_TAX_ERR = -1,
    DOM_TAX_INVALID_ARGUMENT = -2,
    DOM_TAX_DUPLICATE_ID = -3,
    DOM_TAX_NOT_FOUND = -4,
    DOM_TAX_NOT_IMPLEMENTED = -5,
    DOM_TAX_OVERFLOW = -6,
    DOM_TAX_LEDGER_ERROR = -7
};

enum {
    DOM_TAX_KIND_SALES = 1u,
    DOM_TAX_KIND_INCOME = 2u,
    DOM_TAX_KIND_PROPERTY = 3u,
    DOM_TAX_KIND_TARIFF = 4u
};

enum {
    DOM_TAX_SCHEDULE_PHYSICAL = 1u,
    DOM_TAX_SCHEDULE_CIVIL = 2u,
    DOM_TAX_SCHEDULE_ASTRONOMICAL = 3u
};

typedef u64 dom_tax_rule_id;

typedef struct dom_tax_rule_desc {
    const char *id;
    u32 id_len;
    dom_tax_rule_id id_hash;
    dom_jurisdiction_id jurisdiction_id;
    dom_account_id_t revenue_account_id;
    u32 kind;
    dom_asset_id_t asset_id;
    u32 rate_bps; /* 1/10000 */
    u32 rounding_mode;
    u32 schedule_kind;
    dom_act_time_t period_ticks;
} dom_tax_rule_desc;

typedef struct dom_tax_registry dom_tax_registry;

dom_tax_registry *dom_tax_registry_create(void);
void dom_tax_registry_destroy(dom_tax_registry *registry);

int dom_tax_registry_register(dom_tax_registry *registry,
                              const dom_tax_rule_desc *desc);
int dom_tax_registry_get(const dom_tax_registry *registry,
                         dom_tax_rule_id id_hash,
                         dom_tax_rule_desc *out_desc);
int dom_tax_registry_collect(const dom_tax_registry *registry,
                             dom_jurisdiction_id jurisdiction_id,
                             const dom_tax_rule_desc **out_rules,
                             u32 *out_rule_count);

int dom_tax_compute_amount(dom_amount_t base_amount,
                           u32 rate_bps,
                           u32 rounding_mode,
                           dom_amount_t *out_amount);

int dom_tax_schedule_sales(dom_ledger *ledger,
                           const dom_tax_rule_desc *rule,
                           dom_account_id_t taxpayer_account,
                           dom_amount_t taxable_amount,
                           dom_act_time_t act_time,
                           dom_obligation_id_t *out_obligation_id);

int dom_tax_schedule_periodic(dom_ledger *ledger,
                              const dom_tax_rule_desc *rule,
                              dom_account_id_t taxpayer_account,
                              dom_amount_t taxable_amount,
                              dom_act_time_t start_act,
                              dom_obligation_id_t *out_obligation_id,
                              dom_act_time_t *out_next_due);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_TAX_RULES_H */
