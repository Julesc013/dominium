/*
FILE: source/dominium/game/ui/dom_ui_state.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/ui
RESPONSIBILITY: Implements UI view state machine for local/map/transit presentation.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS-specific headers; authoritative sim mutation.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal structs versioned for forward evolution.
EXTENSION POINTS: Extend via `docs/SPEC_PLAYER_CONTINUITY.md`.
*/
#include "ui/dom_ui_state.h"

namespace dom {

namespace {

static const u32 DOM_UI_TRANSITION_DEFAULT_MS = 400u;

static void dom_ui_state_init_fields(DomUiState *state) {
    if (!state) {
        return;
    }
    state->struct_size = (u32)sizeof(DomUiState);
    state->struct_version = DOM_UI_STATE_VERSION;
    state->view = DOM_UI_VIEW_LOCAL;
    state->previous_view = DOM_UI_VIEW_LOCAL;
    state->transition_from = DOM_UI_VIEW_LOCAL;
    state->transition_to = DOM_UI_VIEW_LOCAL;
    state->transition_ms = 0u;
    state->transition_total_ms = DOM_UI_TRANSITION_DEFAULT_MS;
    state->transition_active = 0;
    state->transit_forced = 0;
}

} // namespace

void dom_ui_state_init(DomUiState *state) {
    dom_ui_state_init_fields(state);
}

void dom_ui_state_reset(DomUiState *state) {
    dom_ui_state_init_fields(state);
}

void dom_ui_state_request_view(DomUiState *state, DomUiViewState view) {
    if (!state) {
        return;
    }
    if (view == DOM_UI_VIEW_TRANSIT) {
        return;
    }
    if (state->view == DOM_UI_VIEW_TRANSIT) {
        state->previous_view = view;
        return;
    }
    if (state->view == view) {
        return;
    }
    state->transition_from = state->view;
    state->transition_to = view;
    state->transition_ms = 0u;
    state->transition_active = 1;
    state->view = view;
}

void dom_ui_state_tick(DomUiState *state, u32 dt_ms, int transit_active) {
    if (!state) {
        return;
    }

    if (transit_active) {
        if (state->view != DOM_UI_VIEW_TRANSIT) {
            state->previous_view = state->view;
            state->view = DOM_UI_VIEW_TRANSIT;
            state->transition_active = 0;
            state->transition_ms = 0u;
            state->transit_forced = 1;
        }
        return;
    }

    if (state->view == DOM_UI_VIEW_TRANSIT) {
        state->view = state->previous_view;
        state->transition_active = 0;
        state->transition_ms = 0u;
        state->transit_forced = 0;
    }

    if (state->transition_active) {
        if (dt_ms > 0u) {
            u32 next = state->transition_ms + dt_ms;
            if (next < state->transition_ms) {
                next = state->transition_total_ms;
            }
            state->transition_ms = next;
        }
        if (state->transition_ms >= state->transition_total_ms) {
            state->transition_active = 0;
            state->transition_ms = state->transition_total_ms;
            state->transition_from = state->view;
            state->transition_to = state->view;
            state->previous_view = state->view;
        }
    } else {
        state->previous_view = state->view;
    }
}

int dom_ui_state_handle_input(DomUiState *state, const d_sys_event *ev) {
    if (!state || !ev) {
        return 0;
    }
    if (ev->type != D_SYS_EVENT_KEY_DOWN) {
        return 0;
    }
    switch (ev->u.key.key) {
    case D_SYS_KEY_0:
    case D_SYS_KEY_1:
        dom_ui_state_request_view(state, DOM_UI_VIEW_LOCAL);
        return 1;
    case D_SYS_KEY_2:
        dom_ui_state_request_view(state, DOM_UI_VIEW_PLANET_MAP);
        return 1;
    case D_SYS_KEY_3:
        dom_ui_state_request_view(state, DOM_UI_VIEW_SYSTEM_MAP);
        return 1;
    case D_SYS_KEY_4:
        dom_ui_state_request_view(state, DOM_UI_VIEW_GALAXY_MAP);
        return 1;
    case D_SYS_KEY_5:
        dom_ui_state_request_view(state, DOM_UI_VIEW_COSMOS_MAP);
        return 1;
    default:
        break;
    }
    return 0;
}

u8 dom_ui_state_transition_alpha(const DomUiState *state) {
    if (!state) {
        return 255u;
    }
    if (!state->transition_active || state->transition_total_ms == 0u) {
        return 255u;
    }
    if (state->transition_ms >= state->transition_total_ms) {
        return 255u;
    }
    return (u8)((state->transition_ms * 255u) / state->transition_total_ms);
}

const char *dom_ui_state_view_name(DomUiViewState view) {
    switch (view) {
    case DOM_UI_VIEW_LOCAL:
        return "local";
    case DOM_UI_VIEW_PLANET_MAP:
        return "planet";
    case DOM_UI_VIEW_SYSTEM_MAP:
        return "system";
    case DOM_UI_VIEW_GALAXY_MAP:
        return "galaxy";
    case DOM_UI_VIEW_COSMOS_MAP:
        return "cosmos";
    case DOM_UI_VIEW_TRANSIT:
        return "transit";
    default:
        break;
    }
    return "unknown";
}

} // namespace dom
