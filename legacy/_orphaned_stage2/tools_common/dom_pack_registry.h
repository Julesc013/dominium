/*
FILE: source/dominium/tools/common/dom_pack_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_pack_registry
RESPONSIBILITY: Defines internal contract for `dom_pack_registry`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_PACK_REGISTRY_H
#define DOM_PACK_REGISTRY_H

#include <string>

namespace dom {
namespace tools {

class DomPackRegistry {
public:
    DomPackRegistry();
    ~DomPackRegistry();

    void clear();
    bool load_from_home(const std::string &home, std::string &err);

private:
    DomPackRegistry(const DomPackRegistry &);
    DomPackRegistry &operator=(const DomPackRegistry &);
};

} // namespace tools
} // namespace dom

#endif /* DOM_PACK_REGISTRY_H */

