/*
FILE: include/domino/launcher_config.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / launcher_config
RESPONSIBILITY: Defines the public contract for `launcher_config` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_LAUNCHER_CONFIG_H_INCLUDED
#define DOMINO_LAUNCHER_CONFIG_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Launcher configuration persisted as `launcher.cfg` (POD).
 *
 * Fields:
 *   - pref_path: NUL-terminated directory path that owns `launcher.cfg`.
 *   - theme: Theme identifier (NUL-terminated).
 *   - width: Window width in pixels.
 *   - height: Window height in pixels.
 *   - soft_only: Non-zero forces the software renderer.
 */
typedef struct launcher_config {
    char pref_path[260];
    char theme[64];
    int  width;
    int  height;
    int  soft_only;
} launcher_config;

/* Purpose: Load `launcher.cfg` and populate `cfg`.
 *
 * Parameters:
 *   - cfg: In/out configuration; must be non-NULL. Defaults are applied before parsing.
 *
 * Returns:
 *   - 0 on success; -1 on failure (missing or unreadable config).
 *
 * Side effects:
 *   - Reads `launcher.cfg` from disk.
 */
int launcher_config_load(launcher_config* cfg);

/* Purpose: Persist `cfg` to `launcher.cfg`.
 *
 * Parameters:
 *   - cfg: Input configuration; must be non-NULL.
 *
 * Returns:
 *   - 0 on success; -1 on failure.
 *
 * Side effects:
 *   - Writes `launcher.cfg` to disk.
 */
int launcher_config_save(const launcher_config* cfg);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_CONFIG_H_INCLUDED */
