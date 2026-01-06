/*
FILE: source/dominium/game/runtime/dom_game_session.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_session
RESPONSIBILITY: Defines session roles/authority configuration for the game runtime.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Session config is not authoritative state; validation must be deterministic.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_SESSION_H
#define DOM_GAME_SESSION_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {

enum DomSessionRole {
    DOM_SESSION_ROLE_SINGLE = 0,
    DOM_SESSION_ROLE_HOST = 1,
    DOM_SESSION_ROLE_DEDICATED_SERVER = 2,
    DOM_SESSION_ROLE_CLIENT = 3
};

enum DomSessionAuthority {
    DOM_SESSION_AUTH_SERVER_AUTH = 0,
    DOM_SESSION_AUTH_LOCKSTEP = 1
};

enum {
    DOM_GAME_SESSION_CONFIG_VERSION = 1u
};

enum DomSessionRefusalCode {
    DOM_SESSION_REFUSAL_OK = 0u,
    DOM_SESSION_REFUSAL_INVALID_ROLE = 2001u,
    DOM_SESSION_REFUSAL_INVALID_AUTHORITY = 2002u,
    DOM_SESSION_REFUSAL_ROLE_AUTH_MISMATCH = 2003u,
    DOM_SESSION_REFUSAL_MISSING_CONNECT_ADDR = 2004u,
    DOM_SESSION_REFUSAL_INVALID_TICK_RATE = 2005u,
    DOM_SESSION_REFUSAL_INVALID_PORT = 2006u,
    DOM_SESSION_REFUSAL_INVALID_INPUT_DELAY = 2007u
};

struct DomSessionIdentity {
    std::string instance_id;
    u64 run_id;
    std::vector<unsigned char> instance_manifest_hash;

    DomSessionIdentity();
};

struct DomSessionConfig {
    u32 struct_size;
    u32 struct_version;
    DomSessionRole role;
    DomSessionAuthority authority;
    u32 tick_rate_hz;
    u32 input_delay_ticks;
    u32 net_port;
    std::string connect_addr;
    DomSessionIdentity identity;

    DomSessionConfig();
};

bool dom_session_config_validate(const DomSessionConfig &cfg,
                                 u32 *out_refusal_code,
                                 std::string *out_detail);

} // namespace dom

#endif /* DOM_GAME_SESSION_H */
