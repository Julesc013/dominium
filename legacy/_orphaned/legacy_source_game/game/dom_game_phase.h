/*
FILE: source/dominium/game/dom_game_phase.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_phase
RESPONSIBILITY: Defines phase/state machine for the play flow (authoritative in game app).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_PHASE_H
#define DOM_GAME_PHASE_H

#include <string>

extern "C" {
#include "domino/core/types.h"
}

#include "ui/d_ui.h"

namespace dom {

enum DomGamePhaseId {
    DOM_GAME_PHASE_BOOT = 0,
    DOM_GAME_PHASE_SPLASH,
    DOM_GAME_PHASE_MAIN_MENU,
    DOM_GAME_PHASE_SESSION_START,
    DOM_GAME_PHASE_SESSION_LOADING,
    DOM_GAME_PHASE_IN_SESSION,
    DOM_GAME_PHASE_SHUTDOWN
};

enum DomGamePhaseAction {
    DOM_GAME_PHASE_ACTION_NONE = 0,
    DOM_GAME_PHASE_ACTION_START_HOST,
    DOM_GAME_PHASE_ACTION_START_JOIN,
    DOM_GAME_PHASE_ACTION_NEW_UNIVERSE,
    DOM_GAME_PHASE_ACTION_LOAD_UNIVERSE,
    DOM_GAME_PHASE_ACTION_IMPORT_UNIVERSE,
    DOM_GAME_PHASE_ACTION_EXPORT_UNIVERSE,
    DOM_GAME_PHASE_ACTION_QUIT_TO_MENU,
    DOM_GAME_PHASE_ACTION_QUIT_APP
};

struct DomGamePhaseInput {
    u32 dt_ms;
    DomGamePhaseAction action;
    bool runtime_ready;
    bool content_ready;
    bool net_ready;
    bool world_ready;
    u32 world_progress;
    bool session_start_ok;
    bool session_start_failed;
    const char *session_error;
};

struct DomGamePhaseCtx {
    DomGamePhaseId phase;
    DomGamePhaseId prev_phase;
    DomGamePhaseAction session_action;
    u32 phase_time_ms;
    u32 splash_min_ms;
    bool phase_changed;
    bool auto_start_host;
    bool auto_start_join;
    bool auto_started;
    bool runtime_ready;
    bool content_ready;
    bool net_ready;
    bool world_ready;
    u32 world_progress;
    bool has_error;
    std::string last_error;
    std::string loading_status;
    std::string loading_progress;
    std::string loading_detail_content;
    std::string loading_detail_net;
    std::string loading_detail_world;
    std::string player_name;
    std::string server_addr;
    u32 server_port;

    DomGamePhaseCtx();
};

void dom_game_phase_init(DomGamePhaseCtx &ctx);
bool dom_game_phase_update(DomGamePhaseCtx &ctx, const DomGamePhaseInput &in);
void dom_game_phase_render(DomGamePhaseCtx &ctx, dui_context &ui, u32 dt_ms);
const char *dom_game_phase_name(DomGamePhaseId phase);

} // namespace dom

#endif /* DOM_GAME_PHASE_H */
