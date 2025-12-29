/*
FILE: source/dominium/game/runtime/dom_game_content_id.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_content_id
RESPONSIBILITY: Defines helpers for building content identity TLVs; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-sensitive (content identity hashing).
VERSIONING / ABI / DATA FORMAT NOTES: TLV tags defined in `source/dominium/game/SPEC_SAVE.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_CONTENT_ID_H
#define DOM_GAME_CONTENT_ID_H

#include <vector>

#ifdef __cplusplus
extern "C" {
#endif
#include "domino/core/types.h"
#ifdef __cplusplus
} /* extern "C" */
#endif

namespace dom {

class DomSession;

bool dom_game_content_build_tlv(const DomSession *session,
                                std::vector<unsigned char> &out);
bool dom_game_content_match_tlv(const DomSession *session,
                                const unsigned char *tlv,
                                u32 len);

} // namespace dom

#endif /* DOM_GAME_CONTENT_ID_H */
