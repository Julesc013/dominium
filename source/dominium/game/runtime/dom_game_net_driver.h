/*
FILE: source/dominium/game/runtime/dom_game_net_driver.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_net_driver
RESPONSIBILITY: Defines net driver interface and authority-specific adapters.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Network drivers must not mutate authoritative state outside the runtime tick pipeline.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_NET_DRIVER_H
#define DOM_GAME_NET_DRIVER_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "runtime/dom_game_session.h"
#include "runtime/dom_game_paths.h"
#include "runtime/dom_game_command.h"

struct dom_game_runtime;

namespace dom {

class DomGameNet;
struct InstanceInfo;

enum {
    DOM_NET_DRIVER_OK = 0,
    DOM_NET_DRIVER_ERR = -1,
    DOM_NET_DRIVER_NO_DATA = 1,
    DOM_NET_DRIVER_NOT_IMPLEMENTED = 2
};

struct DomNetDriverContext {
    DomGameNet *net;
    dom_game_runtime *runtime;
    const InstanceInfo *instance;
    const DomGamePaths *paths;

    DomNetDriverContext();
};

class DomNetDriver {
public:
    virtual ~DomNetDriver();

    virtual int start() = 0;
    virtual void stop() = 0;
    virtual int pump_network() = 0;
    virtual bool ready() const = 0;

    virtual int submit_local_command(const dom_game_command *cmd, u32 *out_tick);

    /* Server-authoritative snapshot/delta plumbing (v0 stubs). */
    virtual int poll_snapshot(std::vector<unsigned char> &out_bytes);
    virtual int consume_snapshot(const unsigned char *data, size_t len);

    /* Lockstep hash exchange (v0). */
    virtual int submit_tick_hash(u64 tick, u64 hash);
    virtual int poll_peer_hash(u64 *out_tick, u64 *out_hash);

    DomSessionRole role() const { return m_role; }
    DomSessionAuthority authority() const { return m_authority; }

protected:
    DomNetDriver(const DomSessionConfig &cfg, const DomNetDriverContext &ctx);

    DomSessionRole m_role;
    DomSessionAuthority m_authority;
    DomSessionConfig m_cfg;
    DomNetDriverContext m_ctx;
};

DomNetDriver *dom_net_driver_create(const DomSessionConfig &cfg,
                                    const DomNetDriverContext &ctx,
                                    std::string *out_error);
void dom_net_driver_destroy(DomNetDriver *driver);

} // namespace dom

#endif /* DOM_GAME_NET_DRIVER_H */
