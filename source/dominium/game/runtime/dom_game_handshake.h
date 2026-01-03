/*
FILE: source/dominium/game/runtime/dom_game_handshake.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_handshake
RESPONSIBILITY: Defines game-side handshake parsing (launcher → game).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_HANDSHAKE_H
#define DOM_GAME_HANDSHAKE_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "runtime/dom_game_paths.h"

namespace dom {

enum { DOM_GAME_HANDSHAKE_TLV_VERSION = 1u };

enum DomGameHandshakeTlvTag {
    DOM_GAME_HANDSHAKE_TLV_TAG_RUN_ID = 2u,
    DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_ID = 3u,
    DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_MANIFEST_HASH = 4u,
    DOM_GAME_HANDSHAKE_TLV_TAG_RUN_ROOT_REF = 100u,
    DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_ROOT_REF = 101u
};

enum DomGameHandshakePathRefTag {
    DOM_GAME_HANDSHAKE_PATH_REF_TAG_BASE = 1u,
    DOM_GAME_HANDSHAKE_PATH_REF_TAG_REL = 2u
};

enum DomGameHandshakePathRefBase {
    DOM_GAME_HANDSHAKE_PATH_REF_BASE_RUN_ROOT = 1u,
    DOM_GAME_HANDSHAKE_PATH_REF_BASE_HOME = 2u
};

struct DomGamePathRef {
    DomGamePathBaseKind base_kind;
    std::string rel;
    bool has_value;

    DomGamePathRef();
};

struct DomGameHandshake {
    u32 schema_version;
    u64 run_id;
    std::string instance_id;
    std::vector<unsigned char> instance_manifest_hash_bytes;
    DomGamePathRef run_root_ref;
    DomGamePathRef instance_root_ref;

    DomGameHandshake();
};

bool dom_game_handshake_from_tlv_bytes(const unsigned char *data,
                                       size_t size,
                                       DomGameHandshake &out_hs);
bool dom_game_handshake_from_file(const std::string &path,
                                  DomGameHandshake &out_hs);

} // namespace dom

#endif /* DOM_GAME_HANDSHAKE_H */
