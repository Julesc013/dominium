/*
FILE: include/domino/profile.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / profile
RESPONSIBILITY: Defines the public contract for `profile` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_PROFILE_H_INCLUDED
#define DOMINO_PROFILE_H_INCLUDED
/*
 * Launcher-driven feature profile (C ABI, POD-only).
 *
 * This struct is produced by the product layer (C++98) and consumed by the
 * engine/runtime selection layer (C90). It must remain ABI-stable and avoid
 * dynamic allocation.
 */

#include "domino/abi.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_PROFILE_ABI_VERSION 1u

#define DOM_PROFILE_SUBSYSTEM_KEY_MAX 32u
#define DOM_PROFILE_BACKEND_NAME_MAX  32u

#define DOM_PROFILE_MAX_OVERRIDES 16u
#define DOM_PROFILE_MAX_FEATURES  16u

typedef enum dom_profile_kind_e {
    DOM_PROFILE_COMPAT = 0,
    DOM_PROFILE_BASELINE = 1,
    DOM_PROFILE_PERF = 2
} dom_profile_kind;

typedef struct dom_profile_override_s {
    char subsystem_key[DOM_PROFILE_SUBSYSTEM_KEY_MAX];
    char backend_name[DOM_PROFILE_BACKEND_NAME_MAX];
} dom_profile_override;

typedef struct dom_profile_feature_s {
    char name[DOM_PROFILE_SUBSYSTEM_KEY_MAX];
    u32  enabled;
} dom_profile_feature;

typedef struct dom_profile {
    DOM_ABI_HEADER;

    dom_profile_kind kind;
    u32 lockstep_strict; /* 0/1 */

    /* Preferred graphics backend (string form, e.g. "soft", "dx11"). */
    char preferred_gfx_backend[DOM_PROFILE_BACKEND_NAME_MAX];

    /* Optional per-subsystem backend preference list, e.g. "sys.fs" -> "win32". */
    u32 override_count;
    dom_profile_override overrides[DOM_PROFILE_MAX_OVERRIDES];

    /* Optional feature flags (bounded list). */
    u32 feature_count;
    dom_profile_feature features[DOM_PROFILE_MAX_FEATURES];
} dom_profile;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_PROFILE_H_INCLUDED */
