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

    bool load_for_instance(const Paths &paths, const InstanceInfo &inst);

private:
    /* Storage to keep TLV payloads alive for the lifetime of the set. */
    std::vector< std::vector<unsigned char> > m_pack_storage;
    std::vector< std::vector<unsigned char> > m_mod_storage;
};

} // namespace dom

#endif
