#ifndef DOM_LAUNCHER_PLUGINS_H
#define DOM_LAUNCHER_PLUGINS_H

#include "launcher_context.h"
#include "launcher_process.h"
#include "launcher_db.h"

void launcher_plugins_load(const LauncherContext &ctx);
void launcher_plugins_unload();
void launcher_plugins_register_builtin();
void launcher_plugins_list();

#endif /* DOM_LAUNCHER_PLUGINS_H */
