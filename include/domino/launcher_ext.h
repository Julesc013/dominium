/*
FILE: include/domino/launcher_ext.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / launcher_ext
RESPONSIBILITY: Defines the public contract for `launcher_ext` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_LAUNCHER_EXT_H_INCLUDED
#define DOMINO_LAUNCHER_EXT_H_INCLUDED

#include "domino/baseline.h"
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct launcher_ext_vtable {
    uint32_t api_version;
    void (*register_views)(dom_core* core);
    void (*register_actions)(dom_core* core);
} launcher_ext_vtable;

typedef bool (*launcher_ext_get_vtable_fn)(launcher_ext_vtable* out);

bool launcher_ext_load_all(dom_core* core);
void launcher_ext_unload_all(dom_core* core);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_EXT_H_INCLUDED */
