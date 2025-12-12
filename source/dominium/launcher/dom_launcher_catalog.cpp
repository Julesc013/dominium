#include "dom_launcher_catalog.h"

#include <cstdio>

namespace dom {

void launcher_print_instances(const std::vector<InstanceInfo> &instances) {
    size_t i;
    if (instances.empty()) {
        std::printf("No instances found.\n");
        return;
    }
    for (i = 0u; i < instances.size(); ++i) {
        const InstanceInfo &inst = instances[i];
        std::printf("Instance %s: suite=%u core=%u world_seed=%u\n",
                    inst.id.c_str(),
                    inst.suite_version,
                    inst.core_version,
                    inst.world_seed);
    }
}

void launcher_print_products(const std::vector<ProductEntry> &products) {
    size_t i;
    if (products.empty()) {
        std::printf("No products registered in repo.\n");
        return;
    }
    for (i = 0u; i < products.size(); ++i) {
        const ProductEntry &p = products[i];
        std::printf("Product %s v%s -> %s\n",
                    p.product.c_str(),
                    p.version.c_str(),
                    p.path.c_str());
    }
}

} // namespace dom
