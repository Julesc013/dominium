/*
FILE: source/dominium/game/ui/dom_ui_views.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/ui
RESPONSIBILITY: Snapshot-driven map/transit render helpers (derived-only).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS-specific headers; authoritative sim mutation.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal helpers; no stable ABI guarantee.
EXTENSION POINTS: Extend via `docs/SPEC_PLAYER_CONTINUITY.md`.
*/
#ifndef DOM_UI_VIEWS_H
#define DOM_UI_VIEWS_H

#include "domino/core/types.h"
#include "domino/gfx.h"
#include "runtime/dom_snapshot.h"
#include "runtime/dom_cosmo_graph.h"
#include "runtime/dom_surface_chunks.h"

namespace dom {

struct DomUiViewParams {
    d_gfx_cmd_buffer *buf;
    int width;
    int height;
    u32 fidelity;
    u8 alpha;
    int clear;
};

void dom_ui_render_planet_map(const DomUiViewParams *params,
                              const dom_surface_view_snapshot *surface,
                              const dom_body_list_snapshot *bodies);
void dom_ui_render_system_map(const DomUiViewParams *params,
                              const dom_body_list_snapshot *bodies);
void dom_ui_render_galaxy_map(const DomUiViewParams *params,
                              const dom_cosmo_map_snapshot *cosmo);
void dom_ui_render_cosmos_map(const DomUiViewParams *params,
                              const dom_cosmo_map_snapshot *cosmo);
void dom_ui_render_transit_view(const DomUiViewParams *params,
                                const dom_cosmo_transit_snapshot *transit,
                                const dom_runtime_summary_snapshot *runtime);

} // namespace dom

#endif /* DOM_UI_VIEWS_H */
