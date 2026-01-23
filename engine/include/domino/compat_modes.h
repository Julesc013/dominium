/*
FILE: include/domino/compat_modes.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / compat_modes
RESPONSIBILITY: Defines compatibility modes and capability negotiation inputs.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Negotiation must be deterministic for the same inputs.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_COMPAT_MODES_H
#define DOMINO_COMPAT_MODES_H

#include "domino/core/types.h"
#include "domino/capability.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_compat_mode: Explicit compatibility modes. */
typedef enum dom_compat_mode {
    DOM_COMPAT_MODE_AUTHORITATIVE = 0,
    DOM_COMPAT_MODE_DEGRADED = 1,
    DOM_COMPAT_MODE_FROZEN = 2,
    DOM_COMPAT_MODE_TRANSFORM_ONLY = 3,
    DOM_COMPAT_MODE_INCOMPATIBLE = 4
} dom_compat_mode;

/* dom_compat_mode_mask: Allowed compatibility modes. */
typedef enum dom_compat_mode_mask {
    DOM_COMPAT_ALLOW_AUTHORITATIVE = (1u << 0u),
    DOM_COMPAT_ALLOW_DEGRADED = (1u << 1u),
    DOM_COMPAT_ALLOW_FROZEN = (1u << 2u),
    DOM_COMPAT_ALLOW_TRANSFORM_ONLY = (1u << 3u)
} dom_compat_mode_mask;

/* dom_compat_caps_requirements: Capability constraints for negotiation. */
typedef struct dom_compat_caps_requirements {
    dom_capability_set_view required;
    dom_capability_set_view optional;
} dom_compat_caps_requirements;

/* dom_compat_decision: Negotiation result (explicit, no silent coercion). */
typedef struct dom_compat_decision {
    dom_compat_mode mode;
    u32             missing_required;
    u32             missing_optional;
} dom_compat_decision;

/* Purpose: Determine compatibility mode based on capability overlap. */
dom_compat_decision dom_compat_negotiate_caps(
    const dom_compat_caps_requirements* runtime,
    const dom_compat_caps_requirements* content,
    u32 allow_modes
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_COMPAT_MODES_H */
