/*
FILE: source/dominium/game/runtime/dom_qos.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_qos
RESPONSIBILITY: Implements QoS negotiation logic and TLV helpers (non-sim).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Logic must be deterministic for identical inputs.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_qos.h"

#include <cstring>

#include "dominium/core_tlv.h"

namespace {

static u32 dom_qos_max_u32(u32 a, u32 b) {
    return (a > b) ? a : b;
}

static u32 dom_qos_scale_u32(u32 v, u32 numer, u32 denom) {
    if (denom == 0u) {
        return v;
    }
    {
        const u64 num = (u64)v * (u64)numer + (u64)(denom / 2u);
        return (u32)(num / (u64)denom);
    }
}

static bool dom_qos_policy_equal(const dom_qos_policy &a, const dom_qos_policy &b) {
    return a.snapshot_hz == b.snapshot_hz &&
           a.delta_detail == b.delta_detail &&
           a.interest_radius_m == b.interest_radius_m &&
           a.recommended_profile == b.recommended_profile &&
           a.server_load_hint == b.server_load_hint &&
           a.assist_flags == b.assist_flags;
}

static void dom_qos_apply_reduction(dom_qos_policy &policy, u32 level) {
    if (level == DOM_QOS_REDUCTION_MILD) {
        if (policy.snapshot_hz > 0u) {
            policy.snapshot_hz = dom_qos_max_u32(1u, dom_qos_scale_u32(policy.snapshot_hz, 3u, 4u));
        }
        policy.delta_detail = dom_qos_scale_u32(policy.delta_detail, 3u, 4u);
        policy.interest_radius_m = dom_qos_scale_u32(policy.interest_radius_m, 4u, 5u);
    } else if (level == DOM_QOS_REDUCTION_MODERATE) {
        if (policy.snapshot_hz > 0u) {
            policy.snapshot_hz = dom_qos_max_u32(1u, dom_qos_scale_u32(policy.snapshot_hz, 1u, 2u));
        }
        policy.delta_detail = dom_qos_scale_u32(policy.delta_detail, 1u, 2u);
        policy.interest_radius_m = dom_qos_scale_u32(policy.interest_radius_m, 3u, 5u);
    } else if (level == DOM_QOS_REDUCTION_SEVERE) {
        if (policy.snapshot_hz > 0u) {
            policy.snapshot_hz = dom_qos_max_u32(1u, dom_qos_scale_u32(policy.snapshot_hz, 1u, 4u));
        }
        policy.delta_detail = dom_qos_scale_u32(policy.delta_detail, 3u, 10u);
        policy.interest_radius_m = dom_qos_scale_u32(policy.interest_radius_m, 2u, 5u);
    }
}

static void dom_qos_recompute(dom_qos_state *state) {
    dom_qos_policy effective;
    u32 reason = 0u;
    u32 reduction = 0u;
    u32 assist = 0u;

    if (!state) {
        return;
    }

    effective = state->base_policy;

    if (state->caps.max_snapshot_hz > 0u &&
        effective.snapshot_hz > state->caps.max_snapshot_hz) {
        effective.snapshot_hz = state->caps.max_snapshot_hz;
        reason |= DOM_QOS_REASON_CAPS_CLAMP;
    }
    if (state->caps.max_delta_detail > 0u &&
        effective.delta_detail > state->caps.max_delta_detail) {
        effective.delta_detail = state->caps.max_delta_detail;
        reason |= DOM_QOS_REASON_CAPS_CLAMP;
    }
    if (state->caps.max_interest_radius_m > 0u &&
        effective.interest_radius_m > state->caps.max_interest_radius_m) {
        effective.interest_radius_m = state->caps.max_interest_radius_m;
        reason |= DOM_QOS_REASON_CAPS_CLAMP;
    }
    if (state->caps.diagnostic_rate_cap > 0u &&
        effective.snapshot_hz > state->caps.diagnostic_rate_cap) {
        effective.snapshot_hz = state->caps.diagnostic_rate_cap;
        reason |= DOM_QOS_REASON_CAPS_CLAMP;
    }

    assist = effective.assist_flags & state->caps.assist_flags;
    if (assist != effective.assist_flags) {
        reason |= DOM_QOS_REASON_ASSIST_CLAMP;
        effective.assist_flags = assist;
    }

    if (effective.server_load_hint == DOM_QOS_SERVER_LOAD_OVERLOADED) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_SEVERE);
        reason |= DOM_QOS_REASON_SERVER_LOAD;
    } else if (effective.server_load_hint == DOM_QOS_SERVER_LOAD_BUSY) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MODERATE);
        reason |= DOM_QOS_REASON_SERVER_LOAD;
    }

    if (state->status.request_detail_reduction != 0u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MILD);
        reason |= DOM_QOS_REASON_STATUS_REDUCTION;
    }

    if (state->status.backlog_jobs >= 32u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_SEVERE);
        reason |= DOM_QOS_REASON_STATUS_BACKLOG;
    } else if (state->status.backlog_jobs >= 16u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MODERATE);
        reason |= DOM_QOS_REASON_STATUS_BACKLOG;
    } else if (state->status.backlog_jobs >= 8u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MILD);
        reason |= DOM_QOS_REASON_STATUS_BACKLOG;
    }

    if (state->status.derived_queue_pressure >= 90u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_SEVERE);
        reason |= DOM_QOS_REASON_STATUS_PRESSURE;
    } else if (state->status.derived_queue_pressure >= 75u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MODERATE);
        reason |= DOM_QOS_REASON_STATUS_PRESSURE;
    } else if (state->status.derived_queue_pressure >= 60u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MILD);
        reason |= DOM_QOS_REASON_STATUS_PRESSURE;
    }

    if (state->status.render_fps_avg > 0u) {
        if (state->status.render_fps_avg <= 20u) {
            reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_SEVERE);
            reason |= DOM_QOS_REASON_STATUS_FPS;
        } else if (state->status.render_fps_avg <= 30u) {
            reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MODERATE);
            reason |= DOM_QOS_REASON_STATUS_FPS;
        } else if (state->status.render_fps_avg <= 45u) {
            reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MILD);
            reason |= DOM_QOS_REASON_STATUS_FPS;
        }
    }
    if (state->status.frame_time_ms_avg > 0u) {
        if (state->status.frame_time_ms_avg >= 50u) {
            reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_SEVERE);
            reason |= DOM_QOS_REASON_STATUS_FPS;
        } else if (state->status.frame_time_ms_avg >= 33u) {
            reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MODERATE);
            reason |= DOM_QOS_REASON_STATUS_FPS;
        } else if (state->status.frame_time_ms_avg >= 25u) {
            reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MILD);
            reason |= DOM_QOS_REASON_STATUS_FPS;
        }
    }

    dom_qos_apply_reduction(effective, reduction);

    if (!dom_qos_policy_equal(state->effective_policy, effective) ||
        state->last_reason_mask != reason) {
        state->last_revision += 1u;
    }
    state->effective_policy = effective;
    state->last_reason_mask = reason;
}

} // namespace

int dom_qos_init(dom_qos_state *state, const dom_qos_policy *defaults) {
    if (!state || !defaults) {
        return DOM_QOS_ERR;
    }
    std::memset(state, 0, sizeof(*state));
    state->struct_size = sizeof(*state);
    state->struct_version = DOM_QOS_STRUCT_VERSION;
    state->base_policy = *defaults;
    state->effective_policy = *defaults;
    state->last_reason_mask = 0u;
    state->last_revision = 0u;
    return DOM_QOS_OK;
}

int dom_qos_apply_server_policy(dom_qos_state *state, const dom_qos_policy *policy) {
    if (!state || !policy) {
        return DOM_QOS_ERR;
    }
    state->base_policy = *policy;
    dom_qos_recompute(state);
    return DOM_QOS_OK;
}

int dom_qos_apply_client_caps(dom_qos_state *state, const dom_qos_caps *caps) {
    if (!state || !caps) {
        return DOM_QOS_ERR;
    }
    state->caps = *caps;
    dom_qos_recompute(state);
    return DOM_QOS_OK;
}

int dom_qos_apply_client_status(dom_qos_state *state, const dom_qos_status *status) {
    if (!state || !status) {
        return DOM_QOS_ERR;
    }
    state->status = *status;
    dom_qos_recompute(state);
    return DOM_QOS_OK;
}

int dom_qos_get_effective_params(const dom_qos_state *state, dom_qos_policy *out_policy) {
    if (!state || !out_policy) {
        return DOM_QOS_ERR;
    }
    *out_policy = state->effective_policy;
    return DOM_QOS_OK;
}

int dom_qos_build_client_hello(const dom_qos_caps *caps,
                               std::vector<unsigned char> &out_bytes) {
    dom::core_tlv::TlvWriter w;
    if (!caps) {
        return DOM_QOS_ERR;
    }
    w.add_u32(DOM_QOS_TLV_SCHEMA_VERSION, DOM_QOS_SCHEMA_VERSION);
    w.add_u32(DOM_QOS_TLV_KIND, (u32)DOM_QOS_KIND_CLIENT_HELLO);
    w.add_u64(DOM_QOS_TLV_CAPS_PERF_DIGEST64, caps->perf_caps_digest64);
    w.add_u32(DOM_QOS_TLV_CAPS_PREFERRED_PROFILE, caps->preferred_profile);
    w.add_u32(DOM_QOS_TLV_CAPS_MAX_SNAPSHOT_HZ, caps->max_snapshot_hz);
    w.add_u32(DOM_QOS_TLV_CAPS_MAX_DELTA_DETAIL, caps->max_delta_detail);
    w.add_u32(DOM_QOS_TLV_CAPS_MAX_INTEREST_RADIUS_M, caps->max_interest_radius_m);
    w.add_u32(DOM_QOS_TLV_CAPS_DIAGNOSTIC_RATE_CAP, caps->diagnostic_rate_cap);
    w.add_u32(DOM_QOS_TLV_CAPS_ASSIST_FLAGS, caps->assist_flags);
    out_bytes = w.bytes();
    return DOM_QOS_OK;
}

int dom_qos_build_server_policy(const dom_qos_policy *policy,
                                std::vector<unsigned char> &out_bytes) {
    dom::core_tlv::TlvWriter w;
    if (!policy) {
        return DOM_QOS_ERR;
    }
    w.add_u32(DOM_QOS_TLV_SCHEMA_VERSION, DOM_QOS_SCHEMA_VERSION);
    w.add_u32(DOM_QOS_TLV_KIND, (u32)DOM_QOS_KIND_SERVER_POLICY);
    w.add_u32(DOM_QOS_TLV_POLICY_SNAPSHOT_HZ, policy->snapshot_hz);
    w.add_u32(DOM_QOS_TLV_POLICY_DELTA_DETAIL, policy->delta_detail);
    w.add_u32(DOM_QOS_TLV_POLICY_INTEREST_RADIUS_M, policy->interest_radius_m);
    w.add_u32(DOM_QOS_TLV_POLICY_RECOMMENDED_PROFILE, policy->recommended_profile);
    w.add_u32(DOM_QOS_TLV_POLICY_SERVER_LOAD_HINT, policy->server_load_hint);
    w.add_u32(DOM_QOS_TLV_POLICY_ASSIST_FLAGS, policy->assist_flags);
    out_bytes = w.bytes();
    return DOM_QOS_OK;
}

int dom_qos_build_client_status(const dom_qos_status *status,
                                std::vector<unsigned char> &out_bytes) {
    dom::core_tlv::TlvWriter w;
    if (!status) {
        return DOM_QOS_ERR;
    }
    w.add_u32(DOM_QOS_TLV_SCHEMA_VERSION, DOM_QOS_SCHEMA_VERSION);
    w.add_u32(DOM_QOS_TLV_KIND, (u32)DOM_QOS_KIND_CLIENT_STATUS);
    w.add_u32(DOM_QOS_TLV_STATUS_RENDER_FPS_AVG, status->render_fps_avg);
    w.add_u32(DOM_QOS_TLV_STATUS_FRAME_TIME_MS_AVG, status->frame_time_ms_avg);
    w.add_u32(DOM_QOS_TLV_STATUS_BACKLOG_JOBS, status->backlog_jobs);
    w.add_u32(DOM_QOS_TLV_STATUS_DERIVED_QUEUE_PRESSURE, status->derived_queue_pressure);
    w.add_u32(DOM_QOS_TLV_STATUS_REQUEST_DETAIL_REDUCTION, status->request_detail_reduction);
    out_bytes = w.bytes();
    return DOM_QOS_OK;
}

int dom_qos_parse_message(const unsigned char *data,
                          size_t len,
                          dom_qos_message *out_msg) {
    dom::core_tlv::TlvReader r(data, len);
    dom::core_tlv::TlvRecord rec;
    u32 schema_version = 0u;
    u32 kind = 0u;
    bool have_version = false;
    bool have_kind = false;

    if (!data || len == 0u || !out_msg) {
        return DOM_QOS_ERR;
    }

    std::memset(out_msg, 0, sizeof(*out_msg));

    while (r.next(rec)) {
        if (rec.tag == DOM_QOS_TLV_SCHEMA_VERSION) {
            if (dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, schema_version)) {
                have_version = true;
            }
        } else if (rec.tag == DOM_QOS_TLV_KIND) {
            if (dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, kind)) {
                have_kind = true;
            }
        } else if (rec.tag == DOM_QOS_TLV_CAPS_PERF_DIGEST64) {
            (void)dom::core_tlv::tlv_read_u64_le(rec.payload, rec.len, out_msg->caps.perf_caps_digest64);
        } else if (rec.tag == DOM_QOS_TLV_CAPS_PREFERRED_PROFILE) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.preferred_profile);
        } else if (rec.tag == DOM_QOS_TLV_CAPS_MAX_SNAPSHOT_HZ) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.max_snapshot_hz);
        } else if (rec.tag == DOM_QOS_TLV_CAPS_MAX_DELTA_DETAIL) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.max_delta_detail);
        } else if (rec.tag == DOM_QOS_TLV_CAPS_MAX_INTEREST_RADIUS_M) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.max_interest_radius_m);
        } else if (rec.tag == DOM_QOS_TLV_CAPS_DIAGNOSTIC_RATE_CAP) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.diagnostic_rate_cap);
        } else if (rec.tag == DOM_QOS_TLV_CAPS_ASSIST_FLAGS) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.assist_flags);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_SNAPSHOT_HZ) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.snapshot_hz);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_DELTA_DETAIL) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.delta_detail);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_INTEREST_RADIUS_M) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.interest_radius_m);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_RECOMMENDED_PROFILE) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.recommended_profile);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_SERVER_LOAD_HINT) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.server_load_hint);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_ASSIST_FLAGS) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.assist_flags);
        } else if (rec.tag == DOM_QOS_TLV_STATUS_RENDER_FPS_AVG) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->status.render_fps_avg);
        } else if (rec.tag == DOM_QOS_TLV_STATUS_FRAME_TIME_MS_AVG) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->status.frame_time_ms_avg);
        } else if (rec.tag == DOM_QOS_TLV_STATUS_BACKLOG_JOBS) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->status.backlog_jobs);
        } else if (rec.tag == DOM_QOS_TLV_STATUS_DERIVED_QUEUE_PRESSURE) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->status.derived_queue_pressure);
        } else if (rec.tag == DOM_QOS_TLV_STATUS_REQUEST_DETAIL_REDUCTION) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->status.request_detail_reduction);
        }
    }

    if (!have_version || schema_version != DOM_QOS_SCHEMA_VERSION) {
        return DOM_QOS_ERR_FORMAT;
    }
    if (!have_kind) {
        return DOM_QOS_ERR_KIND;
    }
    if (kind != DOM_QOS_KIND_CLIENT_HELLO &&
        kind != DOM_QOS_KIND_SERVER_POLICY &&
        kind != DOM_QOS_KIND_CLIENT_STATUS) {
        return DOM_QOS_ERR_KIND;
    }
    out_msg->kind = kind;
    return DOM_QOS_OK;
}
