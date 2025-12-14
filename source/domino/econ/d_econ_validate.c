#include <stdio.h>

#include "econ/d_econ_metrics.h"

#include "core/d_org.h"

int d_econ_validate(const d_world *w) {
    u32 i;
    u32 count;
    (void)w;

    count = d_econ_org_metrics_count();
    for (i = 0u; i < count; ++i) {
        d_econ_org_metrics m;
        d_org org;
        if (d_econ_org_metrics_get_by_index(i, &m) != 0) {
            fprintf(stderr, "econ validate: failed get_by_index %u\n", (unsigned)i);
            return -1;
        }
        if (m.org_id == 0u) {
            fprintf(stderr, "econ validate: invalid org_id at index %u\n", (unsigned)i);
            return -1;
        }
        if (d_org_get(m.org_id, &org) != 0) {
            fprintf(stderr, "econ validate: missing org %u for metrics\n", (unsigned)m.org_id);
            return -1;
        }
    }
    return 0;
}

