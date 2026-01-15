/*
FILE: source/tests/dom_ui_widgets_tests.cpp
MODULE: Dominium Tests
PURPOSE: Validate widget definition parsing and capability-driven rendering.
*/
#include <cstdio>
#include <cstring>
#include <string>

extern "C" {
#include "domino/core/types.h"
#include "domino/gfx.h"
}

#include "runtime/dom_belief_store.h"
#include "runtime/dom_capability_engine.h"
#include "runtime/dom_time_knowledge.h"
#include "ui/dom_ui_widgets.h"

#ifndef UI_FIXTURE_ROOT
#define UI_FIXTURE_ROOT "tests/fixtures/ui"
#endif

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static std::string fixture_path(const char *name) {
    std::string path(UI_FIXTURE_ROOT);
    path.push_back('/');
    path.append(name ? name : "");
    return path;
}

static dom_belief_record make_record(u64 record_id,
                                     dom_capability_id cap,
                                     u32 subject_kind,
                                     u64 subject_id,
                                     i64 min_val,
                                     i64 max_val,
                                     dom_tick observed,
                                     dom_tick delivered,
                                     dom_tick expiry,
                                     u64 provenance,
                                     u32 flags,
                                     u32 resolution) {
    dom_belief_record r;
    r.record_id = record_id;
    r.capability_id = cap;
    r.subject.kind = subject_kind;
    r.subject.id = subject_id;
    r.resolution_tier = resolution;
    r.value_min = min_val;
    r.value_max = max_val;
    r.observed_tick = observed;
    r.delivery_tick = delivered;
    r.expiry_tick = expiry;
    r.source_provenance = provenance;
    r.flags = flags;
    return r;
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

static int test_load_fixtures(dom::DomUiWidgetRegistry &defs,
                              dom::DomUiLayoutSet &layouts) {
    std::string err;
    if (!dom::dom_ui_widgets_load_definitions(fixture_path("widgets.toml"), defs, err)) {
        std::fprintf(stderr, "load_definitions: %s\n", err.c_str());
        return 1;
    }
    if (!dom::dom_ui_widgets_load_layouts(fixture_path("layouts.toml"), layouts, err)) {
        std::fprintf(stderr, "load_layouts: %s\n", err.c_str());
        return 1;
    }
    if (defs.definitions.size() != 2u) {
        return fail("unexpected widget count");
    }
    if (layouts.profiles.size() != 1u) {
        return fail("unexpected layout profile count");
    }
    if (layouts.profiles[0].instances.size() != 2u) {
        return fail("unexpected instance count");
    }
    return 0;
}

static int test_render_with_caps(const dom::DomUiWidgetRegistry &defs,
                                 const dom::DomUiLayoutSet &layouts) {
    dom_belief_store *store = dom_belief_store_create();
    dom_capability_engine *engine = dom_capability_engine_create();
    dom_time_knowledge *tk = dom_time_knowledge_create(1u);
    dom_time_clock_def sundial;
    dom_time_clock_env env = { D_TRUE, D_TRUE, D_TRUE, 0u, 0u };
    d_gfx_cmd_buffer *buf = d_gfx_cmd_buffer_begin();
    dom::DomUiWidgetRenderParams params;
    const dom_capability_snapshot *snap = 0;
    dom_belief_record health;

    if (!store || !engine || !tk || !buf) {
        return fail("setup failed");
    }

    (void)dom_time_clock_init_sundial(100u, DOM_TIME_FRAME_ACT, &sundial);
    (void)dom_time_knowledge_add_clock(tk, &sundial, 0);

    health = make_record(1u, DOM_CAP_HEALTH_STATUS, DOM_CAP_SUBJECT_ENTITY, 7u,
                         95, 95, 10, 10, 0, 5u, 0u, DOM_RESOLUTION_EXACT);
    (void)dom_belief_store_add_record(store, &health);

    snap = dom_capability_engine_build_snapshot(engine, 1u, store, tk, 120, 60u, &env, 0);
    if (!snap) {
        return fail("snapshot build failed");
    }

    params.buf = buf;
    params.width = 640;
    params.height = 480;
    params.projection = dom::DOM_UI_PROJECTION_HUD_OVERLAY;

    buf->count = 0u;
    dom::dom_ui_widgets_render(defs, layouts.profiles[0], snap, params);
    if (buf->count == 0u) {
        return fail("no draw commands");
    }
    if (!find_text(buf, "Time")) {
        return fail("missing Time widget");
    }
    if (!find_text(buf, "Health")) {
        return fail("missing Health widget");
    }

    (void)dom_belief_store_remove_record(store, health.record_id);
    snap = dom_capability_engine_build_snapshot(engine, 1u, store, tk, 120, 60u, &env, 0);
    buf->count = 0u;
    dom::dom_ui_widgets_render(defs, layouts.profiles[0], snap, params);
    if (find_text(buf, "Health")) {
        return fail("health widget should be suppressed without uncertainty");
    }

    dom_time_knowledge_destroy(tk);
    dom_capability_engine_destroy(engine);
    dom_belief_store_destroy(store);
    d_gfx_shutdown();
    return 0;
}

int main(void) {
    dom::DomUiWidgetRegistry defs;
    dom::DomUiLayoutSet layouts;
    int rc = test_load_fixtures(defs, layouts);
    if (rc != 0) {
        return rc;
    }
    rc = test_render_with_caps(defs, layouts);
    if (rc != 0) {
        return rc;
    }
    std::printf("dom_ui_widgets_tests passed\n");
    return 0;
}
