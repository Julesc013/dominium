/*
FILE: include/dominium/_internal/dom_priv/dom_build_version.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_build_version
RESPONSIBILITY: Defines the public contract for `dom_build_version` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_BUILD_VERSION_H
#define DOM_BUILD_VERSION_H

/* Fallback build/version metadata for dom_core_version. */
#ifndef DOM_VERSION_SEMVER
#define DOM_VERSION_SEMVER "0.0.0"
#endif

#ifndef DOM_BUILD_NUMBER
#define DOM_BUILD_NUMBER 0
#endif

#ifndef DOM_STRINGIFY
#define DOM_STRINGIFY_HELPER(x) #x
#define DOM_STRINGIFY(x) DOM_STRINGIFY_HELPER(x)
#endif

#ifndef DOM_VERSION_BUILD_STR
#define DOM_VERSION_BUILD_STR DOM_VERSION_SEMVER " (build " DOM_STRINGIFY(DOM_BUILD_NUMBER) ")"
#endif

#endif /* DOM_BUILD_VERSION_H */
