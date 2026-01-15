/*
FILE: include/domino/launcher_process.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / launcher_process
RESPONSIBILITY: Defines the public contract for `launcher_process` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_LAUNCHER_PROCESS_H_INCLUDED
#define DOMINO_LAUNCHER_PROCESS_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

/* launcher_proc: Public type used by `launcher_process`. */
typedef struct launcher_proc {
    int             pid;
    int             running;
    int             exit_code;
    char            cmdline[260];
    char            cwd[260];
    dsys_process*   handle;
} launcher_proc;

/* Purpose: Spawn launcher process.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_process_spawn(launcher_proc* p, const char* exe, const char* args, const char* cwd);
/* Purpose: Poll launcher process.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_process_poll(launcher_proc* p);
/* Purpose: Kill launcher process.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_process_kill(launcher_proc* p);
/* Purpose: Read stdout.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_process_read_stdout(launcher_proc* p, char* buf, int maxlen);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_PROCESS_H_INCLUDED */
