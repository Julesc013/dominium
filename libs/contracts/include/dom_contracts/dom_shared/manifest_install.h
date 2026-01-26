/*
FILE: include/dominium/_internal/dom_priv/dom_shared/manifest_install.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_shared/manifest_install
RESPONSIBILITY: Defines the public contract for `manifest_install` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SHARED_MANIFEST_INSTALL_H
#define DOM_SHARED_MANIFEST_INSTALL_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_shared_install_info {
    char install_id[64];
    char install_type[32];
    char platform[16];
    char version[32];
    char root_path[260];
    char created_at[32];
    char created_by[32];
} dom_shared_install_info;

/* Purpose: Exists manifest install.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
int dom_shared_manifest_install_exists(const char* root_path);

// Attempts to parse INSTALL_ROOT/dominium_install.json
// On failure, returns false and leaves out_info unchanged.
int dom_shared_parse_install_manifest(const char* root_path, dom_shared_install_info* out_info);

// Writes INSTALL_ROOT/dominium_install.json with info fields.
// Returns false on IO/serialization error.
int dom_shared_write_install_manifest(const dom_shared_install_info* info);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
