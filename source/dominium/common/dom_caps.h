/*
FILE: source/dominium/common/dom_caps.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_caps
RESPONSIBILITY: SIM_CAPS/PERF_CAPS compatibility helpers + identity digest utilities.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS-specific headers; no exceptions.
*/
#ifndef DOM_CAPS_H
#define DOM_CAPS_H

#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "dominium/caps_split.h"

namespace dom {

bool dom_sim_caps_equal(const DomSimCaps &a, const DomSimCaps &b);
bool dom_sim_caps_compatible(const DomSimCaps &a, const DomSimCaps &b);
bool dom_perf_caps_equal(const DomPerfCaps &a, const DomPerfCaps &b);

/* Identity digest for launcher/game handshake compatibility. */
u64 dom_identity_digest64(const DomSimCaps &sim_caps,
                          const unsigned char *content_hash_bytes,
                          u32 content_hash_len,
                          u64 provider_bindings_hash64);

} // namespace dom

#endif /* DOM_CAPS_H */
