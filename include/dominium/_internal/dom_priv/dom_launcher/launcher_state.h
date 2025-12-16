/*
FILE: include/dominium/_internal/dom_priv/dom_launcher/launcher_state.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_launcher/launcher_state
RESPONSIBILITY: Defines the public contract for `launcher_state` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_STATE_H
#define DOM_LAUNCHER_STATE_H

#include <vector>
#include <string>
#include "dom_launcher/launcher_context.h"
#include "dom_launcher/launcher_db.h"
#include "dom_shared/manifest_install.h"

namespace dom_launcher {

// Forward declarations for later prompts
struct NewsItem;
struct NewsState;

struct ChangeEntry;
struct ChangesState;

struct PackInfo;
struct ModViewModSet;
struct ModsState;

struct Instance;
struct InstancesState;

struct SettingsState;

struct LauncherState {
    LauncherContext          ctx;
    LauncherDB               db;
    std::vector<dom_shared::InstallInfo> installs; // discovered installs

    // Live/dynamic slices to be filled later
    NewsState*               news;     // allocate in init, or store by value later
    ChangesState*            changes;
    ModsState*               mods;
    InstancesState*          instances_state;
    SettingsState*           settings_state;
};

/* Purpose: State get.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
LauncherState& get_state();

// Initializes state from context and DB; should be called early in main.
void state_initialize();

// Persists DB to disk using ctx.user_data_root.
void state_save();

} // namespace dom_launcher

#endif
