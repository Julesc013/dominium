/*
FILE: include/dominium/paths.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / paths
RESPONSIBILITY: Defines the public contract for `paths` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_PATHS_H
#define DOMINIUM_PATHS_H

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Home dmn get dominium.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const char* dmn_get_dominium_home(void);
/* Purpose: Root dmn get install.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const char* dmn_get_install_root(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_PATHS_H */
