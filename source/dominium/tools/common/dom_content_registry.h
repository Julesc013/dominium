/*
FILE: source/dominium/tools/common/dom_content_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_content_registry
RESPONSIBILITY: Implements `dom_content_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_CONTENT_REGISTRY_H
#define DOM_CONTENT_REGISTRY_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/d_tlv.h"
}

namespace dom {
namespace tools {

class DomContentRegistry {
public:
    DomContentRegistry();
    ~DomContentRegistry();

    void reset();

    bool load_as_pack(const d_tlv_blob &content_or_pack_manifest, std::string &err);
    bool load_as_mod(const d_tlv_blob &content_or_mod_manifest, std::string &err);

    bool validate_all(std::string &err);

private:
    DomContentRegistry(const DomContentRegistry &);
    DomContentRegistry &operator=(const DomContentRegistry &);
};

} // namespace tools
} // namespace dom

#endif /* DOM_CONTENT_REGISTRY_H */

