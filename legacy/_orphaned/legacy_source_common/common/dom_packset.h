/*
FILE: source/dominium/common/dom_packset.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_packset
RESPONSIBILITY: Defines internal contract for `dom_packset`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_PACKSET_H
#define DOM_PACKSET_H

#include <string>
#include <vector>
#include "dom_paths.h"
#include "dom_instance.h"

extern "C" {
#include "content/d_content.h"
}

namespace dom {

struct PackSet {
    /* Ordered list of pack TLVs to load */
    std::vector<d_tlv_blob> pack_blobs;

    /* Ordered list of mod TLVs to load */
    std::vector<d_tlv_blob> mod_blobs;

    /* True if the implicit base pack was loaded into pack_blobs[0]. */
    bool base_loaded;
    unsigned base_version;

    bool load_for_instance(const Paths &paths, const InstanceInfo &inst);

private:
    /* Storage to keep TLV payloads alive for the lifetime of the set. */
    std::vector< std::vector<unsigned char> > m_pack_storage;
    std::vector< std::vector<unsigned char> > m_mod_storage;
};

} // namespace dom

#endif
