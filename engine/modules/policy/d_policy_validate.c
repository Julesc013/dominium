/*
FILE: source/domino/policy/d_policy_validate.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / policy/d_policy_validate
RESPONSIBILITY: Implements `d_policy_validate`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "policy/d_policy.h"

#include "core/d_tlv_kv.h"
#include "content/d_content.h"
#include "content/d_content_extra.h"

static int dpolicy_subject_kind_valid(u32 kind) {
    switch (kind) {
    case D_POLICY_SUBJECT_NONE:
    case D_POLICY_SUBJECT_PROCESS:
    case D_POLICY_SUBJECT_JOB_TEMPLATE:
    case D_POLICY_SUBJECT_STRUCTURE:
    case D_POLICY_SUBJECT_SPLINE_PROFILE:
        return 1;
    default:
        return 0;
    }
}

static int dpolicy_validate_rule(const d_proto_policy_rule *p) {
    u32 off;
    u32 tag;
    d_tlv_blob payload;
    int rc;

    int have_subject_kind = 0;
    u32 subject_kind = D_POLICY_SUBJECT_NONE;

    if (!p) {
        return -1;
    }

    /* Validate scope subject_kind if present. */
    off = 0u;
    while ((rc = d_tlv_kv_next(&p->scope, &off, &tag, &payload)) == 0) {
        if (tag == D_TLV_POLICY_SCOPE_SUBJECT_KIND) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&payload, &tmp) == 0) {
                have_subject_kind = 1;
                subject_kind = tmp;
            }
        }
    }
    if (rc < 0) {
        return -1;
    }
    if (have_subject_kind && !dpolicy_subject_kind_valid(subject_kind)) {
        return -1;
    }

    /* Validate referenced subject ids when subject_kind is known. */
    off = 0u;
    while ((rc = d_tlv_kv_next(&p->scope, &off, &tag, &payload)) == 0) {
        if (tag == D_TLV_POLICY_SCOPE_SUBJECT_ID) {
            u32 sid = 0u;
            if (d_tlv_kv_read_u32(&payload, &sid) != 0) {
                continue;
            }
            if (sid == 0u) {
                return -1;
            }
            if (have_subject_kind) {
                switch (subject_kind) {
                case D_POLICY_SUBJECT_PROCESS:
                    if (!d_content_get_process((d_process_id)sid)) return -1;
                    break;
                case D_POLICY_SUBJECT_JOB_TEMPLATE:
                    if (!d_content_get_job_template((d_job_template_id)sid)) return -1;
                    break;
                case D_POLICY_SUBJECT_STRUCTURE:
                    if (!d_content_get_structure((d_structure_proto_id)sid)) return -1;
                    break;
                case D_POLICY_SUBJECT_SPLINE_PROFILE:
                    if (!d_content_get_spline_profile((d_spline_profile_id)sid)) return -1;
                    break;
                default:
                    break;
                }
            }
        }
    }
    if (rc < 0) {
        return -1;
    }

    /* Validate research ids referenced by conditions. */
    off = 0u;
    while ((rc = d_tlv_kv_next(&p->conditions, &off, &tag, &payload)) == 0) {
        if (tag == D_TLV_POLICY_COND_RESEARCH_COMPLETED ||
            tag == D_TLV_POLICY_COND_RESEARCH_NOT_COMPLETED) {
            u32 rid = 0u;
            if (d_tlv_kv_read_u32(&payload, &rid) == 0) {
                if (rid == 0u || !d_content_get_research((d_research_id)rid)) {
                    return -1;
                }
            }
        }
    }
    if (rc < 0) {
        return -1;
    }

    /* Validate basic effect value ranges. */
    off = 0u;
    while ((rc = d_tlv_kv_next(&p->effect, &off, &tag, &payload)) == 0) {
        if (tag == D_TLV_POLICY_EFFECT_ALLOWED) {
            u32 v = 1u;
            if (d_tlv_kv_read_u32(&payload, &v) == 0) {
                if (v != 0u && v != 1u) {
                    return -1;
                }
            }
        } else if (tag == D_TLV_POLICY_EFFECT_MULTIPLIER ||
                   tag == D_TLV_POLICY_EFFECT_CAP) {
            q16_16 q = 0;
            if (d_tlv_kv_read_q16_16(&payload, &q) == 0) {
                if (q < 0) {
                    return -1;
                }
            }
        }
    }
    if (rc < 0) {
        return -1;
    }

    return 0;
}

int d_policy_validate(const struct d_world *w) {
    u32 count;
    u32 i;
    (void)w;

    count = d_content_policy_rule_count();
    for (i = 0u; i < count; ++i) {
        const d_proto_policy_rule *p = d_content_get_policy_rule_by_index(i);
        if (p && dpolicy_validate_rule(p) != 0) {
            fprintf(stderr, "policy validate: invalid rule %u\n", (unsigned)p->id);
            return -1;
        }
    }
    return 0;
}

