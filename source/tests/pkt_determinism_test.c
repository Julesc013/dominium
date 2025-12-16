/*
FILE: source/tests/pkt_determinism_test.c
MODULE: Repository
LAYER / SUBSYSTEM: source/tests
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <string.h>

#include "res/dg_tlv_canon.h"
#include "sim/pkt/dg_pkt_common.h"
#include "sim/pkt/pkt_hash.h"
#include "sim/pkt/registry/dg_type_registry.h"

#define TASSERT(cond, msg) do { \
    if (!(cond)) { \
        printf("FAIL: %s (line %u)\n", (msg), (unsigned int)__LINE__); \
        return 1; \
    } \
} while (0)

static u64 fnv1a64_bytes(u64 h, const unsigned char *data, u32 len) {
    u32 i;
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 fnv1a64_u64_le(u64 h, u64 v) {
    unsigned char buf[8];
    dg_le_write_u64(buf, v);
    return fnv1a64_bytes(h, buf, 8u);
}

static u64 fnv1a64_u16_le(u64 h, u16 v) {
    unsigned char buf[2];
    dg_le_write_u16(buf, v);
    return fnv1a64_bytes(h, buf, 2u);
}

static void tlv_write(unsigned char *buf, u32 *io_off, u32 tag, const unsigned char *payload, u32 payload_len) {
    u32 off = *io_off;
    dg_le_write_u32(buf + off, tag);
    dg_le_write_u32(buf + off + 4u, payload_len);
    off += 8u;
    if (payload_len != 0u) {
        memcpy(buf + off, payload, (size_t)payload_len);
        off += payload_len;
    }
    *io_off = off;
}

static int test_registry_determinism(void) {
    dg_type_registry reg_a;
    dg_type_registry reg_b;
    dg_type_registry_entry entries[6];
    u32 order_a[6] = { 2u, 0u, 5u, 1u, 3u, 4u };
    u32 order_b[6] = { 4u, 3u, 1u, 5u, 0u, 2u };
    u32 i;
    u64 hash_a;
    u64 hash_b;

    /* Same entries, different insertion orders. */
    entries[0].type_id = 50u;  entries[0].schema_id = 2u; entries[0].schema_ver_min = 1u; entries[0].schema_ver_max = 1u; entries[0].name = "t50_s2_v1"; entries[0].validate_fn = (dg_type_validate_fn)0;
    entries[1].type_id = 50u;  entries[1].schema_id = 1u; entries[1].schema_ver_min = 2u; entries[1].schema_ver_max = 2u; entries[1].name = "t50_s1_v2"; entries[1].validate_fn = (dg_type_validate_fn)0;
    entries[2].type_id = 50u;  entries[2].schema_id = 1u; entries[2].schema_ver_min = 1u; entries[2].schema_ver_max = 1u; entries[2].name = "t50_s1_v1"; entries[2].validate_fn = (dg_type_validate_fn)0;
    entries[3].type_id = 100u; entries[3].schema_id = 1u; entries[3].schema_ver_min = 1u; entries[3].schema_ver_max = 1u; entries[3].name = "t100_s1_v1"; entries[3].validate_fn = (dg_type_validate_fn)0;
    entries[4].type_id = 100u; entries[4].schema_id = 1u; entries[4].schema_ver_min = 3u; entries[4].schema_ver_max = 3u; entries[4].name = "t100_s1_v3"; entries[4].validate_fn = (dg_type_validate_fn)0;
    entries[5].type_id = 200u; entries[5].schema_id = 9u; entries[5].schema_ver_min = 1u; entries[5].schema_ver_max = 1u; entries[5].name = "t200_s9_v1"; entries[5].validate_fn = (dg_type_validate_fn)0;

    dg_type_registry_init(&reg_a);
    dg_type_registry_init(&reg_b);

    for (i = 0u; i < 6u; ++i) {
        TASSERT(dg_type_registry_add(&reg_a, &entries[order_a[i]]) == 0, "registry add A failed");
    }
    for (i = 0u; i < 6u; ++i) {
        TASSERT(dg_type_registry_add(&reg_b, &entries[order_b[i]]) == 0, "registry add B failed");
    }

    TASSERT(dg_type_registry_count(&reg_a) == 6u, "registry count A");
    TASSERT(dg_type_registry_count(&reg_b) == 6u, "registry count B");

    /* Verify identical canonical iteration and compute aggregate hash. */
    hash_a = 14695981039346656037ULL;
    hash_b = 14695981039346656037ULL;
    for (i = 0u; i < 6u; ++i) {
        const dg_type_registry_entry *ea = dg_type_registry_at(&reg_a, i);
        const dg_type_registry_entry *eb = dg_type_registry_at(&reg_b, i);
        TASSERT(ea && eb, "registry at");
        TASSERT(ea->type_id == eb->type_id, "type_id mismatch");
        TASSERT(ea->schema_id == eb->schema_id, "schema_id mismatch");
        TASSERT(ea->schema_ver_min == eb->schema_ver_min, "schema_ver_min mismatch");
        TASSERT(ea->schema_ver_max == eb->schema_ver_max, "schema_ver_max mismatch");

        if (i > 0u) {
            const dg_type_registry_entry *prev = dg_type_registry_at(&reg_a, i - 1u);
            TASSERT(prev, "registry prev");
            TASSERT(prev->type_id < ea->type_id ||
                    (prev->type_id == ea->type_id && (prev->schema_id < ea->schema_id ||
                     (prev->schema_id == ea->schema_id && prev->schema_ver_min <= ea->schema_ver_min))),
                    "canonical ordering violated");
        }

        hash_a = fnv1a64_u64_le(hash_a, (u64)ea->type_id);
        hash_a = fnv1a64_u64_le(hash_a, (u64)ea->schema_id);
        hash_a = fnv1a64_u16_le(hash_a, ea->schema_ver_min);
        hash_a = fnv1a64_u16_le(hash_a, ea->schema_ver_max);

        hash_b = fnv1a64_u64_le(hash_b, (u64)eb->type_id);
        hash_b = fnv1a64_u64_le(hash_b, (u64)eb->schema_id);
        hash_b = fnv1a64_u16_le(hash_b, eb->schema_ver_min);
        hash_b = fnv1a64_u16_le(hash_b, eb->schema_ver_max);
    }

    TASSERT(hash_a == hash_b, "registry aggregate hash mismatch");

    dg_type_registry_free(&reg_a);
    dg_type_registry_free(&reg_b);
    return 0;
}

static int test_tlv_canon_determinism(void) {
    unsigned char tlv_a[64];
    unsigned char tlv_b[64];
    unsigned char canon_a[64];
    unsigned char canon_b[64];
    u32 off_a = 0u;
    u32 off_b = 0u;
    u32 out_a = 0u;
    u32 out_b = 0u;
    unsigned char v1[4];
    unsigned char v2[2];
    unsigned char v3[2];
    u64 h_a;
    u64 h_b;

    dg_le_write_u32(v1, 0x11223344u);
    dg_le_write_u16(v2, 123u);
    dg_le_write_u16(v3, 1u);

    /* Same logical records, different ordering. Includes repeated tag=5 with different payloads. */
    tlv_write(tlv_a, &off_a, 10u, v1, 4u);
    tlv_write(tlv_a, &off_a, 5u, v2, 2u);
    tlv_write(tlv_a, &off_a, 5u, v3, 2u);

    tlv_write(tlv_b, &off_b, 5u, v3, 2u);
    tlv_write(tlv_b, &off_b, 10u, v1, 4u);
    tlv_write(tlv_b, &off_b, 5u, v2, 2u);

    TASSERT(dg_tlv_canon(tlv_a, off_a, canon_a, sizeof(canon_a), &out_a) == 0, "canon A failed");
    TASSERT(dg_tlv_canon(tlv_b, off_b, canon_b, sizeof(canon_b), &out_b) == 0, "canon B failed");
    TASSERT(out_a == out_b, "canon length mismatch");
    TASSERT(memcmp(canon_a, canon_b, (size_t)out_a) == 0, "canon bytes mismatch");

    h_a = fnv1a64_bytes(14695981039346656037ULL, canon_a, out_a);
    h_b = fnv1a64_bytes(14695981039346656037ULL, canon_b, out_b);
    TASSERT(h_a == h_b, "canon hash mismatch");
    return 0;
}

static int test_packet_hash_determinism(void) {
    unsigned char tlv_a[64];
    unsigned char tlv_b[64];
    u32 off_a = 0u;
    u32 off_b = 0u;
    unsigned char v1[4];
    unsigned char v2[4];
    dg_pkt_hdr hdr;
    dg_pkt_hash ha;
    dg_pkt_hash hb;

    dg_le_write_u32(v1, 7u);
    dg_le_write_u32(v2, 42u);

    /* Same fields, different ordering. */
    tlv_write(tlv_a, &off_a, 2u, v2, 4u);
    tlv_write(tlv_a, &off_a, 1u, v1, 4u);

    tlv_write(tlv_b, &off_b, 1u, v1, 4u);
    tlv_write(tlv_b, &off_b, 2u, v2, 4u);

    dg_pkt_hdr_clear(&hdr);
    hdr.type_id = 0xABCDEFu;
    hdr.schema_id = 0x1111222233334444ULL;
    hdr.schema_ver = 1u;
    hdr.flags = DG_PKT_FLAG_NONE;
    hdr.tick = 99u;
    hdr.src_entity = 1u;
    hdr.dst_entity = 2u;
    hdr.domain_id = 3u;
    hdr.chunk_id = 4u;
    hdr.seq = 123u;
    hdr.payload_len = off_a;

    TASSERT(off_a == off_b, "payload length mismatch");
    TASSERT(dg_pkt_hash_compute(&ha, &hdr, tlv_a, off_a) == 0, "pkt hash A failed");
    TASSERT(dg_pkt_hash_compute(&hb, &hdr, tlv_b, off_b) == 0, "pkt hash B failed");
    TASSERT(ha == hb, "packet hash mismatch");
    return 0;
}

int main(void) {
    TASSERT(test_registry_determinism() == 0, "registry determinism");
    TASSERT(test_tlv_canon_determinism() == 0, "tlv canon determinism");
    TASSERT(test_packet_hash_determinism() == 0, "packet hash determinism");
    printf("OK: domino_pkt_determinism_test\n");
    return 0;
}

