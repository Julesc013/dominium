/*
FILE: source/dominium/game/ui/dom_ui_projection.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/ui
RESPONSIBILITY: Projection modules (HUD/diegetic/world/debug) built on widget render output.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS-specific headers; authoritative sim mutation; direct world state queries.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; projection must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal implementation; see `docs/SPEC_UI_PROJECTIONS.md`.
EXTENSION POINTS: Extend projection modes without changing capability semantics.
*/
#include "ui/dom_ui_projection.h"

#include <algorithm>
#include <cstdlib>

namespace dom {
namespace {

static std::vector<std::string> g_projection_text_scratch;

struct AnchorFilterState {
    const DomUiDeviceAnchor *anchor;
    int allow_untagged;
};

struct AnchorLess {
    bool operator()(const DomUiDeviceAnchor &a, const DomUiDeviceAnchor &b) const {
        if (a.projection != b.projection) {
            return a.projection < b.projection;
        }
        if (a.device_tag != b.device_tag) {
            return a.device_tag < b.device_tag;
        }
        if (a.provenance_id != b.provenance_id) {
            return a.provenance_id < b.provenance_id;
        }
        return a.x < b.x;
    }
};

static const DomUiLayoutProfile *find_profile_by_id_or_projection(
    const DomUiLayoutSet &layouts,
    const std::string &profile_id,
    DomUiWidgetProjection projection) {
    if (!profile_id.empty()) {
        const DomUiLayoutProfile *found = dom_ui_widgets_find_profile(layouts, profile_id);
        if (found) {
            return found;
        }
    }
    for (size_t i = 0u; i < layouts.profiles.size(); ++i) {
        if (layouts.profiles[i].projection == projection) {
            return &layouts.profiles[i];
        }
    }
    return 0;
}

static bool allow_anchor_widget(const DomUiWidgetInstance &inst,
                                const DomUiWidgetDefinition &,
                                const dom_capability *cap,
                                void *user) {
    const AnchorFilterState *state = (const AnchorFilterState *)user;
    if (!state || !state->anchor || !state->anchor->available) {
        return false;
    }
    if (!inst.device_tag.empty()) {
        if (state->anchor->device_tag.empty()) {
            return false;
        }
        if (inst.device_tag != state->anchor->device_tag) {
            return false;
        }
    } else if (!state->allow_untagged) {
        return false;
    }
    if (!cap) {
        return false;
    }
    if (state->anchor->provenance_id != 0u &&
        cap->source_provenance != 0u &&
        cap->source_provenance != state->anchor->provenance_id) {
        return false;
    }
    return true;
}

static void reset_cmd_buffer(d_gfx_cmd_buffer *buf) {
    if (buf) {
        buf->count = 0u;
    }
}

static void append_cmds_with_offset(d_gfx_cmd_buffer *dst,
                                    const d_gfx_cmd_buffer *src,
                                    int offset_x,
                                    int offset_y) {
    if (!dst || !src || !src->cmds) {
        return;
    }
    for (u32 i = 0u; i < src->count; ++i) {
        const d_gfx_cmd *cmd = src->cmds + i;
        switch (cmd->opcode) {
        case D_GFX_OP_DRAW_RECT: {
            d_gfx_draw_rect_cmd r = cmd->u.rect;
            r.x += offset_x;
            r.y += offset_y;
            d_gfx_cmd_draw_rect(dst, &r);
            break;
        }
        case D_GFX_OP_DRAW_TEXT: {
            d_gfx_draw_text_cmd t = cmd->u.text;
            t.x += offset_x;
            t.y += offset_y;
            d_gfx_cmd_draw_text(dst, &t);
            break;
        }
        case D_GFX_OP_SET_VIEWPORT: {
            d_gfx_set_viewport_cmd vp = cmd->u.viewport;
            d_gfx_cmd_set_viewport(dst, &vp.vp);
            break;
        }
        case D_GFX_OP_SET_CAMERA: {
            d_gfx_set_camera_cmd cam = cmd->u.camera;
            d_gfx_cmd_set_camera(dst, &cam.cam);
            break;
        }
        case D_GFX_OP_CLEAR:
        default:
            break;
        }
    }
}

static void render_profile_direct(const DomUiWidgetRegistry &defs,
                                  const DomUiLayoutProfile *profile,
                                  const dom_capability_snapshot *snapshot,
                                  const DomUiWidgetRenderParams &params,
                                  DomUiWidgetRenderContext *context) {
    if (!profile) {
        return;
    }
    dom_ui_widgets_render_ex(defs, *profile, snapshot, params, 0, context);
}

static void render_profile_anchored(const DomUiWidgetRegistry &defs,
                                    const DomUiLayoutProfile *profile,
                                    const dom_capability_snapshot *snapshot,
                                    const DomUiWidgetRenderParams &params,
                                    const DomUiDeviceAnchorSet *anchors,
                                    DomUiWidgetProjection projection,
                                    DomUiWidgetRenderContext *context) {
    std::vector<DomUiDeviceAnchor> sorted;
    d_gfx_cmd_buffer tmp;
    DomUiWidgetRenderParams local_params = params;

    if (!profile || !anchors || anchors->anchors.empty()) {
        return;
    }

    sorted = anchors->anchors;
    std::sort(sorted.begin(), sorted.end(), AnchorLess());

    tmp.cmds = 0;
    tmp.count = 0u;
    tmp.capacity = 0u;

    local_params.projection = projection;
    local_params.buf = &tmp;

    int untagged_used = 0;
    for (size_t i = 0u; i < sorted.size(); ++i) {
        AnchorFilterState state;
        DomUiWidgetRenderFilter filter;
        const DomUiDeviceAnchor &anchor = sorted[i];
        int local_w;
        int local_h;
        if (anchor.projection != projection || !anchor.available) {
            continue;
        }
        local_w = (anchor.width > 0) ? anchor.width : params.width;
        local_h = (anchor.height > 0) ? anchor.height : params.height;
        local_params.width = local_w;
        local_params.height = local_h;

        state.anchor = &anchor;
        state.allow_untagged = (untagged_used == 0) ? 1 : 0;
        filter.allow = allow_anchor_widget;
        filter.user = &state;

        reset_cmd_buffer(&tmp);
        dom_ui_widgets_render_ex(defs, *profile, snapshot, local_params, &filter, context);
        append_cmds_with_offset(params.buf, &tmp, anchor.x, anchor.y);

        if (state.allow_untagged) {
            untagged_used = 1;
        }
    }

    if (tmp.cmds) {
        std::free(tmp.cmds);
    }
}

} // namespace

void dom_ui_projection_render(const DomUiWidgetRegistry &defs,
                              const DomUiLayoutSet &layouts,
                              const dom_capability_snapshot *snapshot,
                              const DomUiProjectionParams &params) {
    const DomUiProjectionConfig empty_cfg;
    const DomUiProjectionConfig *cfg = params.config ? params.config : &empty_cfg;
    DomUiWidgetRenderParams render_params;
    DomUiWidgetRenderContext context;
    int want_hud = 0;
    int want_diegetic = 0;
    int want_world = 0;
    int want_debug = 0;

    if (!params.buf) {
        return;
    }

    g_projection_text_scratch.clear();

    render_params.buf = params.buf;
    render_params.width = params.width;
    render_params.height = params.height;

    context.text_scratch = &g_projection_text_scratch;
    context.clear_before = 0;

    switch (params.mode) {
    case DOM_UI_MODE_DIEGETIC_ONLY:
        want_diegetic = 1;
        want_world = 1;
        break;
    case DOM_UI_MODE_HYBRID:
        want_hud = 1;
        want_diegetic = 1;
        want_world = 1;
        if (params.allow_debug) {
            want_debug = 1;
        }
        break;
    case DOM_UI_MODE_DEBUG:
        want_hud = 1;
        want_diegetic = 1;
        want_world = 1;
        want_debug = params.allow_debug ? 1 : 0;
        break;
    case DOM_UI_MODE_HUD_ONLY:
    default:
        want_hud = 1;
        break;
    }

    if (want_hud) {
        render_params.projection = DOM_UI_PROJECTION_HUD_OVERLAY;
        render_profile_direct(defs,
                              find_profile_by_id_or_projection(layouts,
                                                               cfg->hud_profile_id,
                                                               DOM_UI_PROJECTION_HUD_OVERLAY),
                              snapshot,
                              render_params,
                              &context);
    }

    if (want_diegetic) {
        render_params.projection = DOM_UI_PROJECTION_DIEGETIC;
        render_profile_anchored(defs,
                                find_profile_by_id_or_projection(layouts,
                                                                 cfg->diegetic_profile_id,
                                                                 DOM_UI_PROJECTION_DIEGETIC),
                                snapshot,
                                render_params,
                                params.anchors,
                                DOM_UI_PROJECTION_DIEGETIC,
                                &context);
    }

    if (want_world) {
        render_params.projection = DOM_UI_PROJECTION_WORLD_SURFACE;
        render_profile_anchored(defs,
                                find_profile_by_id_or_projection(layouts,
                                                                 cfg->world_profile_id,
                                                                 DOM_UI_PROJECTION_WORLD_SURFACE),
                                snapshot,
                                render_params,
                                params.anchors,
                                DOM_UI_PROJECTION_WORLD_SURFACE,
                                &context);
    }

    if (want_debug) {
        render_params.projection = DOM_UI_PROJECTION_DEBUG;
        render_profile_direct(defs,
                              find_profile_by_id_or_projection(layouts,
                                                               cfg->debug_profile_id,
                                                               DOM_UI_PROJECTION_DEBUG),
                              snapshot,
                              render_params,
                              &context);
    }
}

} // namespace dom
