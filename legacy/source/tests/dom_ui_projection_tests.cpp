/*
FILE: source/tests/dom_ui_projection_tests.cpp
MODULE: Dominium Tests
PURPOSE: Validate UI projection modes, device gating, and determinism-safe rendering.
*/
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/gfx.h"
}

#include "runtime/dom_io_guard.h"
#include "ui/dom_ui_projection.h"
#include "ui/dom_ui_widgets.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static dom_capability make_capability(dom_capability_id cap_id,
                                      u64 provenance,
                                      u32 resolution,
                                      i64 min_val,
                                      i64 max_val,
                                      u32 flags) {
    dom_capability cap;
    cap.capability_id = cap_id;
    cap.subject.kind = DOM_CAP_SUBJECT_ACTOR;
    cap.subject.id = 1u;
    cap.resolution_tier = resolution;
    cap.value_min = min_val;
    cap.value_max = max_val;
    cap.observed_tick = 10u;
    cap.delivery_tick = 10u;
    cap.expiry_tick = 0u;
    cap.latency_ticks = 0u;
    cap.staleness_ticks = 0u;
    cap.source_provenance = provenance;
    cap.flags = flags;
    return cap;
}

static void build_registry_and_layouts(dom::DomUiWidgetRegistry &defs,
                                       dom::DomUiLayoutSet &layouts) {
    dom::DomUiWidgetDefinition def;
    def.id = "time";
    def.label = "Time";
    def.required_caps.clear();
    def.required_caps.push_back(DOM_CAP_TIME_READOUT);
    def.min_resolution = DOM_RESOLUTION_BINARY;
    def.allow_uncertainty = 1;
    def.width_px = 220;
    def.height_px = 40;
    def.draw_panel = 1;
    defs.definitions.push_back(def);

    dom::DomUiLayoutProfile hud;
    dom::DomUiWidgetInstance inst;
    hud.id = "hud";
    hud.projection = dom::DOM_UI_PROJECTION_HUD_OVERLAY;
    inst.widget_id = "time";
    inst.projection = hud.projection;
    inst.anchor = dom::DOM_UI_ANCHOR_TOP_LEFT;
    inst.x = 16;
    inst.y = 16;
    inst.scale_q16 = (1 << 16);
    inst.opacity_q16 = (1 << 16);
    inst.enabled = 1;
    inst.input_binding.clear();
    inst.device_tag.clear();
    hud.instances.push_back(inst);
    layouts.profiles.push_back(hud);

    dom::DomUiLayoutProfile dieg;
    dieg.id = "diegetic";
    dieg.projection = dom::DOM_UI_PROJECTION_DIEGETIC;
    inst.projection = dieg.projection;
    inst.anchor = dom::DOM_UI_ANCHOR_TOP_LEFT;
    inst.x = 0;
    inst.y = 0;
    inst.device_tag = "clock";
    dieg.instances.push_back(inst);
    layouts.profiles.push_back(dieg);
}

static void collect_texts(const d_gfx_cmd_buffer *buf,
                          std::vector<std::string> &out) {
    out.clear();
    if (!buf) {
        return;
    }
    for (u32 i = 0u; i < buf->count; ++i) {
        const d_gfx_cmd *cmd = buf->cmds + i;
        if (cmd->opcode != D_GFX_OP_DRAW_TEXT || !cmd->u.text.text) {
            continue;
        }
        out.push_back(std::string(cmd->u.text.text));
    }
    std::sort(out.begin(), out.end());
}

static int find_text(const d_gfx_cmd_buffer *buf, const char *needle) {
    if (!buf || !needle) {
        return 0;
    }
    for (u32 i = 0u; i < buf->count; ++i) {
        const d_gfx_cmd *cmd = buf->cmds + i;
        if (cmd->opcode != D_GFX_OP_DRAW_TEXT) {
            continue;
        }
        if (cmd->u.text.text && std::strstr(cmd->u.text.text, needle)) {
            return 1;
        }
    }
    return 0;
}

static int test_projection_equivalence(void) {
    dom::DomUiWidgetRegistry defs;
    dom::DomUiLayoutSet layouts;
    dom::DomUiProjectionConfig config;
    dom::DomUiDeviceAnchorSet anchors;
    dom::DomUiProjectionParams params;
    d_gfx_cmd_buffer *buf = d_gfx_cmd_buffer_begin();
    dom_capability cap = make_capability(DOM_CAP_TIME_READOUT, 42u,
                                         DOM_RESOLUTION_EXACT, 123, 123, 0u);
    dom_capability_snapshot snap;
    std::vector<std::string> hud_texts;
    std::vector<std::string> dieg_texts;
    dom::DomUiDeviceAnchor anchor;

    if (!buf) {
        return fail("cmd buffer not available");
    }
    build_registry_and_layouts(defs, layouts);

    anchor.provenance_id = 42u;
    anchor.projection = dom::DOM_UI_PROJECTION_DIEGETIC;
    anchor.anchor = dom::DOM_UI_ANCHOR_TOP_LEFT;
    anchor.x = 120;
    anchor.y = 60;
    anchor.width = 220;
    anchor.height = 40;
    anchor.available = 1;
    anchor.device_tag = "clock";
    anchors.anchors.push_back(anchor);

    config.hud_profile_id = "hud";
    config.diegetic_profile_id = "diegetic";

    snap.tick = 100u;
    snap.capability_count = 1u;
    snap.capabilities = &cap;

    params.buf = buf;
    params.width = 640;
    params.height = 480;
    params.anchors = &anchors;
    params.config = &config;
    params.allow_debug = 0;

    buf->count = 0u;
    params.mode = dom::DOM_UI_MODE_HUD_ONLY;
    dom::dom_ui_projection_render(defs, layouts, &snap, params);
    collect_texts(buf, hud_texts);

    buf->count = 0u;
    params.mode = dom::DOM_UI_MODE_DIEGETIC_ONLY;
    dom::dom_ui_projection_render(defs, layouts, &snap, params);
    collect_texts(buf, dieg_texts);

    if (hud_texts != dieg_texts) {
        return fail("projection semantic equivalence failed");
    }
    return 0;
}

static int test_device_removal(void) {
    dom::DomUiWidgetRegistry defs;
    dom::DomUiLayoutSet layouts;
    dom::DomUiProjectionConfig config;
    dom::DomUiDeviceAnchorSet anchors;
    dom::DomUiProjectionParams params;
    d_gfx_cmd_buffer *buf = d_gfx_cmd_buffer_begin();
    dom_capability cap = make_capability(DOM_CAP_TIME_READOUT, 77u,
                                         DOM_RESOLUTION_EXACT, 1, 1, 0u);
    dom_capability_snapshot snap;
    dom::DomUiDeviceAnchor anchor;

    if (!buf) {
        return fail("cmd buffer not available");
    }
    build_registry_and_layouts(defs, layouts);

    anchor.provenance_id = 77u;
    anchor.projection = dom::DOM_UI_PROJECTION_DIEGETIC;
    anchor.anchor = dom::DOM_UI_ANCHOR_TOP_LEFT;
    anchor.x = 0;
    anchor.y = 0;
    anchor.width = 200;
    anchor.height = 40;
    anchor.available = 0;
    anchor.device_tag = "clock";
    anchors.anchors.push_back(anchor);

    config.diegetic_profile_id = "diegetic";

    snap.tick = 10u;
    snap.capability_count = 1u;
    snap.capabilities = &cap;

    params.buf = buf;
    params.width = 320;
    params.height = 200;
    params.mode = dom::DOM_UI_MODE_DIEGETIC_ONLY;
    params.anchors = &anchors;
    params.config = &config;
    params.allow_debug = 0;

    buf->count = 0u;
    dom::dom_ui_projection_render(defs, layouts, &snap, params);
    if (buf->count != 0u) {
        return fail("diegetic render should skip removed devices");
    }
    return 0;
}

static int test_hud_unknown(void) {
    dom::DomUiWidgetRegistry defs;
    dom::DomUiLayoutSet layouts;
    dom::DomUiProjectionConfig config;
    dom::DomUiProjectionParams params;
    d_gfx_cmd_buffer *buf = d_gfx_cmd_buffer_begin();
    dom_capability cap = make_capability(DOM_CAP_TIME_READOUT, 0u,
                                         DOM_RESOLUTION_BINARY, 0, 0,
                                         DOM_CAPABILITY_FLAG_UNKNOWN);
    dom_capability_snapshot snap;

    if (!buf) {
        return fail("cmd buffer not available");
    }
    build_registry_and_layouts(defs, layouts);

    config.hud_profile_id = "hud";
    snap.tick = 10u;
    snap.capability_count = 1u;
    snap.capabilities = &cap;

    params.buf = buf;
    params.width = 320;
    params.height = 200;
    params.mode = dom::DOM_UI_MODE_HUD_ONLY;
    params.anchors = 0;
    params.config = &config;
    params.allow_debug = 0;

    buf->count = 0u;
    dom::dom_ui_projection_render(defs, layouts, &snap, params);
    if (!find_text(buf, "UNKNOWN")) {
        return fail("unknown value not rendered in HUD");
    }
    return 0;
}

static int test_no_io_violation(void) {
    dom::DomUiWidgetRegistry defs;
    dom::DomUiLayoutSet layouts;
    dom::DomUiProjectionConfig config;
    dom::DomUiProjectionParams params;
    d_gfx_cmd_buffer *buf = d_gfx_cmd_buffer_begin();
    dom_capability cap = make_capability(DOM_CAP_TIME_READOUT, 0u,
                                         DOM_RESOLUTION_EXACT, 5, 5, 0u);
    dom_capability_snapshot snap;

    if (!buf) {
        return fail("cmd buffer not available");
    }
    build_registry_and_layouts(defs, layouts);

    config.hud_profile_id = "hud";
    snap.tick = 10u;
    snap.capability_count = 1u;
    snap.capabilities = &cap;

    params.buf = buf;
    params.width = 320;
    params.height = 200;
    params.mode = dom::DOM_UI_MODE_HUD_ONLY;
    params.anchors = 0;
    params.config = &config;
    params.allow_debug = 0;

    dom_io_guard_reset();
    dom_io_guard_enter_ui();
    buf->count = 0u;
    dom::dom_ui_projection_render(defs, layouts, &snap, params);
    dom_io_guard_exit_ui();
    if (dom_io_guard_violation_count() != 0u) {
        return fail("ui projection performed IO");
    }
    return 0;
}

static int test_snapshot_immutability(void) {
    dom::DomUiWidgetRegistry defs;
    dom::DomUiLayoutSet layouts;
    dom::DomUiProjectionConfig config;
    dom::DomUiDeviceAnchorSet anchors;
    dom::DomUiProjectionParams params;
    d_gfx_cmd_buffer *buf = d_gfx_cmd_buffer_begin();
    dom_capability cap = make_capability(DOM_CAP_TIME_READOUT, 99u,
                                         DOM_RESOLUTION_EXACT, 7, 7, 0u);
    dom_capability cap_copy;
    dom_capability_snapshot snap;
    dom::DomUiDeviceAnchor anchor;

    if (!buf) {
        return fail("cmd buffer not available");
    }
    build_registry_and_layouts(defs, layouts);

    anchor.provenance_id = 99u;
    anchor.projection = dom::DOM_UI_PROJECTION_DIEGETIC;
    anchor.anchor = dom::DOM_UI_ANCHOR_TOP_LEFT;
    anchor.x = 10;
    anchor.y = 10;
    anchor.width = 220;
    anchor.height = 40;
    anchor.available = 1;
    anchor.device_tag = "clock";
    anchors.anchors.push_back(anchor);

    config.hud_profile_id = "hud";
    config.diegetic_profile_id = "diegetic";

    snap.tick = 10u;
    snap.capability_count = 1u;
    snap.capabilities = &cap;
    cap_copy = cap;

    params.buf = buf;
    params.width = 640;
    params.height = 480;
    params.mode = dom::DOM_UI_MODE_HYBRID;
    params.anchors = &anchors;
    params.config = &config;
    params.allow_debug = 0;

    buf->count = 0u;
    dom::dom_ui_projection_render(defs, layouts, &snap, params);
    if (std::memcmp(&cap, &cap_copy, sizeof(dom_capability)) != 0) {
        return fail("projection mutated capability snapshot");
    }
    return 0;
}

int main(void) {
    int rc = test_projection_equivalence();
    if (rc != 0) {
        return rc;
    }
    rc = test_device_removal();
    if (rc != 0) {
        return rc;
    }
    rc = test_hud_unknown();
    if (rc != 0) {
        return rc;
    }
    rc = test_no_io_violation();
    if (rc != 0) {
        return rc;
    }
    rc = test_snapshot_immutability();
    if (rc != 0) {
        return rc;
    }
    std::printf("dom_ui_projection_tests passed\n");
    return 0;
}
