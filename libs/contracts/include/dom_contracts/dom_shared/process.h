/*
FILE: include/dominium/_internal/dom_priv/dom_shared/process.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_shared/process
RESPONSIBILITY: Defines the public contract for `process` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SHARED_PROCESS_H
#define DOM_SHARED_PROCESS_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_shared_process_options {
    const char* working_directory;
    int         inherit_environment;
} dom_shared_process_options;

typedef struct dom_shared_process_handle {
    int   pid;
    void* internal;
} dom_shared_process_handle;

/* Purpose: Process spawn.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
int dom_shared_spawn_process(const char* executable,
                             const char* const* args,
                             size_t arg_count,
                             const dom_shared_process_options* options,
                             dom_shared_process_handle* out_handle);

// Non-blocking check if process is still alive
int dom_shared_process_is_running(const dom_shared_process_handle* handle);

// Blocking wait
int dom_shared_process_wait(const dom_shared_process_handle* handle);

// Simple helpers to read buffered stdout/stderr later if implemented
// (You can stub them for now; they will be expanded later)
size_t dom_shared_process_read_stdout(const dom_shared_process_handle* handle,
                                      char* out,
                                      size_t out_cap);
/* Purpose: Read stderr.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
size_t dom_shared_process_read_stderr(const dom_shared_process_handle* handle,
                                      char* out,
                                      size_t out_cap);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
