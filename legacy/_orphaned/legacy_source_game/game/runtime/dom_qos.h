/*
FILE: source/dominium/game/runtime/dom_qos.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_qos
RESPONSIBILITY: Defines QoS negotiation structs and helpers (non-sim).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: QoS is non-authoritative; logic must be deterministic for identical inputs.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_QOS_H
#define DOM_GAME_QOS_H

#include <stddef.h>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

enum {
    DOM_QOS_STRUCT_VERSION = 2u
};

enum {
    DOM_QOS_OK = 0,
    DOM_QOS_ERR = -1,
    DOM_QOS_ERR_FORMAT = -2,
    DOM_QOS_ERR_KIND = -3
};

enum DomQosKind {
    DOM_QOS_KIND_NONE = 0,
    DOM_QOS_KIND_CLIENT_HELLO = 1,
    DOM_QOS_KIND_SERVER_POLICY = 2,
    DOM_QOS_KIND_CLIENT_STATUS = 3
};

enum DomQosReduction {
    DOM_QOS_REDUCTION_NONE = 0,
    DOM_QOS_REDUCTION_MILD = 1,
    DOM_QOS_REDUCTION_MODERATE = 2,
    DOM_QOS_REDUCTION_SEVERE = 3
};

enum {
    DOM_QOS_REASON_NONE = 0u,
    DOM_QOS_REASON_CAPS_CLAMP = 1u << 0,
    DOM_QOS_REASON_STATUS_BACKLOG = 1u << 1,
    DOM_QOS_REASON_STATUS_REDUCTION = 1u << 2,
    DOM_QOS_REASON_STATUS_PRESSURE = 1u << 3,
    DOM_QOS_REASON_STATUS_FPS = 1u << 4,
    DOM_QOS_REASON_SERVER_LOAD = 1u << 5,
    DOM_QOS_REASON_ASSIST_CLAMP = 1u << 6
};

enum {
    DOM_QOS_SCHEMA_VERSION = 2u
};

enum {
    DOM_QOS_TLV_SCHEMA_VERSION = 1u,
    DOM_QOS_TLV_KIND = 2u,

    DOM_QOS_TLV_CAPS_PERF_DIGEST64 = 10u,
    DOM_QOS_TLV_CAPS_PREFERRED_PROFILE = 11u,
    DOM_QOS_TLV_CAPS_MAX_SNAPSHOT_HZ = 12u,
    DOM_QOS_TLV_CAPS_MAX_DELTA_DETAIL = 13u,
    DOM_QOS_TLV_CAPS_MAX_INTEREST_RADIUS_M = 14u,
    DOM_QOS_TLV_CAPS_DIAGNOSTIC_RATE_CAP = 15u,
    DOM_QOS_TLV_CAPS_ASSIST_FLAGS = 16u,

    DOM_QOS_TLV_POLICY_SNAPSHOT_HZ = 20u,
    DOM_QOS_TLV_POLICY_DELTA_DETAIL = 21u,
    DOM_QOS_TLV_POLICY_INTEREST_RADIUS_M = 22u,
    DOM_QOS_TLV_POLICY_RECOMMENDED_PROFILE = 23u,
    DOM_QOS_TLV_POLICY_SERVER_LOAD_HINT = 24u,
    DOM_QOS_TLV_POLICY_ASSIST_FLAGS = 25u,

    DOM_QOS_TLV_STATUS_RENDER_FPS_AVG = 30u,
    DOM_QOS_TLV_STATUS_FRAME_TIME_MS_AVG = 31u,
    DOM_QOS_TLV_STATUS_BACKLOG_JOBS = 32u,
    DOM_QOS_TLV_STATUS_DERIVED_QUEUE_PRESSURE = 33u,
    DOM_QOS_TLV_STATUS_REQUEST_DETAIL_REDUCTION = 34u
};

enum DomQosAssistFlags {
    DOM_QOS_ASSIST_NONE = 0u,
    DOM_QOS_ASSIST_LOCAL_MESH = 1u << 0,
    DOM_QOS_ASSIST_LOCAL_CACHE = 1u << 1
};

enum DomQosServerLoadHint {
    DOM_QOS_SERVER_LOAD_NOMINAL = 0u,
    DOM_QOS_SERVER_LOAD_BUSY = 1u,
    DOM_QOS_SERVER_LOAD_OVERLOADED = 2u
};

typedef struct dom_qos_caps {
    u64 perf_caps_digest64;
    u32 preferred_profile;
    u32 max_snapshot_hz;
    u32 max_delta_detail;
    u32 max_interest_radius_m;
    u32 diagnostic_rate_cap;
    u32 assist_flags;
} dom_qos_caps;

typedef struct dom_qos_policy {
    u32 snapshot_hz;
    u32 delta_detail;
    u32 interest_radius_m;
    u32 recommended_profile;
    u32 server_load_hint;
    u32 assist_flags;
} dom_qos_policy;

typedef struct dom_qos_status {
    u32 render_fps_avg;
    u32 frame_time_ms_avg;
    u32 backlog_jobs;
    u32 derived_queue_pressure;
    u32 request_detail_reduction;
} dom_qos_status;

typedef struct dom_qos_state {
    u32 struct_size;
    u32 struct_version;
    dom_qos_caps caps;
    dom_qos_policy base_policy;
    dom_qos_policy effective_policy;
    dom_qos_status status;
    u32 last_reason_mask;
    u32 last_revision;
} dom_qos_state;

typedef struct dom_qos_message {
    u32 kind;
    dom_qos_caps caps;
    dom_qos_policy policy;
    dom_qos_status status;
} dom_qos_message;

int dom_qos_init(dom_qos_state *state, const dom_qos_policy *defaults);
int dom_qos_apply_server_policy(dom_qos_state *state, const dom_qos_policy *policy);
int dom_qos_apply_client_caps(dom_qos_state *state, const dom_qos_caps *caps);
int dom_qos_apply_client_status(dom_qos_state *state, const dom_qos_status *status);
int dom_qos_get_effective_params(const dom_qos_state *state, dom_qos_policy *out_policy);

int dom_qos_build_client_hello(const dom_qos_caps *caps,
                               std::vector<unsigned char> &out_bytes);
int dom_qos_build_server_policy(const dom_qos_policy *policy,
                                std::vector<unsigned char> &out_bytes);
int dom_qos_build_client_status(const dom_qos_status *status,
                                std::vector<unsigned char> &out_bytes);
int dom_qos_parse_message(const unsigned char *data,
                          size_t len,
                          dom_qos_message *out_msg);

#endif /* DOM_GAME_QOS_H */
