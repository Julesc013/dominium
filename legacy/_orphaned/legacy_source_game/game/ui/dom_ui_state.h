/*
FILE: source/dominium/game/ui/dom_ui_state.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/ui
RESPONSIBILITY: Defines UI view state machine for local/map/transit presentation.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS-specific headers; authoritative sim mutation.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal structs versioned for forward evolution.
EXTENSION POINTS: Extend via `docs/SPEC_PLAYER_CONTINUITY.md`.
*/
#ifndef DOM_UI_STATE_H
#define DOM_UI_STATE_H

#include "domino/core/types.h"

extern "C" {
#include "domino/system/d_system_input.h"
}

namespace dom {

enum DomUiViewState {
    DOM_UI_VIEW_LOCAL = 0,
    DOM_UI_VIEW_PLANET_MAP,
    DOM_UI_VIEW_SYSTEM_MAP,
    DOM_UI_VIEW_GALAXY_MAP,
    DOM_UI_VIEW_COSMOS_MAP,
    DOM_UI_VIEW_TRANSIT
};

enum {
    DOM_UI_STATE_VERSION = 1u
};

struct DomUiState {
    u32 struct_size;
    u32 struct_version;
    DomUiViewState view;
    DomUiViewState previous_view;
    DomUiViewState transition_from;
    DomUiViewState transition_to;
    u32 transition_ms;
    u32 transition_total_ms;
    int transition_active;
    int transit_forced;
};

void dom_ui_state_init(DomUiState *state);
void dom_ui_state_reset(DomUiState *state);
void dom_ui_state_request_view(DomUiState *state, DomUiViewState view);
void dom_ui_state_tick(DomUiState *state, u32 dt_ms, int transit_active);
int dom_ui_state_handle_input(DomUiState *state, const d_sys_event *ev);
u8 dom_ui_state_transition_alpha(const DomUiState *state);
const char *dom_ui_state_view_name(DomUiViewState view);

} // namespace dom

#endif /* DOM_UI_STATE_H */
