/*
FILE: source/domino/core/d_org.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_org
RESPONSIBILITY: Defines internal contract for `d_org`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
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
