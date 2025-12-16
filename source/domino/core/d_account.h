/*
FILE: source/domino/core/d_account.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_account
RESPONSIBILITY: Implements `d_account`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Minimal deterministic account/balance system (C89). */
#ifndef D_ACCOUNT_H
#define D_ACCOUNT_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_account_id;

typedef struct d_account_s {
    d_account_id id;
    q32_32       balance; /* generic fixed-point, e.g. Q32.32 */
} d_account;

int d_account_system_init(void);
void d_account_system_shutdown(void);

d_account_id d_account_create(q32_32 initial_balance);
/* Create an account with a specific id (used for deterministic load/restore). */
int          d_account_create_with_id(d_account_id id, q32_32 initial_balance);
int          d_account_get(d_account_id id, d_account *out);
int          d_account_update(const d_account *acc);

/* Deterministic transfer, returns 0 on success, non-zero on fail. */
int d_account_transfer(
    d_account_id from,
    d_account_id to,
    q32_32       amount
);

#ifdef __cplusplus
}
#endif

#endif /* D_ACCOUNT_H */
