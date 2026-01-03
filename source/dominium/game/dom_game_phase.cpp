/*
FILE: source/dominium/game/dom_game_phase.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_phase
RESPONSIBILITY: Implements phase/state machine for the play flow.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal implementation).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_game_phase.h"

#include <cstdio>

#include "dom_game_ui.h"

namespace dom {

namespace {

static void set_phase(DomGamePhaseCtx &ctx, DomGamePhaseId next) {
    if (ctx.phase == next) {
        return;
    }
    ctx.prev_phase = ctx.phase;
    ctx.phase = next;
    ctx.phase_time_ms = 0u;
    ctx.phase_changed = true;
}

static DomGamePhaseAction resolve_menu_action(DomGamePhaseCtx &ctx, DomGamePhaseAction action) {
    if (action != DOM_GAME_PHASE_ACTION_NONE) {
        return action;
    }
    if (ctx.auto_started) {
        return DOM_GAME_PHASE_ACTION_NONE;
    }
    if (ctx.auto_start_join) {
        ctx.auto_started = true;
        return DOM_GAME_PHASE_ACTION_START_JOIN;
    }
    if (ctx.auto_start_host) {
        ctx.auto_started = true;
        return DOM_GAME_PHASE_ACTION_START_HOST;
    }
    return DOM_GAME_PHASE_ACTION_NONE;
}

} // namespace

DomGamePhaseCtx::DomGamePhaseCtx()
    : phase(DOM_GAME_PHASE_BOOT),
      prev_phase(DOM_GAME_PHASE_BOOT),
      session_action(DOM_GAME_PHASE_ACTION_NONE),
      phase_time_ms(0u),
      splash_min_ms(1000u),
      phase_changed(false),
      auto_start_host(false),
      auto_start_join(false),
      auto_started(false),
      runtime_ready(false),
      content_ready(false),
      net_ready(false),
      world_ready(false),
      world_progress(0u),
      has_error(false),
      last_error(),
      loading_status(),
      loading_progress(),
      loading_detail_content(),
      loading_detail_net(),
      loading_detail_world(),
      player_name(),
      server_addr(),
      server_port(0u) {
}

void dom_game_phase_init(DomGamePhaseCtx &ctx) {
    ctx = DomGamePhaseCtx();
}

bool dom_game_phase_update(DomGamePhaseCtx &ctx, const DomGamePhaseInput &in) {
    ctx.phase_changed = false;
    ctx.phase_time_ms += in.dt_ms;
    ctx.runtime_ready = in.runtime_ready;
    ctx.content_ready = in.content_ready;
    ctx.net_ready = in.net_ready;
    ctx.world_ready = in.world_ready;
    ctx.world_progress = in.world_progress;

    if (in.session_start_failed && in.session_error) {
        ctx.has_error = true;
        ctx.last_error = in.session_error;
    }

    if (in.action == DOM_GAME_PHASE_ACTION_QUIT_APP) {
        set_phase(ctx, DOM_GAME_PHASE_SHUTDOWN);
        return ctx.phase_changed;
    }

    switch (ctx.phase) {
    case DOM_GAME_PHASE_BOOT:
        set_phase(ctx, DOM_GAME_PHASE_SPLASH);
        break;
    case DOM_GAME_PHASE_SPLASH:
        if (ctx.runtime_ready && ctx.content_ready &&
            ctx.phase_time_ms >= ctx.splash_min_ms) {
            set_phase(ctx, DOM_GAME_PHASE_MAIN_MENU);
        }
        break;
    case DOM_GAME_PHASE_MAIN_MENU: {
        DomGamePhaseAction action = resolve_menu_action(ctx, in.action);
        if (action == DOM_GAME_PHASE_ACTION_START_HOST ||
            action == DOM_GAME_PHASE_ACTION_START_JOIN) {
            ctx.has_error = false;
            ctx.last_error.clear();
            ctx.session_action = action;
            set_phase(ctx, DOM_GAME_PHASE_SESSION_START);
        } else if (action == DOM_GAME_PHASE_ACTION_QUIT_APP) {
            set_phase(ctx, DOM_GAME_PHASE_SHUTDOWN);
        }
        break;
    }
    case DOM_GAME_PHASE_SESSION_START:
        if (in.session_start_ok) {
            set_phase(ctx, DOM_GAME_PHASE_SESSION_LOADING);
        } else if (in.session_start_failed) {
            set_phase(ctx, DOM_GAME_PHASE_MAIN_MENU);
        }
        break;
    case DOM_GAME_PHASE_SESSION_LOADING:
        if (ctx.world_ready && ctx.net_ready) {
            set_phase(ctx, DOM_GAME_PHASE_IN_SESSION);
        }
        if (in.action == DOM_GAME_PHASE_ACTION_QUIT_TO_MENU) {
            set_phase(ctx, DOM_GAME_PHASE_MAIN_MENU);
        }
        break;
    case DOM_GAME_PHASE_IN_SESSION:
        if (in.action == DOM_GAME_PHASE_ACTION_QUIT_TO_MENU) {
            set_phase(ctx, DOM_GAME_PHASE_MAIN_MENU);
        }
        break;
    case DOM_GAME_PHASE_SHUTDOWN:
    default:
        break;
    }

    return ctx.phase_changed;
}

void dom_game_phase_render(DomGamePhaseCtx &ctx, dui_context &ui, u32 dt_ms) {
    char buf[128];
    const char spinner_chars[] = "|/-\\";
    const char spinner = spinner_chars[(ctx.phase_time_ms / 150u) % 4u];
    (void)dt_ms;
    if (ctx.phase == DOM_GAME_PHASE_SPLASH) {
        u32 progress = 0u;
        if (ctx.runtime_ready) {
            progress += 50u;
        }
        if (ctx.content_ready) {
            progress += 50u;
        }
        std::snprintf(buf, sizeof(buf), "Booting %c", spinner);
        ctx.loading_status = buf;
        std::snprintf(buf, sizeof(buf), "Progress: %u%%", progress);
        ctx.loading_progress = buf;
        dom_game_ui_set_loading_status(ui, ctx.loading_status.c_str());
        dom_game_ui_set_loading_progress(ui, ctx.loading_progress.c_str());
        return;
    }
    if (ctx.phase == DOM_GAME_PHASE_SESSION_START ||
        ctx.phase == DOM_GAME_PHASE_SESSION_LOADING) {
        u32 world_pct = ctx.world_ready ? 100u : ctx.world_progress;
        if (world_pct > 100u) {
            world_pct = 100u;
        }
        std::snprintf(buf, sizeof(buf), "Session loading %c", spinner);
        ctx.loading_status = buf;
        std::snprintf(buf, sizeof(buf), "Progress: %u%%", world_pct);
        ctx.loading_progress = buf;
        ctx.loading_detail_content = ctx.content_ready ? "Content: ready" : "Content: pending";
        ctx.loading_detail_net = ctx.net_ready ? "Network: ready" : "Network: pending";
        if (ctx.world_ready) {
            ctx.loading_detail_world = "World: ready";
        } else {
            std::snprintf(buf, sizeof(buf), "World: %u%%", world_pct);
            ctx.loading_detail_world = buf;
        }
        dom_game_ui_set_loading_status(ui, ctx.loading_status.c_str());
        dom_game_ui_set_loading_progress(ui, ctx.loading_progress.c_str());
        dom_game_ui_set_loading_detail_content(ui, ctx.loading_detail_content.c_str());
        dom_game_ui_set_loading_detail_net(ui, ctx.loading_detail_net.c_str());
        dom_game_ui_set_loading_detail_world(ui, ctx.loading_detail_world.c_str());
    }
}

const char *dom_game_phase_name(DomGamePhaseId phase) {
    switch (phase) {
    case DOM_GAME_PHASE_BOOT: return "BOOT";
    case DOM_GAME_PHASE_SPLASH: return "SPLASH";
    case DOM_GAME_PHASE_MAIN_MENU: return "MAIN_MENU";
    case DOM_GAME_PHASE_SESSION_START: return "SESSION_START";
    case DOM_GAME_PHASE_SESSION_LOADING: return "SESSION_LOADING";
    case DOM_GAME_PHASE_IN_SESSION: return "IN_SESSION";
    case DOM_GAME_PHASE_SHUTDOWN: return "SHUTDOWN";
    default:
        break;
    }
    return "UNKNOWN";
}

} // namespace dom
