#ifndef DOM_SETUP_PLUGINS_H
#define DOM_SETUP_PLUGINS_H

#include "dom_setup_plugin.h"
#include "dom_shared/manifest_install.h"
#include "dom_setup_config.h"

#include <vector>
#include <string>

void setup_plugins_load();
void setup_plugins_unload();
void setup_plugins_apply_profiles(SetupConfig &cfg);
void setup_plugins_post_install(const dom_shared::InstallInfo &info);
void setup_plugins_post_repair(const dom_shared::InstallInfo &info);
void setup_plugins_post_uninstall(const dom_shared::InstallInfo &info);

#endif /* DOM_SETUP_PLUGINS_H */
