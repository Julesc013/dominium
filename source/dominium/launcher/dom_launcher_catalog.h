/*
FILE: source/dominium/launcher/dom_launcher_catalog.h
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
