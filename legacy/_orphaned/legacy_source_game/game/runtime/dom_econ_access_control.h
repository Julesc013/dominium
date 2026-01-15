/*
FILE: source/dominium/game/runtime/dom_econ_access_control.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/econ_access_control
RESPONSIBILITY: Deterministic access control for economic data visibility.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_ECON_ACCESS_CONTROL_H
#define DOM_ECON_ACCESS_CONTROL_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_ECON_ACCESS_OK = 0,
    DOM_ECON_ACCESS_ERR = -1,
    DOM_ECON_ACCESS_INVALID_ARGUMENT = -2
};

enum {
    DOM_ECON_ACCESS_VIEW_BALANCE = 1u << 0,
    DOM_ECON_ACCESS_VIEW_TRANSACTIONS = 1u << 1,
    DOM_ECON_ACCESS_VIEW_LOTS = 1u << 2
};

typedef struct dom_econ_access_grant_desc {
    u64 actor_id;
    u64 account_id;
    u32 flags;
} dom_econ_access_grant_desc;

typedef struct dom_econ_access_grant_info {
    u64 actor_id;
    u64 account_id;
    u32 flags;
} dom_econ_access_grant_info;

typedef void (*dom_econ_access_iter_fn)(const dom_econ_access_grant_info *info,
                                        void *user);

typedef struct dom_econ_access_control dom_econ_access_control;

dom_econ_access_control *dom_econ_access_control_create(void);
void dom_econ_access_control_destroy(dom_econ_access_control *ctrl);

int dom_econ_access_grant(dom_econ_access_control *ctrl,
                          const dom_econ_access_grant_desc *desc);
int dom_econ_access_revoke(dom_econ_access_control *ctrl,
                           u64 actor_id,
                           u64 account_id);
u32 dom_econ_access_check(const dom_econ_access_control *ctrl,
                          u64 actor_id,
                          u64 account_id);
int dom_econ_access_iterate(const dom_econ_access_control *ctrl,
                            dom_econ_access_iter_fn fn,
                            void *user);
u32 dom_econ_access_count(const dom_econ_access_control *ctrl);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_ECON_ACCESS_CONTROL_H */
