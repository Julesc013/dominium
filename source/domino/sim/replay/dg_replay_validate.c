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

int dg_replay_validate(
    dg_replay_validate_mode mode,
    const dg_replay_stream *expected,
    const dg_replay_stream *actual,
    dg_replay_mismatch     *out_mismatch
) {
    u32 tick_count;
    u32 i;
    u32 d;

    if (out_mismatch) {
        dg_replay_mismatch_clear(out_mismatch);
        out_mismatch->mode = mode;
        out_mismatch->expected_tick_index = 0u;
        out_mismatch->actual_tick_index = 0u;
    }

    if (!expected || !actual) {
        return -1;
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

            if (!dg_replay_domain_selected(mode, flags)) {
                continue;
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

