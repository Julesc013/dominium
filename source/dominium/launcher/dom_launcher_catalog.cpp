/*
FILE: source/dominium/launcher/dom_launcher_catalog.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/dom_launcher_catalog
RESPONSIBILITY: Implements `dom_launcher_catalog`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
