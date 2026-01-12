/*
FILE: source/dominium/game/ui/dom_ui_projection.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/ui
RESPONSIBILITY: Projection modules that render widgets into HUD/diegetic/world surfaces without accessing world state.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS-specific headers; authoritative sim mutation; direct world state queries.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; projection must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal API; projections are deterministic and replay-safe.
EXTENSION POINTS: Extend via `docs/SPEC_UI_PROJECTIONS.md`.
*/
#ifndef DOM_UI_PROJECTION_H
#define DOM_UI_PROJECTION_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/gfx.h"
}

#include "ui/dom_ui_widgets.h"

namespace dom {

enum DomUiProjectionMode {
    DOM_UI_MODE_DIEGETIC_ONLY = 0,
    DOM_UI_MODE_HUD_ONLY,
    DOM_UI_MODE_HYBRID,
    DOM_UI_MODE_DEBUG
};

struct DomUiDeviceAnchor {
    u64 provenance_id;
    DomUiWidgetProjection projection;
    DomUiWidgetAnchor anchor;
    int x;
    int y;
    int width;
    int height;
    int available;
    std::string device_tag;
};

struct DomUiDeviceAnchorSet {
    std::vector<DomUiDeviceAnchor> anchors;
};

struct DomUiProjectionConfig {
    std::string hud_profile_id;
    std::string diegetic_profile_id;
    std::string world_profile_id;
    std::string debug_profile_id;
};

struct DomUiProjectionParams {
    d_gfx_cmd_buffer *buf;
    int width;
    int height;
    DomUiProjectionMode mode;
    const DomUiDeviceAnchorSet *anchors;
    const DomUiProjectionConfig *config;
    int allow_debug;
};

void dom_ui_projection_render(const DomUiWidgetRegistry &defs,
                              const DomUiLayoutSet &layouts,
                              const dom_capability_snapshot *snapshot,
                              const DomUiProjectionParams &params);

} // namespace dom

#endif /* DOM_UI_PROJECTION_H */
