/*
FILE: include/dominium/launcher_ext_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / launcher_ext_api
RESPONSIBILITY: Defines the public contract for `launcher_ext_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_LAUNCHER_EXT_API_H
#define DOMINIUM_LAUNCHER_EXT_API_H

#include "domino/mod.h"

/* Purpose: Opaque launcher context owned by the launcher host.
 *
 * Lifetime/ownership:
 * - The host creates and owns the context; callers pass a borrowed pointer.
 */
struct dominium_launcher_context;

/* Purpose: Enumerate currently loaded launcher instances.
 *
 * Parameters:
 * - `ctx`: Launcher context (non-NULL).
 * - `out`: Optional output array of `domino_instance_desc` entries. May be NULL to query count only.
 * - `max_count`: Capacity of `out` in elements.
 * - `out_count`: Optional output receiving the total number of loaded instances.
 *
 * Returns:
 * - 0 on success.
 * - -1 if `ctx` is NULL.
 *
 * Notes:
 * - When `out` is non-NULL and `max_count > 0`, up to `min(max_count, total)` items are copied.
 * - `*out_count` (when provided) is set to the total instance count, not the number copied.
 */
int launcher_ext_list_instances(struct dominium_launcher_context* ctx,
                                domino_instance_desc* out,
                                unsigned int max_count,
                                unsigned int* out_count);

/* Purpose: Resolve and run an instance by id via the launcher host.
 *
 * Parameters:
 * - `ctx`: Launcher context (non-NULL).
 * - `instance_id`: Instance identifier string (non-NULL).
 *
 * Returns:
 * - Process exit code of the launched instance on success.
 * - -1 on error (invalid arguments, resolution failure, spawn failure, or instance not found).
 *
 * Side effects:
 * - May spawn a child process and block while waiting for it to exit.
 * - May emit launcher logs via the host system layer.
 */
int launcher_ext_run_instance(struct dominium_launcher_context* ctx,
                              const char* instance_id);

/* Purpose: Enumerate packages visible to the launcher host.
 *
 * Parameters:
 * - `ctx`: Launcher context (non-NULL).
 * - `out`: Output array of `domino_package_desc` entries (non-NULL).
 * - `max_count`: Capacity of `out` in elements.
 * - `out_count`: Optional output receiving the number of entries written.
 *
 * Returns:
 * - 0 on success (including when no registry is loaded).
 * - -1 if `ctx` or `out` is NULL.
 *
 * Notes:
 * - Current implementation does not filter for launcher-target packages; it forwards all
 *   visible package descriptors in registry iteration order.
 */
int launcher_ext_list_launcher_packages(struct dominium_launcher_context* ctx,
                                        domino_package_desc* out,
                                        unsigned int max_count,
                                        unsigned int* out_count);

#endif /* DOMINIUM_LAUNCHER_EXT_API_H */
