/*
FILE: source/domino/econ/d_econ_metrics.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / econ/d_econ_metrics
RESPONSIBILITY: Implements `d_econ_metrics`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Macro-economy metrics substrate (C89).
 * Generic rolling metrics; no currency or market semantics are enforced here.
 */
#ifndef D_ECON_METRICS_H
#define D_ECON_METRICS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "content/d_content.h"
#include "core/d_org.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_econ_flow_s {
    d_item_id item_id;
    q32_32    quantity_per_tick;
} d_econ_flow;

typedef struct d_econ_org_metrics_s {
    d_org_id org_id;

    /* Rolling metrics (generic units). */
    q32_32 total_output;
    q32_32 total_input;
    q32_32 net_throughput;

    /* Optional: generic value/index proxy. */
    q32_32 price_index;
} d_econ_org_metrics;

int d_econ_metrics_init(void);
void d_econ_metrics_shutdown(void);

void d_econ_metrics_tick(d_world *w, u32 ticks);

/* Called by process/job systems when deterministic production/consumption events occur.
 * quantity may be negative to represent input/consumption.
 */
void d_econ_register_production(
    d_org_id    org_id,
    d_item_id   item_id,
    q32_32      quantity
);

int d_econ_get_org_metrics(d_org_id org_id, d_econ_org_metrics *out);
u32 d_econ_org_metrics_count(void);
int d_econ_org_metrics_get_by_index(u32 index, d_econ_org_metrics *out);

/* Subsystem registration hook (called once at startup). */
void d_econ_register_subsystem(void);

/* World-state validator hook. */
int d_econ_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_ECON_METRICS_H */
