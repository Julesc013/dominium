/*
FILE: include/domino/launcher.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / launcher
RESPONSIBILITY: Defines the public contract for `launcher` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_LAUNCHER_H_INCLUDED
#define DOMINO_LAUNCHER_H_INCLUDED

#include "launcher/launcher_config.h"
#include "launcher/launcher_profile.h"
#include "launcher/launcher_mods.h"
#include "launcher/launcher_process.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Init launcher.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_init(const launcher_config* cfg);
/* Purpose: Run launcher.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_run(void);
/* Purpose: Shutdown launcher.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void launcher_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_H_INCLUDED */
