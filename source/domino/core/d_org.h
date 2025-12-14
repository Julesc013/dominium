/* Organization/company registry (C89).
 * Orgs own entities, accounts, and research state at the engine level.
 */
#ifndef D_ORG_H
#define D_ORG_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "core/d_account.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_org_id;

typedef struct d_org_s {
    d_org_id      id;
    q32_32        priority;   /* optional weight/importance */
    d_account_id  account_id; /* link to deterministic account */
} d_org;

struct d_world;

int d_org_system_init(void);
void d_org_system_shutdown(void);

d_org_id d_org_create(q32_32 initial_balance);
int      d_org_get(d_org_id id, d_org *out);
int      d_org_update(const d_org *org);

/* Iteration helpers for UI/debug (deterministic order by id). */
u32 d_org_count(void);
int d_org_get_by_index(u32 index, d_org *out);

/* Subsystem registration hook (called once at startup). */
void d_org_register_subsystem(void);

/* World-state validator hook. */
int d_org_validate(const struct d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_ORG_H */
