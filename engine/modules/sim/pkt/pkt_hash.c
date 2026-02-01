/*
FILE: source/domino/sim/pkt/pkt_hash.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/pkt/pkt_hash
RESPONSIBILITY: Implements `pkt_hash`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include "sim/pkt/pkt_hash.h"

#define DG_FNV1A64_OFFSET 14695981039346656037ULL
#define DG_FNV1A64_PRIME  1099511628211ULL

static u64 dg_hash64_update_bytes(u64 h, const unsigned char *data, u32 len) {
    u32 i;
    if (!data || len == 0u) {
        return h;
    }
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= DG_FNV1A64_PRIME;
    }
    return h;
}

static u64 dg_hash64_update_u16_le(u64 h, u16 v) {
    unsigned char buf[2];
    dg_le_write_u16(buf, v);
    return dg_hash64_update_bytes(h, buf, 2u);
}

static u64 dg_hash64_update_u32_le(u64 h, u32 v) {
    unsigned char buf[4];
    dg_le_write_u32(buf, v);
    return dg_hash64_update_bytes(h, buf, 4u);
}

static u64 dg_hash64_update_u64_le(u64 h, u64 v) {
    unsigned char buf[8];
    dg_le_write_u64(buf, v);
    return dg_hash64_update_bytes(h, buf, 8u);
}

u64 dg_hash64_fnv1a_cstr(const char *s) {
    u64 h = DG_FNV1A64_OFFSET;
    const unsigned char *p = (const unsigned char *)s;
    if (!s) {
        return 0u;
    }
    while (*p) {
        h ^= (u64)(*p++);
        h *= DG_FNV1A64_PRIME;
    }
    return h;
}

static u64 dg_pkt_hash_hdr(u64 h, const dg_pkt_hdr *hdr) {
    h = dg_hash64_update_u64_le(h, (u64)hdr->type_id);
    h = dg_hash64_update_u64_le(h, (u64)hdr->schema_id);
    h = dg_hash64_update_u16_le(h, hdr->schema_ver);
    h = dg_hash64_update_u16_le(h, hdr->flags);
    h = dg_hash64_update_u64_le(h, (u64)hdr->tick);
    h = dg_hash64_update_u64_le(h, (u64)hdr->src_entity);
    h = dg_hash64_update_u64_le(h, (u64)hdr->dst_entity);
    h = dg_hash64_update_u64_le(h, (u64)hdr->domain_id);
    h = dg_hash64_update_u64_le(h, (u64)hdr->chunk_id);
    h = dg_hash64_update_u32_le(h, hdr->seq);
    h = dg_hash64_update_u32_le(h, hdr->payload_len);
    return h;
}

int dg_pkt_hash_compute_canon(
    dg_pkt_hash        *out_hash,
    const dg_pkt_hdr   *hdr,
    const unsigned char *canon_payload,
    u32                 payload_len
) {
    u64 h;
    if (!out_hash || !hdr) {
        return -1;
    }
    if (!canon_payload && payload_len != 0u) {
        return -2;
    }
    if (hdr->payload_len != payload_len) {
        return -3;
    }

    h = DG_FNV1A64_OFFSET;
    h = dg_pkt_hash_hdr(h, hdr);
    h = dg_hash64_update_bytes(h, canon_payload, payload_len);
    *out_hash = h;
    return 0;
}

int dg_pkt_hash_compute(
    dg_pkt_hash        *out_hash,
    const dg_pkt_hdr   *hdr,
    const unsigned char *payload,
    u32                 payload_len
) {
    unsigned char *canon;
    u32 canon_len;
    int rc;

    if (!out_hash || !hdr) {
        return -1;
    }
    if (!payload && payload_len != 0u) {
        return -2;
    }
    if (hdr->payload_len != payload_len) {
        return -3;
    }

    canon = (unsigned char *)0;
    canon_len = 0u;

    if (payload_len != 0u) {
        canon = (unsigned char *)malloc((size_t)payload_len);
        if (!canon) {
            return -4;
        }
        rc = dg_tlv_canon(payload, payload_len, canon, payload_len, &canon_len);
        if (rc != 0 || canon_len != payload_len) {
            free(canon);
            return -5;
        }
    }

    rc = dg_pkt_hash_compute_canon(out_hash, hdr, canon ? canon : payload, payload_len);
    if (canon) {
        free(canon);
    }
    return rc;
}

