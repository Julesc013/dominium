/*
FILE: source/domino/sim/pkt/idmap/dg_idmap.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/pkt/idmap/dg_idmap
RESPONSIBILITY: Implements `dg_idmap`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "res/dg_tlv_canon.h"
#include "sim/pkt/idmap/dg_idmap.h"

static int dg_idmap_entry_cmp(const void *a, const void *b) {
    const dg_idmap_entry *ea = (const dg_idmap_entry *)a;
    const dg_idmap_entry *eb = (const dg_idmap_entry *)b;
    if (ea->external_id < eb->external_id) return -1;
    if (ea->external_id > eb->external_id) return 1;
    if (ea->runtime_id < eb->runtime_id) return -1;
    if (ea->runtime_id > eb->runtime_id) return 1;
    return 0;
}

void dg_idmap_init(dg_idmap *m) {
    if (!m) {
        return;
    }
    m->entries = (dg_idmap_entry *)0;
    m->count = 0u;
    m->capacity = 0u;
}

void dg_idmap_free(dg_idmap *m) {
    if (!m) {
        return;
    }
    if (m->entries) {
        free(m->entries);
    }
    m->entries = (dg_idmap_entry *)0;
    m->count = 0u;
    m->capacity = 0u;
}

static int dg_idmap_reserve(dg_idmap *m, u32 cap) {
    dg_idmap_entry *new_entries;
    if (!m) {
        return -1;
    }
    if (cap <= m->capacity) {
        return 0;
    }
    new_entries = (dg_idmap_entry *)realloc(m->entries, sizeof(dg_idmap_entry) * (size_t)cap);
    if (!new_entries) {
        return -2;
    }
    m->entries = new_entries;
    m->capacity = cap;
    return 0;
}

int dg_idmap_load_tlv(dg_idmap *m, const unsigned char *tlv, u32 tlv_len) {
    u32 offset = 0u;
    u32 tag;
    const unsigned char *payload;
    u32 payload_len;
    dg_idmap_entry tmp;
    int rc;

    if (!m) {
        return -1;
    }

    /* Replace existing contents. */
    dg_idmap_free(m);
    dg_idmap_init(m);

    if (!tlv && tlv_len != 0u) {
        return -2;
    }

    for (;;) {
        rc = dg_tlv_next(tlv, tlv_len, &offset, &tag, &payload, &payload_len);
        if (rc != 0) {
            break;
        }

        if (tag != DG_IDMAP_TLV_ENTRY) {
            continue; /* forward-compat: ignore unknown tags */
        }
        if (payload_len != 16u) {
            dg_idmap_free(m);
            return -3;
        }

        tmp.external_id = dg_le_read_u64(payload);
        tmp.runtime_id = dg_le_read_u64(payload + 8u);

        if (m->count >= m->capacity) {
            u32 new_cap = (m->capacity == 0u) ? 32u : (m->capacity * 2u);
            rc = dg_idmap_reserve(m, new_cap);
            if (rc != 0) {
                dg_idmap_free(m);
                return -4;
            }
        }
        m->entries[m->count] = tmp;
        m->count += 1u;
    }

    if (rc != 1) {
        dg_idmap_free(m);
        return rc; /* malformed TLV */
    }

    if (m->count > 1u) {
        qsort(m->entries, (size_t)m->count, sizeof(dg_idmap_entry), dg_idmap_entry_cmp);
    }

    /* Reject duplicates (same external_id). */
    if (m->count > 1u) {
        u32 i;
        for (i = 1u; i < m->count; ++i) {
            if (m->entries[i - 1u].external_id == m->entries[i].external_id) {
                dg_idmap_free(m);
                return -5;
            }
        }
    }

    return 0;
}

int dg_idmap_lookup(const dg_idmap *m, u64 external_id, u64 *out_runtime_id) {
    u32 lo, hi, mid;

    if (!m || !out_runtime_id) {
        return -1;
    }
    if (m->count == 0u || !m->entries) {
        return 1;
    }

    lo = 0u;
    hi = m->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (m->entries[mid].external_id < external_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < m->count && m->entries[lo].external_id == external_id) {
        *out_runtime_id = m->entries[lo].runtime_id;
        return 0;
    }

    return 1;
}

u32 dg_idmap_count(const dg_idmap *m) {
    return m ? m->count : 0u;
}

const dg_idmap_entry *dg_idmap_at(const dg_idmap *m, u32 index) {
    if (!m || index >= m->count) {
        return (const dg_idmap_entry *)0;
    }
    return &m->entries[index];
}

