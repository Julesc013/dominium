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
    return a.update_hz == b.update_hz &&
           a.delta_detail == b.delta_detail &&
           a.interest_radius_m == b.interest_radius_m &&
           a.recommended_profile == b.recommended_profile;
}

static void dom_qos_apply_reduction(dom_qos_policy &policy, u32 level) {
    if (level == DOM_QOS_REDUCTION_MILD) {
        if (policy.update_hz > 0u) {
            policy.update_hz = dom_qos_max_u32(1u, dom_qos_scale_u32(policy.update_hz, 3u, 4u));
        }
        policy.delta_detail = dom_qos_scale_u32(policy.delta_detail, 3u, 4u);
        policy.interest_radius_m = dom_qos_scale_u32(policy.interest_radius_m, 4u, 5u);
    } else if (level == DOM_QOS_REDUCTION_MODERATE) {
        if (policy.update_hz > 0u) {
            policy.update_hz = dom_qos_max_u32(1u, dom_qos_scale_u32(policy.update_hz, 1u, 2u));
        }
        policy.delta_detail = dom_qos_scale_u32(policy.delta_detail, 1u, 2u);
        policy.interest_radius_m = dom_qos_scale_u32(policy.interest_radius_m, 3u, 5u);
    } else if (level == DOM_QOS_REDUCTION_SEVERE) {
        if (policy.update_hz > 0u) {
            policy.update_hz = dom_qos_max_u32(1u, dom_qos_scale_u32(policy.update_hz, 1u, 4u));
        }
        policy.delta_detail = dom_qos_scale_u32(policy.delta_detail, 3u, 10u);
        policy.interest_radius_m = dom_qos_scale_u32(policy.interest_radius_m, 2u, 5u);
    }
}

static void dom_qos_recompute(dom_qos_state *state) {
    dom_qos_policy effective;
    u32 reason = 0u;
    u32 reduction = 0u;

    if (!state) {
        return;
    }

    effective = state->base_policy;

    if (state->caps.max_update_hz > 0u &&
        effective.update_hz > state->caps.max_update_hz) {
        effective.update_hz = state->caps.max_update_hz;
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

    reduction = state->status.desired_reduction;
    if (state->status.backlog_ms >= 250u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_SEVERE);
        reason |= DOM_QOS_REASON_STATUS_BACKLOG;
    } else if (state->status.backlog_ms >= 120u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MODERATE);
        reason |= DOM_QOS_REASON_STATUS_BACKLOG;
    } else if (state->status.backlog_ms >= 60u) {
        reduction = dom_qos_max_u32(reduction, (u32)DOM_QOS_REDUCTION_MILD);
        reason |= DOM_QOS_REASON_STATUS_BACKLOG;
    }
    if (state->status.desired_reduction != 0u) {
        reason |= DOM_QOS_REASON_STATUS_REDUCTION;
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
    w.add_u32(DOM_QOS_TLV_CAPS_PERF_CLASS, caps->perf_class);
    w.add_u32(DOM_QOS_TLV_CAPS_MAX_UPDATE_HZ, caps->max_update_hz);
    w.add_u32(DOM_QOS_TLV_CAPS_MAX_DELTA_DETAIL, caps->max_delta_detail);
    w.add_u32(DOM_QOS_TLV_CAPS_MAX_INTEREST_RADIUS_M, caps->max_interest_radius_m);
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
    w.add_u32(DOM_QOS_TLV_POLICY_UPDATE_HZ, policy->update_hz);
    w.add_u32(DOM_QOS_TLV_POLICY_DELTA_DETAIL, policy->delta_detail);
    w.add_u32(DOM_QOS_TLV_POLICY_INTEREST_RADIUS_M, policy->interest_radius_m);
    w.add_u32(DOM_QOS_TLV_POLICY_RECOMMENDED_PROFILE, policy->recommended_profile);
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
    w.add_u32(DOM_QOS_TLV_STATUS_FPS_BUDGET, status->fps_budget);
    w.add_u32(DOM_QOS_TLV_STATUS_BACKLOG_MS, status->backlog_ms);
    w.add_u32(DOM_QOS_TLV_STATUS_DESIRED_REDUCTION, status->desired_reduction);
    w.add_u32(DOM_QOS_TLV_STATUS_FLAGS, status->status_flags);
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
        } else if (rec.tag == DOM_QOS_TLV_CAPS_PERF_CLASS) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.perf_class);
        } else if (rec.tag == DOM_QOS_TLV_CAPS_MAX_UPDATE_HZ) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.max_update_hz);
        } else if (rec.tag == DOM_QOS_TLV_CAPS_MAX_DELTA_DETAIL) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.max_delta_detail);
        } else if (rec.tag == DOM_QOS_TLV_CAPS_MAX_INTEREST_RADIUS_M) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->caps.max_interest_radius_m);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_UPDATE_HZ) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.update_hz);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_DELTA_DETAIL) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.delta_detail);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_INTEREST_RADIUS_M) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.interest_radius_m);
        } else if (rec.tag == DOM_QOS_TLV_POLICY_RECOMMENDED_PROFILE) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->policy.recommended_profile);
        } else if (rec.tag == DOM_QOS_TLV_STATUS_FPS_BUDGET) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->status.fps_budget);
        } else if (rec.tag == DOM_QOS_TLV_STATUS_BACKLOG_MS) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->status.backlog_ms);
        } else if (rec.tag == DOM_QOS_TLV_STATUS_DESIRED_REDUCTION) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->status.desired_reduction);
        } else if (rec.tag == DOM_QOS_TLV_STATUS_FLAGS) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_msg->status.status_flags);
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
