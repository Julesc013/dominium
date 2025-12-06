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

LauncherState& get_state();

// Initializes state from context and DB; should be called early in main.
void state_initialize();

// Persists DB to disk using ctx.user_data_root.
void state_save();

} // namespace dom_launcher

#endif
