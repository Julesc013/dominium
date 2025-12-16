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

/* dominium_product_desc: Public type used by `product_manifest`. */
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

/* Load from a TOML-like file on disk. Returns 0 on success. */
int dominium_product_load(const char* path, dominium_product_desc* out);

#ifdef __cplusplus
}
#endif

#endif
