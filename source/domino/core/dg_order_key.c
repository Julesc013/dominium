#include "core/dg_order_key.h"

void dg_order_key_clear(dg_order_key *k) {
    if (!k) {
        return;
    }
    k->phase = 0u;
    k->_pad16 = 0u;
    k->domain_id = 0u;
    k->chunk_id = 0u;
    k->entity_id = 0u;
    k->component_id = 0u;
    k->type_id = 0u;
    k->seq = 0u;
    k->_pad32 = 0u;
}

dg_order_key dg_order_key_make(
    u16          phase,
    dg_domain_id domain_id,
    dg_chunk_id  chunk_id,
    dg_entity_id entity_id,
    u64          component_id,
    dg_type_id   type_id,
    u32          seq
) {
    dg_order_key k;
    k.phase = phase;
    k._pad16 = 0u;
    k.domain_id = domain_id;
    k.chunk_id = chunk_id;
    k.entity_id = entity_id;
    k.component_id = component_id;
    k.type_id = type_id;
    k.seq = seq;
    k._pad32 = 0u;
    return k;
}

dg_order_key dg_order_key_from_pkt_hdr(u16 phase, const dg_pkt_hdr *hdr, u64 component_id) {
    if (!hdr) {
        return dg_order_key_make(phase, 0u, 0u, 0u, component_id, 0u, 0u);
    }
    return dg_order_key_make(
        phase,
        hdr->domain_id,
        hdr->chunk_id,
        hdr->src_entity,
        component_id,
        hdr->type_id,
        hdr->seq
    );
}

static int dg_cmp_u16(u16 a, u16 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static int dg_cmp_u32(u32 a, u32 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static int dg_cmp_u64(u64 a, u64 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

int dg_order_key_cmp(const dg_order_key *a, const dg_order_key *b) {
    int c;
    if (a == b) {
        return 0;
    }
    if (!a) {
        return -1;
    }
    if (!b) {
        return 1;
    }

    c = dg_cmp_u16(a->phase, b->phase);
    if (c) return c;
    c = dg_cmp_u64(a->domain_id, b->domain_id);
    if (c) return c;
    c = dg_cmp_u64(a->chunk_id, b->chunk_id);
    if (c) return c;
    c = dg_cmp_u64(a->entity_id, b->entity_id);
    if (c) return c;
    c = dg_cmp_u64(a->component_id, b->component_id);
    if (c) return c;
    c = dg_cmp_u64(a->type_id, b->type_id);
    if (c) return c;
    c = dg_cmp_u32(a->seq, b->seq);
    if (c) return c;
    return 0;
}

