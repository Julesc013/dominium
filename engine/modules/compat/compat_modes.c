/*
FILE: source/domino/compat/compat_modes.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / compat/compat_modes
RESPONSIBILITY: Implements capability-based compatibility negotiation.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Negotiation outcome is deterministic for the same inputs.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/compat_modes.h"

static d_bool dom_compat_runtime_has(const dom_compat_caps_requirements* runtime,
                                     dom_capability_id id)
{
    if (!runtime) {
        return D_FALSE;
    }
    if (dom_capability_set_contains(&runtime->required, id)) {
        return D_TRUE;
    }
    if (dom_capability_set_contains(&runtime->optional, id)) {
        return D_TRUE;
    }
    return D_FALSE;
}

static u32 dom_compat_count_missing(const dom_compat_caps_requirements* runtime,
                                    const dom_capability_set_view* required)
{
    u32 i;
    u32 missing = 0u;
    if (!required || required->count == 0u) {
        return 0u;
    }
    for (i = 0u; i < required->count; ++i) {
        if (!dom_compat_runtime_has(runtime, required->ids[i])) {
            missing += 1u;
        }
    }
    return missing;
}

dom_compat_decision dom_compat_negotiate_caps(
    const dom_compat_caps_requirements* runtime,
    const dom_compat_caps_requirements* content,
    u32 allow_modes
)
{
    dom_compat_decision decision;
    u32 missing_required;
    u32 missing_optional;

    decision.mode = DOM_COMPAT_MODE_INCOMPATIBLE;
    decision.missing_required = 0u;
    decision.missing_optional = 0u;

    if (!runtime || !content) {
        return decision;
    }

    missing_required = dom_compat_count_missing(runtime, &content->required);
    missing_optional = dom_compat_count_missing(runtime, &content->optional);

    decision.missing_required = missing_required;
    decision.missing_optional = missing_optional;

    if (missing_required == 0u) {
        if (missing_optional == 0u) {
            if (allow_modes & DOM_COMPAT_ALLOW_AUTHORITATIVE) {
                decision.mode = DOM_COMPAT_MODE_AUTHORITATIVE;
            } else if (allow_modes & DOM_COMPAT_ALLOW_DEGRADED) {
                decision.mode = DOM_COMPAT_MODE_DEGRADED;
            } else if (allow_modes & DOM_COMPAT_ALLOW_FROZEN) {
                decision.mode = DOM_COMPAT_MODE_FROZEN;
            } else if (allow_modes & DOM_COMPAT_ALLOW_TRANSFORM_ONLY) {
                decision.mode = DOM_COMPAT_MODE_TRANSFORM_ONLY;
            } else {
                decision.mode = DOM_COMPAT_MODE_INCOMPATIBLE;
            }
            return decision;
        }
        if (allow_modes & DOM_COMPAT_ALLOW_DEGRADED) {
            decision.mode = DOM_COMPAT_MODE_DEGRADED;
        } else if (allow_modes & DOM_COMPAT_ALLOW_AUTHORITATIVE) {
            decision.mode = DOM_COMPAT_MODE_AUTHORITATIVE;
        } else if (allow_modes & DOM_COMPAT_ALLOW_FROZEN) {
            decision.mode = DOM_COMPAT_MODE_FROZEN;
        } else if (allow_modes & DOM_COMPAT_ALLOW_TRANSFORM_ONLY) {
            decision.mode = DOM_COMPAT_MODE_TRANSFORM_ONLY;
        } else {
            decision.mode = DOM_COMPAT_MODE_INCOMPATIBLE;
        }
        return decision;
    }

    if (allow_modes & DOM_COMPAT_ALLOW_FROZEN) {
        decision.mode = DOM_COMPAT_MODE_FROZEN;
    } else if (allow_modes & DOM_COMPAT_ALLOW_TRANSFORM_ONLY) {
        decision.mode = DOM_COMPAT_MODE_TRANSFORM_ONLY;
    } else {
        decision.mode = DOM_COMPAT_MODE_INCOMPATIBLE;
    }
    return decision;
}
