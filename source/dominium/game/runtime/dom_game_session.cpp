/*
FILE: source/dominium/game/runtime/dom_game_session.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_session
RESPONSIBILITY: Implements session role/authority validation helpers.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Session config is not authoritative state; validation must be deterministic.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_session.h"

#include <cstring>

namespace dom {

DomSessionIdentity::DomSessionIdentity()
    : instance_id(),
      run_id(0ull),
      instance_manifest_hash() {
}

DomSessionConfig::DomSessionConfig()
    : struct_size(sizeof(DomSessionConfig)),
      struct_version(DOM_GAME_SESSION_CONFIG_VERSION),
      role(DOM_SESSION_ROLE_SINGLE),
      authority(DOM_SESSION_AUTH_SERVER_AUTH),
      tick_rate_hz(60u),
      input_delay_ticks(1u),
      net_port(7777u),
      connect_addr(),
      identity() {
}

static bool set_refusal(u32 code,
                        const char *detail,
                        u32 *out_refusal_code,
                        std::string *out_detail) {
    if (out_refusal_code) {
        *out_refusal_code = code;
    }
    if (out_detail) {
        if (detail) {
            *out_detail = detail;
        } else {
            out_detail->clear();
        }
    }
    return false;
}

bool dom_session_config_validate(const DomSessionConfig &cfg,
                                 u32 *out_refusal_code,
                                 std::string *out_detail) {
    if (out_refusal_code) {
        *out_refusal_code = DOM_SESSION_REFUSAL_OK;
    }
    if (out_detail) {
        out_detail->clear();
    }

    if (cfg.struct_size != sizeof(DomSessionConfig) ||
        cfg.struct_version != DOM_GAME_SESSION_CONFIG_VERSION) {
        return set_refusal(DOM_SESSION_REFUSAL_INVALID_ROLE,
                           "invalid_session_config_version",
                           out_refusal_code,
                           out_detail);
    }

    if (cfg.tick_rate_hz == 0u) {
        return set_refusal(DOM_SESSION_REFUSAL_INVALID_TICK_RATE,
                           "invalid_tick_rate",
                           out_refusal_code,
                           out_detail);
    }

    if (cfg.net_port == 0u || cfg.net_port > 65535u) {
        return set_refusal(DOM_SESSION_REFUSAL_INVALID_PORT,
                           "invalid_port",
                           out_refusal_code,
                           out_detail);
    }

    if (cfg.authority == DOM_SESSION_AUTH_LOCKSTEP && cfg.input_delay_ticks == 0u) {
        return set_refusal(DOM_SESSION_REFUSAL_INVALID_INPUT_DELAY,
                           "invalid_input_delay",
                           out_refusal_code,
                           out_detail);
    }

    switch (cfg.role) {
    case DOM_SESSION_ROLE_SINGLE:
        if (cfg.authority != DOM_SESSION_AUTH_SERVER_AUTH) {
            return set_refusal(DOM_SESSION_REFUSAL_ROLE_AUTH_MISMATCH,
                               "single_requires_server_auth",
                               out_refusal_code,
                               out_detail);
        }
        if (!cfg.connect_addr.empty()) {
            return set_refusal(DOM_SESSION_REFUSAL_MISSING_CONNECT_ADDR,
                               "single_disallows_connect_addr",
                               out_refusal_code,
                               out_detail);
        }
        break;
    case DOM_SESSION_ROLE_HOST:
        break;
    case DOM_SESSION_ROLE_DEDICATED_SERVER:
        if (cfg.authority != DOM_SESSION_AUTH_SERVER_AUTH) {
            return set_refusal(DOM_SESSION_REFUSAL_ROLE_AUTH_MISMATCH,
                               "dedicated_requires_server_auth",
                               out_refusal_code,
                               out_detail);
        }
        if (!cfg.connect_addr.empty()) {
            return set_refusal(DOM_SESSION_REFUSAL_MISSING_CONNECT_ADDR,
                               "server_disallows_connect_addr",
                               out_refusal_code,
                               out_detail);
        }
        break;
    case DOM_SESSION_ROLE_CLIENT:
        if (cfg.connect_addr.empty()) {
            return set_refusal(DOM_SESSION_REFUSAL_MISSING_CONNECT_ADDR,
                               "missing_connect_addr",
                               out_refusal_code,
                               out_detail);
        }
        break;
    default:
        return set_refusal(DOM_SESSION_REFUSAL_INVALID_ROLE,
                           "invalid_role",
                           out_refusal_code,
                           out_detail);
    }

    return true;
}

} // namespace dom
