/*
FILE: source/domino/econ/d_econ_metrics.c
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
#include <stdlib.h>
#include <string.h>

#include "econ/d_econ_metrics.h"

#include "core/d_subsystem.h"

#define DECON_MAX_ORGS 1024u
#define DECON_EMA_WINDOW 64u

typedef struct decon_entry_s {
    d_econ_org_metrics metrics;

    q32_32 step_out_value;
    q32_32 step_out_qty;
    q32_32 step_in_value;
    q32_32 step_in_qty;

    q32_32 ema_out;
    q32_32 ema_in;
    q32_32 ema_price;

    int in_use;
} decon_entry;

static decon_entry g_econ_orgs[DECON_MAX_ORGS];
static int g_econ_initialized = 0;
static int g_econ_registered = 0;

static decon_entry *decon_find(d_org_id org_id) {
    u32 i;
    if (org_id == 0u) {
        return (decon_entry *)0;
    }
    for (i = 0u; i < DECON_MAX_ORGS; ++i) {
        if (g_econ_orgs[i].in_use && g_econ_orgs[i].metrics.org_id == org_id) {
            return &g_econ_orgs[i];
        }
    }
    return (decon_entry *)0;
}

static decon_entry *decon_alloc(d_org_id org_id) {
    u32 i;
    for (i = 0u; i < DECON_MAX_ORGS; ++i) {
        if (!g_econ_orgs[i].in_use) {
            memset(&g_econ_orgs[i], 0, sizeof(g_econ_orgs[i]));
            g_econ_orgs[i].metrics.org_id = org_id;
            g_econ_orgs[i].ema_out = 0;
            g_econ_orgs[i].ema_in = 0;
            g_econ_orgs[i].ema_price = 0;
            g_econ_orgs[i].in_use = 1;
            return &g_econ_orgs[i];
        }
    }
    return (decon_entry *)0;
}

int d_econ_metrics_init(void) {
    if (g_econ_initialized) {
        return 0;
    }
    memset(g_econ_orgs, 0, sizeof(g_econ_orgs));
    g_econ_initialized = 1;
    return 0;
}

void d_econ_metrics_shutdown(void) {
    memset(g_econ_orgs, 0, sizeof(g_econ_orgs));
    g_econ_initialized = 0;
}

void d_econ_register_production(
    d_org_id    org_id,
    d_item_id   item_id,
    q32_32      quantity
) {
    decon_entry *e;
    const d_proto_item *it;
    q16_16 base_value;
    i64 qty_int;
    i64 prod_q16;
    q32_32 val_q32;
    q32_32 qty_q32;

    if (org_id == 0u || item_id == 0u || quantity == 0) {
        return;
    }
    if (!g_econ_initialized) {
        (void)d_econ_metrics_init();
    }

    e = decon_find(org_id);
    if (!e) {
        e = decon_alloc(org_id);
        if (!e) {
            return;
        }
    }

    it = d_content_get_item(item_id);
    base_value = it ? it->base_value : 0;

    qty_int = ((i64)quantity) >> Q32_32_FRAC_BITS;
    if (qty_int == 0) {
        return;
    }

    /* Compute |base_value * qty_int| in q16_16, then lift to q32_32. */
    prod_q16 = (i64)base_value * qty_int;
    if (prod_q16 < 0) {
        prod_q16 = -prod_q16;
    }
    val_q32 = (q32_32)(prod_q16 << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS));

    if (qty_int > 0) {
        qty_q32 = (q32_32)(qty_int << Q32_32_FRAC_BITS);
        e->step_out_qty += qty_q32;
        e->step_out_value += val_q32;
    } else {
        qty_int = -qty_int;
        qty_q32 = (q32_32)(qty_int << Q32_32_FRAC_BITS);
        e->step_in_qty += qty_q32;
        e->step_in_value += val_q32;
    }
}

static q32_32 decon_ema_update(q32_32 ema, q32_32 sample) {
    q32_32 diff = sample - ema;
    return ema + (diff / (q32_32)DECON_EMA_WINDOW);
}

void d_econ_metrics_tick(d_world *w, u32 ticks) {
    u32 i;
    (void)w;
    if (ticks == 0u) {
        return;
    }
    if (!g_econ_initialized) {
        (void)d_econ_metrics_init();
    }

    for (i = 0u; i < DECON_MAX_ORGS; ++i) {
        decon_entry *e = &g_econ_orgs[i];
        q32_32 sample_out;
        q32_32 sample_in;
        q32_32 sample_price = e->ema_price;
        i64 qty_int;
        i64 value_sum_q16;
        i64 avg_q16;

        if (!e->in_use) {
            continue;
        }

        sample_out = e->step_out_value / (q32_32)(i32)ticks;
        sample_in = e->step_in_value / (q32_32)(i32)ticks;

        e->ema_out = decon_ema_update(e->ema_out, sample_out);
        e->ema_in = decon_ema_update(e->ema_in, sample_in);

        /* Price index proxy: average base_value of outputs in this step. */
        qty_int = ((i64)e->step_out_qty) >> Q32_32_FRAC_BITS;
        if (qty_int > 0) {
            value_sum_q16 = ((i64)e->step_out_value) >> (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
            avg_q16 = value_sum_q16 / qty_int;
            sample_price = (q32_32)(avg_q16 << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS));
        }
        e->ema_price = decon_ema_update(e->ema_price, sample_price);

        e->metrics.total_output = e->ema_out;
        e->metrics.total_input = e->ema_in;
        e->metrics.net_throughput = e->ema_out - e->ema_in;
        e->metrics.price_index = e->ema_price;

        e->step_out_value = 0;
        e->step_out_qty = 0;
        e->step_in_value = 0;
        e->step_in_qty = 0;
    }
}

int d_econ_get_org_metrics(d_org_id org_id, d_econ_org_metrics *out) {
    decon_entry *e;
    if (!out) {
        return -1;
    }
    e = decon_find(org_id);
    if (!e) {
        return -1;
    }
    *out = e->metrics;
    return 0;
}

u32 d_econ_org_metrics_count(void) {
    u32 i;
    u32 count = 0u;
    for (i = 0u; i < DECON_MAX_ORGS; ++i) {
        if (g_econ_orgs[i].in_use) {
            count += 1u;
        }
    }
    return count;
}

static void decon_sort_org_ids(d_org_id *ids, u32 count) {
    u32 i;
    for (i = 1u; i < count; ++i) {
        d_org_id key = ids[i];
        u32 j = i;
        while (j > 0u && ids[j - 1u] > key) {
            ids[j] = ids[j - 1u];
            --j;
        }
        ids[j] = key;
    }
}

int d_econ_org_metrics_get_by_index(u32 index, d_econ_org_metrics *out) {
    d_org_id ids[DECON_MAX_ORGS];
    u32 i;
    u32 count = 0u;

    if (!out) {
        return -1;
    }

    for (i = 0u; i < DECON_MAX_ORGS; ++i) {
        if (g_econ_orgs[i].in_use) {
            ids[count++] = g_econ_orgs[i].metrics.org_id;
        }
    }
    if (index >= count) {
        return -1;
    }
    decon_sort_org_ids(ids, count);
    return d_econ_get_org_metrics(ids[index], out);
}

static int d_econ_save_chunk(struct d_world *w, struct d_chunk *chunk, struct d_tlv_blob *out) {
    (void)w;
    (void)chunk;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_econ_load_chunk(struct d_world *w, struct d_chunk *chunk, const struct d_tlv_blob *in) {
    (void)w;
    (void)chunk;
    (void)in;
    return 0;
}

static void d_econ_init_instance_subsys(struct d_world *w) {
    (void)w;
    d_econ_metrics_shutdown();
    (void)d_econ_metrics_init();
}

static void d_econ_tick_subsys(struct d_world *w, u32 ticks) {
    d_econ_metrics_tick(w, ticks);
}

static int d_econ_save_instance(struct d_world *w, struct d_tlv_blob *out) {
    u32 version;
    u32 count;
    u32 total;
    unsigned char *buf;
    unsigned char *dst;
    u32 i;
    u32 written = 0u;

    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;

    count = d_econ_org_metrics_count();
    if (count == 0u) {
        return 0;
    }

    version = 1u;
    total = 0u;
    total += 4u; /* version */
    total += 4u; /* count */
    total += count * (4u + sizeof(q32_32) * 8u + 4u); /* per entry + pad */

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;
    memcpy(dst, &version, 4u); dst += 4u;
    memcpy(dst, &count, 4u); dst += 4u;

    for (i = 0u; i < count; ++i) {
        d_econ_org_metrics m;
        decon_entry *e;
        u32 pad = 0u;
        if (d_econ_org_metrics_get_by_index(i, &m) != 0) {
            continue;
        }
        e = decon_find(m.org_id);
        if (!e) {
            continue;
        }

        memcpy(dst, &m.org_id, 4u); dst += 4u;
        memcpy(dst, &m.total_output, sizeof(q32_32)); dst += sizeof(q32_32);
        memcpy(dst, &m.total_input, sizeof(q32_32)); dst += sizeof(q32_32);
        memcpy(dst, &m.net_throughput, sizeof(q32_32)); dst += sizeof(q32_32);
        memcpy(dst, &m.price_index, sizeof(q32_32)); dst += sizeof(q32_32);

        memcpy(dst, &e->step_out_value, sizeof(q32_32)); dst += sizeof(q32_32);
        memcpy(dst, &e->step_out_qty, sizeof(q32_32)); dst += sizeof(q32_32);
        memcpy(dst, &e->step_in_value, sizeof(q32_32)); dst += sizeof(q32_32);
        memcpy(dst, &e->step_in_qty, sizeof(q32_32)); dst += sizeof(q32_32);

        memcpy(dst, &pad, 4u); dst += 4u;
        written += 1u;
    }

    /* Fix-up count to written to avoid hashing uninitialized trailing bytes. */
    if (written != count) {
        u32 fixed_total = 8u + written * (4u + sizeof(q32_32) * 8u + 4u);
        memcpy(buf + 4u, &written, 4u);
        out->ptr = buf;
        out->len = fixed_total;
        return 0;
    }

    out->ptr = buf;
    out->len = total;
    return 0;
}

static int d_econ_load_instance(struct d_world *w, const struct d_tlv_blob *in) {
    const unsigned char *ptr;
    u32 remaining;
    u32 version;
    u32 count;
    u32 i;

    (void)w;
    d_econ_metrics_shutdown();
    (void)d_econ_metrics_init();

    if (!in || !in->ptr || in->len == 0u) {
        return 0;
    }

    ptr = in->ptr;
    remaining = in->len;
    if (remaining < 8u) {
        return -1;
    }
    memcpy(&version, ptr, 4u); ptr += 4u; remaining -= 4u;
    memcpy(&count, ptr, 4u); ptr += 4u; remaining -= 4u;
    if (version != 1u) {
        return -1;
    }

    for (i = 0u; i < count; ++i) {
        d_org_id org_id;
        d_econ_org_metrics m;
        decon_entry *e;
        u32 pad;

        if (remaining < (4u + sizeof(q32_32) * 8u + 4u)) {
            return -1;
        }
        memcpy(&org_id, ptr, 4u); ptr += 4u;
        memcpy(&m.total_output, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&m.total_input, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&m.net_throughput, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&m.price_index, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);

        m.org_id = org_id;

        e = decon_alloc(org_id);
        if (!e) {
            return -1;
        }

        e->ema_out = m.total_output;
        e->ema_in = m.total_input;
        e->ema_price = m.price_index;

        memcpy(&e->step_out_value, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&e->step_out_qty, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&e->step_in_value, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&e->step_in_qty, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);

        memcpy(&pad, ptr, 4u); ptr += 4u;
        (void)pad;

        e->metrics = m;
        remaining -= (u32)(4u + sizeof(q32_32) * 8u + 4u);
    }

    return remaining == 0u ? 0 : -1;
}

static void d_econ_register_models(void) {
    /* No standalone models. */
}

static void d_econ_load_protos(const struct d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_econ_subsystem = {
    D_SUBSYS_ECON,
    "econ",
    1u,
    d_econ_register_models,
    d_econ_load_protos,
    d_econ_init_instance_subsys,
    d_econ_tick_subsys,
    d_econ_save_chunk,
    d_econ_load_chunk,
    d_econ_save_instance,
    d_econ_load_instance
};

void d_econ_register_subsystem(void) {
    if (g_econ_registered) {
        return;
    }
    if (d_subsystem_register(&g_econ_subsystem) == 0) {
        g_econ_registered = 1;
    }
}

