/*
FILE: source/dominium/game/ui/dom_ui_widgets.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/ui
RESPONSIBILITY: Data-driven HUD widget definitions, layout profiles, and capability-driven rendering.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS-specific headers; authoritative sim mutation.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; deterministic parsing and ordering.
VERSIONING / ABI / DATA FORMAT NOTES: TOML-like config, forward-compatible keys.
EXTENSION POINTS: Extend via `docs/SPEC_UI_WIDGETS.md`.
*/
#ifndef DOM_UI_WIDGETS_H
#define DOM_UI_WIDGETS_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/gfx.h"
}

#include "runtime/dom_capability_engine.h"

namespace dom {

enum DomUiWidgetProjection {
    DOM_UI_PROJECTION_DIEGETIC = 0,
    DOM_UI_PROJECTION_HUD_OVERLAY,
    DOM_UI_PROJECTION_WORLD_SURFACE,
    DOM_UI_PROJECTION_DEBUG
};

enum DomUiWidgetAnchor {
    DOM_UI_ANCHOR_TOP_LEFT = 0,
    DOM_UI_ANCHOR_TOP_RIGHT,
    DOM_UI_ANCHOR_BOTTOM_LEFT,
    DOM_UI_ANCHOR_BOTTOM_RIGHT,
    DOM_UI_ANCHOR_CENTER
};

struct DomUiWidgetDefinition {
    std::string id;
    std::string label;
    std::vector<dom_capability_id> required_caps;
    u32 min_resolution;
    int allow_uncertainty;
    int width_px;
    int height_px;
    int draw_panel;
};

struct DomUiWidgetInstance {
    std::string widget_id;
    DomUiWidgetProjection projection;
    DomUiWidgetAnchor anchor;
    int x;
    int y;
    i32 scale_q16;
    i32 opacity_q16;
    int enabled;
    std::string input_binding;
};

struct DomUiLayoutProfile {
    std::string id;
    DomUiWidgetProjection projection;
    std::vector<DomUiWidgetInstance> instances;
};

struct DomUiWidgetRegistry {
    std::vector<DomUiWidgetDefinition> definitions;
};

struct DomUiLayoutSet {
    std::vector<DomUiLayoutProfile> profiles;
};

struct DomUiWidgetRenderParams {
    d_gfx_cmd_buffer *buf;
    int width;
    int height;
    DomUiWidgetProjection projection;
};

bool dom_ui_widgets_load_definitions(const std::string &path,
                                     DomUiWidgetRegistry &out,
                                     std::string &err);
bool dom_ui_widgets_load_layouts(const std::string &path,
                                 DomUiLayoutSet &out,
                                 std::string &err);
bool dom_ui_widgets_save_layouts(const std::string &path,
                                 const DomUiLayoutSet &layouts,
                                 std::string &err);

void dom_ui_widgets_default(DomUiWidgetRegistry &defs, DomUiLayoutSet &layouts);

const DomUiWidgetDefinition *dom_ui_widgets_find_definition(
    const DomUiWidgetRegistry &defs,
    const std::string &id);
const DomUiLayoutProfile *dom_ui_widgets_find_profile(
    const DomUiLayoutSet &layouts,
    const std::string &id);

void dom_ui_widgets_render(const DomUiWidgetRegistry &defs,
                           const DomUiLayoutProfile &profile,
                           const dom_capability_snapshot *snapshot,
                           const DomUiWidgetRenderParams &params);

} // namespace dom

#endif /* DOM_UI_WIDGETS_H */
