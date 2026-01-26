/*
FILE: include/dominium/_internal/dom_priv/dom_shared/json.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_shared/json
RESPONSIBILITY: Defines the public contract for `json` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SHARED_JSON_H
#define DOM_SHARED_JSON_H

#include <stddef.h>

extern "C" {
#include "domino/core/types.h"
}

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_shared_json_value {
    u32 struct_size;
    u32 struct_version;
    u32 kind;
} dom_shared_json_value;

int dom_shared_json_parse(const char* text, dom_shared_json_value* out_value);
int dom_shared_json_stringify(const dom_shared_json_value* value,
                              char* out,
                              size_t out_cap);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
