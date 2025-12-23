/*
FILE: include/dominium/version.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / version
RESPONSIBILITY: Defines the public contract for `version` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_VERSION_H
#define DOMINIUM_VERSION_H

#include "domino/version.h"

#define DOMINIUM_CORE_VERSION     "0.0.0"
#define DOMINIUM_GAME_VERSION     "0.0.0"
#define DOMINIUM_LAUNCHER_VERSION "0.0.0"
#define DOMINIUM_SETUP_VERSION    "0.0.0"
#define DOMINIUM_TOOLS_VERSION    "0.0.0"
#define DOMINIUM_SUITE_VERSION    DOMINIUM_GAME_VERSION

#define DOMINIUM_VERSION_MAJOR 0
#define DOMINIUM_VERSION_MINOR 0
#define DOMINIUM_VERSION_PATCH 0
#define DOMINIUM_VERSION_SEMVER DOMINIUM_SUITE_VERSION

/* Legacy compatibility macros */
#ifndef DOM_VERSION_SEMVER
#define DOM_VERSION_SEMVER DOMINIUM_VERSION_SEMVER
#endif
#define DOM_PRODUCT_LAUNCHER 1
#define DOM_PRODUCT_SETUP    2
#define DOM_PRODUCT_GAME     3

#define DOMINIUM_GAME_ID     "dominium.game"
#define DOMINIUM_LAUNCHER_ID "dominium.launcher"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Version dominium game get.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void dominium_game_get_version(domino_semver* out);
/* Purpose: Version dominium launcher get.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void dominium_launcher_get_version(domino_semver* out);

/* Purpose: String version.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const char* dominium_get_core_version_string(void);
/* Purpose: String version.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const char* dominium_get_game_version_string(void);
/* Purpose: String version.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const char* dominium_get_launcher_version_string(void);
/* Purpose: String version.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const char* dominium_get_setup_version_string(void);
/* Purpose: String version.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const char* dominium_get_tools_version_string(void);
/* Purpose: String version.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const char* dominium_get_suite_version_string(void);

/* Purpose: Api dominium game get content.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dominium_game_get_content_api(void);
/* Purpose: Api dominium launcher get content.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dominium_launcher_get_content_api(void);
/* Purpose: Api dominium launcher get ext.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dominium_launcher_get_ext_api(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_VERSION_H */
