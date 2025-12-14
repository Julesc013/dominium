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
