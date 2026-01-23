/*
FILE: game/include/dominium/ups_runtime.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / ups_runtime
RESPONSIBILITY: Game-level UPS registration helpers (manifest parsing + registry add).
ALLOWED DEPENDENCIES: engine/include public headers and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Pass-through; deterministic if engine UPS inputs are deterministic.
*/
#ifndef DOMINIUM_UPS_RUNTIME_H
#define DOMINIUM_UPS_RUNTIME_H

#include "domino/ups.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Parse a manifest string and register the pack in the UPS registry. */
int dmn_ups_register_manifest_text(dom_ups_registry* reg,
                                   const char* text,
                                   u32 precedence,
                                   u64 manifest_hash,
                                   dom_ups_manifest_error* out_error);

/* Purpose: Parse a manifest file and register the pack in the UPS registry. */
int dmn_ups_register_manifest_file(dom_ups_registry* reg,
                                   const char* path,
                                   u32 precedence,
                                   u64 manifest_hash,
                                   dom_ups_manifest_error* out_error);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_UPS_RUNTIME_H */
