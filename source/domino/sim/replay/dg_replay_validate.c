#include <string.h>

#include "sim/replay/dg_replay_validate.h"

void dg_replay_mismatch_clear(dg_replay_mismatch *m) {
    if (!m) {
        return;
    }
    memset(m, 0, sizeof(*m));
    m->ok = D_TRUE;
}

static d_bool dg_replay_domain_selected(dg_replay_validate_mode mode, u32 domain_flags) {
    switch (mode) {
        case DG_REPLAY_VALIDATE_STRICT:
            return D_TRUE;
        case DG_REPLAY_VALIDATE_STRUCTURAL:
            return (domain_flags & DG_HASH_DOMAIN_F_STRUCTURAL) ? D_TRUE : D_FALSE;
        case DG_REPLAY_VALIDATE_BEHAVIORAL:
            return (domain_flags & DG_HASH_DOMAIN_F_BEHAVIORAL) ? D_TRUE : D_FALSE;
        default:
            break;
    }
    return D_FALSE;
}

static int dg_replay_compare_content_pack_ids(
    const dg_replay_stream *expected,
    const dg_replay_stream *actual,
    dg_replay_mismatch     *out_mismatch
) {
    u32 i;
    u32 ne;
    u32 na;

    if (!expected || !actual) {
        return -1;
    }

    ne = expected->content_pack_count;
    na = actual->content_pack_count;
    if (ne != na) {
        if (out_mismatch) {
            out_mismatch->ok = D_FALSE;
            out_mismatch->tick = 0u;
            out_mismatch->domain_id = DG_HASH_DOMAIN_DOMAIN_STATES;
            out_mismatch->expected_hash = (dg_hash_value)ne;
            out_mismatch->actual_hash = (dg_hash_value)na;
        }
        return 1;
    }

    for (i = 0u; i < ne; ++i) {
        u64 pe = expected->content_pack_ids ? expected->content_pack_ids[i] : 0u;
        u64 pa = actual->content_pack_ids ? actual->content_pack_ids[i] : 0u;
        if (pe != pa) {
            if (out_mismatch) {
                out_mismatch->ok = D_FALSE;
                out_mismatch->tick = 0u;
                out_mismatch->domain_id = DG_HASH_DOMAIN_DOMAIN_STATES;
                out_mismatch->expected_hash = (dg_hash_value)pe;
                out_mismatch->actual_hash = (dg_hash_value)pa;
            }
            return 1;
        }
    }

    return 0;
}

static int dg_replay_compare_id_remaps(
    const dg_replay_stream *expected,
    const dg_replay_stream *actual,
    dg_replay_mismatch     *out_mismatch
) {
    u32 i;
    u32 ne;
    u32 na;

    if (!expected || !actual) {
        return -1;
    }

    ne = expected->id_remap_count;
    na = actual->id_remap_count;
    if (ne != na) {
        if (out_mismatch) {
            out_mismatch->ok = D_FALSE;
            out_mismatch->tick = 0u;
            out_mismatch->domain_id = DG_HASH_DOMAIN_DOMAIN_STATES;
            out_mismatch->expected_hash = (dg_hash_value)ne;
            out_mismatch->actual_hash = (dg_hash_value)na;
        }
        return 1;
    }

    for (i = 0u; i < ne; ++i) {
        const dg_replay_id_remap *re = expected->id_remaps ? &expected->id_remaps[i] : (const dg_replay_id_remap *)0;
        const dg_replay_id_remap *ra = actual->id_remaps ? &actual->id_remaps[i] : (const dg_replay_id_remap *)0;
        u64 fe = re ? re->from_id : 0u;
        u64 fa = ra ? ra->from_id : 0u;
        u64 te = re ? re->to_id : 0u;
        u64 ta = ra ? ra->to_id : 0u;

        if (fe != fa) {
            if (out_mismatch) {
                out_mismatch->ok = D_FALSE;
                out_mismatch->tick = 0u;
                out_mismatch->domain_id = DG_HASH_DOMAIN_DOMAIN_STATES;
                out_mismatch->expected_hash = (dg_hash_value)fe;
                out_mismatch->actual_hash = (dg_hash_value)fa;
            }
            return 1;
        }
        if (te != ta) {
            if (out_mismatch) {
                out_mismatch->ok = D_FALSE;
                out_mismatch->tick = 0u;
                out_mismatch->domain_id = DG_HASH_DOMAIN_DOMAIN_STATES;
                out_mismatch->expected_hash = (dg_hash_value)te;
                out_mismatch->actual_hash = (dg_hash_value)ta;
            }
            return 1;
        }
    }

    return 0;
}

static int dg_replay_domain_tables_match(const dg_replay_stream *a, const dg_replay_stream *b) {
    u32 i;
    if (!a || !b) return 0;
    if (a->hash_domain_count != b->hash_domain_count) return 0;
    for (i = 0u; i < a->hash_domain_count; ++i) {
        if (dg_replay_stream_hash_domain_id_at(a, i) != dg_replay_stream_hash_domain_id_at(b, i)) return 0;
        if (dg_replay_stream_hash_domain_flags_at(a, i) != dg_replay_stream_hash_domain_flags_at(b, i)) return 0;
    }
    return 1;
}

static const unsigned char *dg_replay_pkt_payload_ptr(const dg_replay_stream *rs, const dg_replay_pkt *p) {
    if (!rs || !p) return (const unsigned char *)0;
    if (p->payload_len == 0u) return (const unsigned char *)0;
    if (!rs->arena || rs->arena_capacity == 0u) return (const unsigned char *)0;
    if (p->payload_off > rs->arena_capacity) return (const unsigned char *)0;
    if (p->payload_len > (rs->arena_capacity - p->payload_off)) return (const unsigned char *)0;
    return rs->arena + p->payload_off;
}

static int dg_replay_hdr_equal(const dg_pkt_hdr *a, const dg_pkt_hdr *b) {
    if (!a || !b) return 0;
    if (a->type_id != b->type_id) return 0;
    if (a->schema_id != b->schema_id) return 0;
    if (a->schema_ver != b->schema_ver) return 0;
    if (a->flags != b->flags) return 0;
    if (a->tick != b->tick) return 0;
    if (a->src_entity != b->src_entity) return 0;
    if (a->dst_entity != b->dst_entity) return 0;
    if (a->domain_id != b->domain_id) return 0;
    if (a->chunk_id != b->chunk_id) return 0;
    if (a->seq != b->seq) return 0;
    if (a->payload_len != b->payload_len) return 0;
    return 1;
}

static int dg_replay_compare_input_for_tick(
    const dg_replay_stream *expected,
    const dg_replay_stream *actual,
    dg_tick                 tick,
    u32                    *io_expected_index,
    u32                    *io_actual_index,
    dg_replay_mismatch     *out_mismatch
) {
    u32 be;
    u32 ea;
    u32 ba;
    u32 eb;
    u32 i;
    u32 ce;
    u32 ca;

    if (!expected || !actual || !io_expected_index || !io_actual_index) {
        return -1;
    }

    be = *io_expected_index;
    ba = *io_actual_index;

    while (be < expected->input_count && expected->input_pkts && expected->input_pkts[be].tick < tick) {
        be += 1u;
    }
    ea = be;
    while (ea < expected->input_count && expected->input_pkts && expected->input_pkts[ea].tick == tick) {
        ea += 1u;
    }

    while (ba < actual->input_count && actual->input_pkts && actual->input_pkts[ba].tick < tick) {
        ba += 1u;
    }
    eb = ba;
    while (eb < actual->input_count && actual->input_pkts && actual->input_pkts[eb].tick == tick) {
        eb += 1u;
    }

    ce = ea - be;
    ca = eb - ba;
    if (ce != ca) {
        if (out_mismatch) {
            out_mismatch->ok = D_FALSE;
            out_mismatch->tick = tick;
            out_mismatch->domain_id = DG_HASH_DOMAIN_PACKET_STREAMS;
            out_mismatch->expected_hash = (dg_hash_value)ce;
            out_mismatch->actual_hash = (dg_hash_value)ca;
        }
        return 1;
    }

    for (i = 0u; i < ce; ++i) {
        const dg_replay_pkt *pe = expected->input_pkts ? &expected->input_pkts[be + i] : (const dg_replay_pkt *)0;
        const dg_replay_pkt *pa = actual->input_pkts ? &actual->input_pkts[ba + i] : (const dg_replay_pkt *)0;

        if (!pe || !pa) {
            if (out_mismatch) {
                out_mismatch->ok = D_FALSE;
                out_mismatch->tick = tick;
                out_mismatch->domain_id = DG_HASH_DOMAIN_PACKET_STREAMS;
                out_mismatch->expected_hash = pe ? (dg_hash_value)pe->pkt_hash : 0u;
                out_mismatch->actual_hash = pa ? (dg_hash_value)pa->pkt_hash : 0u;
            }
            return 1;
        }

        if (!dg_replay_hdr_equal(&pe->hdr, &pa->hdr) || pe->payload_len != pa->payload_len) {
            if (out_mismatch) {
                out_mismatch->ok = D_FALSE;
                out_mismatch->tick = tick;
                out_mismatch->domain_id = DG_HASH_DOMAIN_PACKET_STREAMS;
                out_mismatch->expected_hash = (dg_hash_value)pe->pkt_hash;
                out_mismatch->actual_hash = (dg_hash_value)pa->pkt_hash;
            }
            return 1;
        }

        if (pe->payload_len != 0u) {
            const unsigned char *bpe = dg_replay_pkt_payload_ptr(expected, pe);
            const unsigned char *bpa = dg_replay_pkt_payload_ptr(actual, pa);
            if (!bpe || !bpa) {
                if (out_mismatch) {
                    out_mismatch->ok = D_FALSE;
                    out_mismatch->tick = tick;
                    out_mismatch->domain_id = DG_HASH_DOMAIN_PACKET_STREAMS;
                    out_mismatch->expected_hash = (dg_hash_value)pe->pkt_hash;
                    out_mismatch->actual_hash = (dg_hash_value)pa->pkt_hash;
                }
                return 1;
            }
            if (memcmp(bpe, bpa, (size_t)pe->payload_len) != 0) {
                if (out_mismatch) {
                    out_mismatch->ok = D_FALSE;
                    out_mismatch->tick = tick;
                    out_mismatch->domain_id = DG_HASH_DOMAIN_PACKET_STREAMS;
                    out_mismatch->expected_hash = (dg_hash_value)pe->pkt_hash;
                    out_mismatch->actual_hash = (dg_hash_value)pa->pkt_hash;
                }
                return 1;
            }
        }
    }

    *io_expected_index = ea;
    *io_actual_index = eb;
    return 0;
}

int dg_replay_validate(
    dg_replay_validate_mode mode,
    const dg_replay_stream *expected,
    const dg_replay_stream *actual,
    dg_replay_mismatch     *out_mismatch
) {
    u32 tick_count;
    u32 i;
    u32 d;
    u32 input_idx_expected = 0u;
    u32 input_idx_actual = 0u;

    if (out_mismatch) {
        dg_replay_mismatch_clear(out_mismatch);
        out_mismatch->mode = mode;
        out_mismatch->expected_tick_index = 0u;
        out_mismatch->actual_tick_index = 0u;
    }

    if (!expected || !actual) {
        return -1;
    }

    /* Structural metadata must match (authoring/topology). */
    if (mode == DG_REPLAY_VALIDATE_STRICT || mode == DG_REPLAY_VALIDATE_STRUCTURAL) {
        int rc_meta;
        rc_meta = dg_replay_compare_content_pack_ids(expected, actual, out_mismatch);
        if (rc_meta != 0) return (rc_meta < 0) ? rc_meta : 1;
        rc_meta = dg_replay_compare_id_remaps(expected, actual, out_mismatch);
        if (rc_meta != 0) return (rc_meta < 0) ? rc_meta : 1;
    }

    if (!dg_replay_domain_tables_match(expected, actual)) {
        if (out_mismatch) {
            out_mismatch->ok = D_FALSE;
            out_mismatch->tick = 0u;
            out_mismatch->domain_id = 0u;
            out_mismatch->expected_hash = (dg_hash_value)expected->hash_domain_count;
            out_mismatch->actual_hash = (dg_hash_value)actual->hash_domain_count;
        }
        return 1;
    }

    /* Tick count must match for strict validation. */
    if (mode == DG_REPLAY_VALIDATE_STRICT) {
        if (expected->tick_count != actual->tick_count) {
            if (out_mismatch) {
                out_mismatch->ok = D_FALSE;
                out_mismatch->tick = 0u;
                out_mismatch->domain_id = DG_HASH_DOMAIN_SCHEDULER_STATE;
                out_mismatch->expected_hash = (dg_hash_value)expected->tick_count;
                out_mismatch->actual_hash = (dg_hash_value)actual->tick_count;
            }
            return 1;
        }
        tick_count = expected->tick_count;
    } else {
        tick_count = (expected->tick_count < actual->tick_count) ? expected->tick_count : actual->tick_count;
    }

    for (i = 0u; i < tick_count; ++i) {
        dg_tick te = dg_replay_stream_tick_at(expected, i);
        dg_tick ta = dg_replay_stream_tick_at(actual, i);
        if (te != ta) {
            if (out_mismatch) {
                out_mismatch->ok = D_FALSE;
                out_mismatch->tick = (te < ta) ? te : ta;
                out_mismatch->domain_id = DG_HASH_DOMAIN_SCHEDULER_STATE;
                out_mismatch->expected_hash = (dg_hash_value)te;
                out_mismatch->actual_hash = (dg_hash_value)ta;
                out_mismatch->expected_tick_index = i;
                out_mismatch->actual_tick_index = i;
            }
            return 1;
        }

        for (d = 0u; d < expected->hash_domain_count; ++d) {
            u32 flags = dg_replay_stream_hash_domain_flags_at(expected, d);
            dg_hash_domain_id domain_id = dg_replay_stream_hash_domain_id_at(expected, d);
            dg_hash_value he;
            dg_hash_value ha;
            int rc_inputs;

            if (!dg_replay_domain_selected(mode, flags)) {
                continue;
            }

            if (domain_id == DG_HASH_DOMAIN_PACKET_STREAMS) {
                rc_inputs = dg_replay_compare_input_for_tick(expected, actual, te, &input_idx_expected, &input_idx_actual, out_mismatch);
                if (rc_inputs != 0) {
                    return (rc_inputs < 0) ? rc_inputs : 1;
                }
            }

            he = dg_replay_stream_hash_value_at(expected, i, d);
            ha = dg_replay_stream_hash_value_at(actual, i, d);
            if (he != ha) {
                if (out_mismatch) {
                    out_mismatch->ok = D_FALSE;
                    out_mismatch->tick = te;
                    out_mismatch->domain_id = domain_id;
                    out_mismatch->expected_hash = he;
                    out_mismatch->actual_hash = ha;
                    out_mismatch->expected_tick_index = i;
                    out_mismatch->actual_tick_index = i;
                }
                return 1;
            }
        }
    }

    return 0;
}
