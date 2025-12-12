#ifndef DOM_LAUNCHER_ACTIONS_H
#define DOM_LAUNCHER_ACTIONS_H

#include "dom_launcher_app.h"

namespace dom {

bool launcher_action_list_instances(const std::vector<InstanceInfo> &instances);
bool launcher_action_list_products(const std::vector<ProductEntry> &products);
bool launcher_action_launch(DomLauncherApp &app,
                            const LauncherConfig &cfg);

} // namespace dom

#endif
