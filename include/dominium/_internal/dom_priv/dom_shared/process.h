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

#include <string>
#include <vector>

namespace dom_shared {

struct ProcessOptions {
    std::string working_directory;
    bool        inherit_environment;

/* Purpose: API entry point for `process`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    ProcessOptions() : working_directory(), inherit_environment(true) {}
};

struct ProcessHandle {
    int  pid;           // platform-specific ID
    void* internal;     // opaque pointer to internal state

/* Purpose: API entry point for `process`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    ProcessHandle() : pid(-1), internal(0) {}
};

/* Purpose: Process spawn.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool spawn_process(const std::string& executable,
                   const std::vector<std::string>& args,
                   const ProcessOptions& options,
                   ProcessHandle& out_handle);

// Non-blocking check if process is still alive
bool process_is_running(const ProcessHandle& handle);

// Blocking wait
int  process_wait(const ProcessHandle& handle);

// Simple helpers to read buffered stdout/stderr later if implemented
// (You can stub them for now; they will be expanded later)
std::string process_read_stdout(const ProcessHandle& handle);
/* Purpose: Read stderr.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::string process_read_stderr(const ProcessHandle& handle);

} // namespace dom_shared

#endif
