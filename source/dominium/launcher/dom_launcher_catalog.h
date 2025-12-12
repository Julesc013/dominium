#ifndef DOM_LAUNCHER_CATALOG_H
#define DOM_LAUNCHER_CATALOG_H

#include <vector>
#include "dom_instance.h"
#include "dom_launcher_app.h"

namespace dom {

void launcher_print_instances(const std::vector<InstanceInfo> &instances);
void launcher_print_products(const std::vector<ProductEntry> &products);

} // namespace dom

#endif
