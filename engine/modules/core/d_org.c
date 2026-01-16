/*
FILE: source/domino/core/d_org.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_org
RESPONSIBILITY: Implements `d_org`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "core/d_org.h"

#include "core/d_subsystem.h"
#include "domino/core/d_tlv.h"
#include "research/d_research_state.h"

#define DORG_MAX 1024u

typedef struct d_org_entry_s {
    d_org org;
    int   in_use;
} d_org_entry;

static d_org_entry g_orgs[DORG_MAX];
static d_org_id g_next_org_id = 1u;
static int g_orgs_initialized = 0;
static int g_org_registered = 0;

static d_org_entry *d_org_find(d_org_id id) {
    u32 i;
    if (id == 0u) {
        return (d_org_entry *)0;
    }
    for (i = 0u; i < DORG_MAX; ++i) {
        if (g_orgs[i].in_use && g_orgs[i].org.id == id) {
            return &g_orgs[i];
        }
    }
    return (d_org_entry *)0;
}

static d_org_entry *d_org_alloc(void) {
    u32 i;
    for (i = 0u; i < DORG_MAX; ++i) {
        if (!g_orgs[i].in_use) {
            return &g_orgs[i];
        }
    }
    return (d_org_entry *)0;
}

int d_org_system_init(void) {
    if (g_orgs_initialized) {
        return 0;
    }
    memset(g_orgs, 0, sizeof(g_orgs));
    g_next_org_id = 1u;
    g_orgs_initialized = 1;
    (void)d_account_system_init();
    return 0;
}

void d_org_system_shutdown(void) {
    memset(g_orgs, 0, sizeof(g_orgs));
    g_next_org_id = 1u;
    g_orgs_initialized = 0;
}

d_org_id d_org_create(q32_32 initial_balance) {
    d_org_entry *e;
    d_org_id id;
    d_account_id account_id;

    if (!g_orgs_initialized) {
        (void)d_org_system_init();
    }

    e = d_org_alloc();
    if (!e) {
        return 0u;
    }
    account_id = d_account_create(initial_balance);
    if (account_id == 0u) {
        return 0u;
    }

    id = g_next_org_id++;
    memset(e, 0, sizeof(*e));
    e->org.id = id;
    e->org.priority = 0;
    e->org.account_id = account_id;
    e->in_use = 1;

    if (id >= g_next_org_id) {
        g_next_org_id = id + 1u;
    }

    (void)d_research_org_init(id);

    return id;
}

int d_org_get(d_org_id id, d_org *out) {
    d_org_entry *e;
    if (!out) {
        return -1;
    }
    e = d_org_find(id);
    if (!e) {
        return -1;
    }
    *out = e->org;
    return 0;
}

int d_org_update(const d_org *org) {
    d_org_entry *e;
    if (!org || org->id == 0u) {
        return -1;
    }
    e = d_org_find(org->id);
    if (!e) {
        return -1;
    }
    e->org = *org;
    return 0;
}

u32 d_org_count(void) {
    u32 i;
    u32 count = 0u;
    for (i = 0u; i < DORG_MAX; ++i) {
        if (g_orgs[i].in_use) {
            count += 1u;
        }
    }
    return count;
}

static void d_org_sort_ids(d_org_id *ids, u32 count) {
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

int d_org_get_by_index(u32 index, d_org *out) {
    d_org_id ids[DORG_MAX];
    u32 i;
    u32 count = 0u;

    if (!out) {
        return -1;
    }

    for (i = 0u; i < DORG_MAX; ++i) {
        if (g_orgs[i].in_use) {
            ids[count++] = g_orgs[i].org.id;
        }
    }
    if (index >= count) {
        return -1;
    }
    d_org_sort_ids(ids, count);
    return d_org_get(ids[index], out);
}

static int d_org_save_chunk(struct d_world *w, struct d_chunk *chunk, struct d_tlv_blob *out) {
    (void)w;
    (void)chunk;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_org_load_chunk(struct d_world *w, struct d_chunk *chunk, const struct d_tlv_blob *in) {
    (void)w;
    (void)chunk;
    (void)in;
    return 0;
}

static void d_org_init_instance_subsys(struct d_world *w) {
    (void)w;
    d_account_system_shutdown();
    d_org_system_shutdown();
    (void)d_account_system_init();
    (void)d_org_system_init();
}

static void d_org_tick_subsys(struct d_world *w, u32 ticks) {
    (void)w;
    (void)ticks;
}

static int d_org_save_instance(struct d_world *w, struct d_tlv_blob *out) {
    u32 version;
    u32 count;
    u32 total;
    unsigned char *buf;
    unsigned char *dst;
    u32 i;

    (void)w;
    if (!out) {
        return -1;
    }

    out->ptr = (unsigned char *)0;
    out->len = 0u;

    count = d_org_count();
    if (count == 0u) {
        return 0;
    }

    version = 1u;
    total = 0u;
    total += 4u; /* version */
    total += 4u; /* count */
    total += count * (
        sizeof(d_org_id) +
        sizeof(q32_32) +
        sizeof(d_account_id) +
        sizeof(q32_32)
    );

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;
    memcpy(dst, &version, 4u); dst += 4u;
    memcpy(dst, &count, 4u); dst += 4u;

    for (i = 0u; i < count; ++i) {
        d_org o;
        d_account acc;
        q32_32 bal = 0;
        if (d_org_get_by_index(i, &o) != 0) {
            continue;
        }
        if (d_account_get(o.account_id, &acc) == 0) {
            bal = acc.balance;
        }
        memcpy(dst, &o.id, sizeof(d_org_id)); dst += sizeof(d_org_id);
        memcpy(dst, &o.priority, sizeof(q32_32)); dst += sizeof(q32_32);
        memcpy(dst, &o.account_id, sizeof(d_account_id)); dst += sizeof(d_account_id);
        memcpy(dst, &bal, sizeof(q32_32)); dst += sizeof(q32_32);
    }

    out->ptr = buf;
    out->len = total;
    return 0;
}

static int d_org_load_instance(struct d_world *w, const struct d_tlv_blob *in) {
    const unsigned char *ptr;
    u32 remaining;
    u32 version;
    u32 count;
    u32 i;

    (void)w;
    d_account_system_shutdown();
    d_org_system_shutdown();
    (void)d_account_system_init();
    (void)d_org_system_init();

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
        d_org_entry *slot;
        d_org_id id;
        q32_32 priority;
        d_account_id account_id;
        q32_32 balance;

        if (remaining < sizeof(d_org_id) + sizeof(q32_32) + sizeof(d_account_id) + sizeof(q32_32)) {
            return -1;
        }
        memcpy(&id, ptr, sizeof(d_org_id)); ptr += sizeof(d_org_id);
        memcpy(&priority, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&account_id, ptr, sizeof(d_account_id)); ptr += sizeof(d_account_id);
        memcpy(&balance, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        remaining -= (u32)(sizeof(d_org_id) + sizeof(q32_32) + sizeof(d_account_id) + sizeof(q32_32));

        if (id == 0u || account_id == 0u) {
            return -1;
        }
        if (d_account_create_with_id(account_id, balance) != 0) {
            return -1;
        }

        if (d_org_find(id)) {
            return -1;
        }
        slot = d_org_alloc();
        if (!slot) {
            return -1;
        }
        memset(slot, 0, sizeof(*slot));
        slot->org.id = id;
        slot->org.priority = priority;
        slot->org.account_id = account_id;
        slot->in_use = 1;

        if (id >= g_next_org_id) {
            g_next_org_id = id + 1u;
        }
    }

    return remaining == 0u ? 0 : -1;
}

static void d_org_register_models(void) {
    /* No standalone models. */
}

static void d_org_load_protos(const struct d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_org_subsystem = {
    D_SUBSYS_ORG,
    "org",
    1u,
    d_org_register_models,
    d_org_load_protos,
    d_org_init_instance_subsys,
    d_org_tick_subsys,
    d_org_save_chunk,
    d_org_load_chunk,
    d_org_save_instance,
    d_org_load_instance
};

void d_org_register_subsystem(void) {
    if (g_org_registered) {
        return;
    }
    if (d_subsystem_register(&g_org_subsystem) == 0) {
        g_org_registered = 1;
    }
}
