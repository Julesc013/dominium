/*
FILE: source/dominium/setup/core/src/state/dsu_state_internal.h
MODULE: Dominium Setup
PURPOSE: Internal helpers for building installed-state (Plan S-5).
*/
#ifndef DSU_STATE_INTERNAL_H_INCLUDED
#define DSU_STATE_INTERNAL_H_INCLUDED

#include "../../include/dsu/dsu_ctx.h"
#include "../../include/dsu/dsu_plan.h"
#include "../../include/dsu/dsu_state.h"

dsu_status_t dsu__state_build_from_plan(dsu_ctx_t *ctx,
                                        const dsu_plan_t *plan,
                                        const dsu_state_t *prev_state,
                                        dsu_u64 last_journal_id,
                                        dsu_bool has_last_audit_log_digest64,
                                        dsu_u64 last_audit_log_digest64,
                                        dsu_state_t **out_state);

#endif /* DSU_STATE_INTERNAL_H_INCLUDED */
