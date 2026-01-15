/*
FILE: include/domino/launcher_mods.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / launcher_mods
RESPONSIBILITY: Defines the public contract for `launcher_mods` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_LAUNCHER_MODS_H_INCLUDED
#define DOMINO_LAUNCHER_MODS_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

/* launcher_mod_meta: Public type used by `launcher_mods`. */
typedef struct launcher_mod_meta {
    char id[64];
    char name[96];
    char version[32];
    int  priority;
    int  enabled;
} launcher_mod_meta;

/* Purpose: Scan launcher mods.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_mods_scan(const char* path);
/* Purpose: Get mods.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_mods_get(int index, launcher_mod_meta* out);
/* Purpose: Count launcher mods.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_mods_count(void);
/* Purpose: Set enabled.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_mods_set_enabled(const char* id, int enabled);
/* Purpose: Resolve order.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int launcher_mods_resolve_order(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_MODS_H_INCLUDED */
