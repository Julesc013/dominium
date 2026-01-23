/*
FILE: game/core/ups_runtime.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / ups_runtime
RESPONSIBILITY: Implements game-level UPS registration helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic if manifest inputs are deterministic.
*/
#include "dominium/ups_runtime.h"

int dmn_ups_register_manifest_text(dom_ups_registry* reg,
                                   const char* text,
                                   u32 precedence,
                                   u64 manifest_hash,
                                   dom_ups_manifest_error* out_error)
{
    dom_ups_manifest manifest;
    if (!reg || !text) {
        return -1;
    }
    if (dom_ups_manifest_parse_text(text, &manifest, out_error) != 0) {
        return -2;
    }
    return dom_ups_registry_add_pack(reg, &manifest, precedence, manifest_hash, out_error);
}

int dmn_ups_register_manifest_file(dom_ups_registry* reg,
                                   const char* path,
                                   u32 precedence,
                                   u64 manifest_hash,
                                   dom_ups_manifest_error* out_error)
{
    dom_ups_manifest manifest;
    if (!reg || !path) {
        return -1;
    }
    if (dom_ups_manifest_parse_file(path, &manifest, out_error) != 0) {
        return -2;
    }
    return dom_ups_registry_add_pack(reg, &manifest, precedence, manifest_hash, out_error);
}
