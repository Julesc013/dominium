/*
FILE: source/tests/dom_ui_continuity_tests.cpp
MODULE: Dominium Tests
PURPOSE: Validate UI continuity state machine and placeholder rendering.
*/
#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/core/types.h"
#include "domino/gfx.h"
}

#include "runtime/dom_io_guard.h"
#include "ui/dom_ui_state.h"
#include "ui/dom_ui_views.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static int expect_true(bool cond, const char *msg) {
    if (!cond) {
        return fail(msg);
    }
    return 0;
}

static int test_seamless_travel() {
    dom::DomUiState st;
    u32 last_ms = 0u;
    int i;

    dom_io_guard_reset();
    dom::dom_ui_state_init(&st);

    dom::dom_ui_state_request_view(&st, dom::DOM_UI_VIEW_PLANET_MAP);
    for (i = 0; i < 40; ++i) {
        dom::dom_ui_state_tick(&st, 16u, 0);
        if (st.transition_active && st.transition_ms < last_ms) {
            return fail("transition_time_regressed");
        }
        last_ms = st.transition_ms;
    }
    if (st.view != dom::DOM_UI_VIEW_PLANET_MAP) {
        return fail("planet_view_not_reached");
    }

    dom::dom_ui_state_request_view(&st, dom::DOM_UI_VIEW_SYSTEM_MAP);
    for (i = 0; i < 40; ++i) {
        dom::dom_ui_state_tick(&st, 16u, 0);
    }
    if (st.view != dom::DOM_UI_VIEW_SYSTEM_MAP) {
        return fail("system_view_not_reached");
    }

    dom::dom_ui_state_request_view(&st, dom::DOM_UI_VIEW_GALAXY_MAP);
    for (i = 0; i < 40; ++i) {
        dom::dom_ui_state_tick(&st, 16u, 0);
    }
    if (st.view != dom::DOM_UI_VIEW_GALAXY_MAP) {
        return fail("galaxy_view_not_reached");
    }

    dom::dom_ui_state_tick(&st, 16u, 1);
    if (st.view != dom::DOM_UI_VIEW_TRANSIT) {
        return fail("transit_not_forced");
    }
    dom::dom_ui_state_tick(&st, 16u, 0);
    if (st.view != dom::DOM_UI_VIEW_GALAXY_MAP) {
        return fail("transit_return_mismatch");
    }

    dom::dom_ui_state_request_view(&st, dom::DOM_UI_VIEW_PLANET_MAP);
    for (i = 0; i < 40; ++i) {
        dom::dom_ui_state_tick(&st, 16u, 0);
    }
    if (st.view != dom::DOM_UI_VIEW_PLANET_MAP) {
        return fail("planet_view_return_failed");
    }

    dom::dom_ui_state_request_view(&st, dom::DOM_UI_VIEW_LOCAL);
    for (i = 0; i < 40; ++i) {
        dom::dom_ui_state_tick(&st, 16u, 0);
    }
    if (st.view != dom::DOM_UI_VIEW_LOCAL) {
        return fail("local_view_return_failed");
    }

    if (dom_io_guard_stall_count() != 0u) {
        return fail("unexpected_stall_count");
    }

    return 0;
}

static int test_fidelity_degradation_visual() {
    dom::DomUiViewParams params;
    d_gfx_cmd_buffer *buf;

    buf = d_gfx_cmd_buffer_begin();
    if (!buf) {
        return fail("cmd_buffer_begin");
    }

    params.buf = buf;
    params.width = 640;
    params.height = 480;
    params.fidelity = dom::DOM_FIDELITY_LOW;
    params.alpha = 255u;
    params.clear = 1;

    dom::dom_ui_render_planet_map(&params, 0, 0);
    if (buf->count == 0u) {
        return fail("planet_map_no_commands");
    }

    buf->count = 0u;
    dom::dom_ui_render_system_map(&params, 0);
    if (buf->count == 0u) {
        return fail("system_map_no_commands");
    }

    buf->count = 0u;
    dom::dom_ui_render_cosmos_map(&params, 0);
    if (buf->count == 0u) {
        return fail("cosmos_map_no_commands");
    }

    return 0;
}

static int test_input_continuity() {
    dom::DomUiState st;
    d_sys_event ev;
    int rc;

    dom::dom_ui_state_init(&st);
    std::memset(&ev, 0, sizeof(ev));

    ev.type = D_SYS_EVENT_KEY_DOWN;
    ev.u.key.key = D_SYS_KEY_2;
    rc = dom::dom_ui_state_handle_input(&st, &ev);
    if (rc != 1) {
        return fail("key_2_not_consumed");
    }
    dom::dom_ui_state_tick(&st, 32u, 0);

    ev.u.key.key = D_SYS_KEY_4;
    rc = dom::dom_ui_state_handle_input(&st, &ev);
    if (rc != 1) {
        return fail("key_4_not_consumed");
    }
    {
        int i;
        for (i = 0; i < 40; ++i) {
            dom::dom_ui_state_tick(&st, 16u, 0);
        }
    }
    if (st.view != dom::DOM_UI_VIEW_GALAXY_MAP) {
        return fail("input_did_not_select_galaxy");
    }

    ev.u.key.key = D_SYS_KEY_0;
    rc = dom::dom_ui_state_handle_input(&st, &ev);
    if (rc != 1) {
        return fail("key_0_not_consumed");
    }
    {
        int i;
        for (i = 0; i < 40; ++i) {
            dom::dom_ui_state_tick(&st, 16u, 0);
        }
    }
    if (st.view != dom::DOM_UI_VIEW_LOCAL) {
        return fail("input_did_not_select_local");
    }

    ev.u.key.key = D_SYS_KEY_ESCAPE;
    rc = dom::dom_ui_state_handle_input(&st, &ev);
    if (rc != 0) {
        return fail("escape_should_not_consume");
    }

    return 0;
}

static int run_named_test(const char *name) {
    if (!name || !name[0]) {
        return fail("missing_test_name");
    }
    if (std::strcmp(name, "seamless_travel") == 0) {
        return test_seamless_travel();
    }
    if (std::strcmp(name, "fidelity_degradation_visual") == 0) {
        return test_fidelity_degradation_visual();
    }
    if (std::strcmp(name, "input_continuity") == 0) {
        return test_input_continuity();
    }
    return fail("unknown_test_name");
}

int main(int argc, char **argv) {
    if (argc < 2) {
        int rc = 0;
        rc |= test_seamless_travel();
        rc |= test_fidelity_degradation_visual();
        rc |= test_input_continuity();
        return rc;
    }
    return run_named_test(argv[1]);
}
