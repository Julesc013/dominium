/*
FILE: include/dominium/product_manifest.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / product_manifest
RESPONSIBILITY: Defines the public contract for `product_manifest` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_PRODUCT_MANIFEST_H
#define DOMINIUM_PRODUCT_MANIFEST_H

#include "domino/version.h"

/* Purpose: Parsed product metadata from a product manifest file (POD).
 *
 * Fields:
 * - `id`: Product identifier string (NUL-terminated; truncated to fit).
 * - `version`: Parsed semantic version (see `domino_semver_parse`).
 * - `content_api` / `launcher_content_api` / `launcher_ext_api`: Compatibility integers read from
 *   the `[compat]` section when present; default to 0 when absent.
 *
 * Format notes:
 * - Parsing is intentionally minimal and does not implement full TOML; see `dominium_product_load`.
 */
typedef struct dominium_product_desc {
    char          id[64];
    domino_semver version;
    int           content_api;
    int           launcher_content_api;
    int           launcher_ext_api;
} dominium_product_desc;

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Load a product manifest from disk into a `dominium_product_desc`.
 *
 * Parameters:
 * - `path`: Filesystem path to a manifest file (non-NULL).
 * - `out`: Output descriptor (non-NULL).
 *
 * Returns:
 * - 0 on success (file opened and a non-empty `id` was parsed).
 * - -1 on error (invalid arguments, file open failure, or missing `id`).
 *
 * Notes:
 * - The parser recognizes `id = "..."` and `version = "..."` at the top level and
 *   integer keys within a `[compat]` section; unknown lines are ignored.
 * - `*out` is assigned even on failure; callers should check the return value before use.
 */
int dominium_product_load(const char* path, dominium_product_desc* out);

#ifdef __cplusplus
}
#endif

#endif
