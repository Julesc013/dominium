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

