/*
FILE: include/domino/launcher_profile.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / launcher_profile
RESPONSIBILITY: Defines the public contract for `launcher_profile` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_LAUNCHER_PROFILE_H_INCLUDED
#define DOMINO_LAUNCHER_PROFILE_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

/* launcher_profile: Public type used by `launcher_profile`. */
typedef struct launcher_profile {
    char id[64];
    char name[96];
    char install_path[260];
    char modset[128];
} launcher_profile;

/* Purpose: Load all.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int   launcher_profile_load_all(void);
/* Purpose: Get profile.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const launcher_profile* launcher_profile_get(int index);
/* Purpose: Count launcher profile.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int   launcher_profile_count(void);
/* Purpose: Save profile.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int   launcher_profile_save(const launcher_profile* p);
/* Purpose: Set active.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int   launcher_profile_set_active(int index);
/* Purpose: Get active.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int   launcher_profile_get_active(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_PROFILE_H_INCLUDED */
