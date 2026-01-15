/*
FILE: source/dominium/tools/common/dom_tool_app.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_app
RESPONSIBILITY: Implements `dom_tool_app`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_tool_app.h"

#include <cstring>

#include "dom_dui_util.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/gfx.h"
#include "domino/system/d_system.h"
#include "system/d_system_input.h"
}

namespace dom {
namespace tools {
namespace {

static dui_widget *add_label(dui_context &ctx, dui_widget *parent, const char *text) {
    dui_widget *w = dui_add_child_end(ctx, parent, DUI_WIDGET_LABEL);
    if (w) {
        w->text = text ? text : "";
    }
    return w;
}

static dui_widget *add_button(dui_context &ctx,
                              dui_widget *parent,
                              const char *text,
                              void (*on_click)(dui_widget *self),
                              void *user) {
    dui_widget *w = dui_add_child_end(ctx, parent, DUI_WIDGET_BUTTON);
    if (w) {
        w->text = text ? text : "";
        w->on_click = on_click;
        w->user_data = user;
    }
    return w;
}

} // namespace

DomToolApp::DomToolApp(DomToolController &controller)
    : m_controller(&controller),
      m_view(0),
      m_ui(),
      m_running(false),
      m_home(),
      m_loaded_path(),
      m_status(),
      m_summary(),
      m_file_line(),
      m_summary_line(),
      m_status_line(),
      m_panel(0),
      m_title(0),
      m_file(0),
      m_summary_label(0),
      m_status_label(0),
      m_btn_validate(0),
      m_btn_save(0),
      m_btn_demo(0),
      m_btn_quit(0) {
    std::memset(&m_ui, 0, sizeof(m_ui));
}

DomToolApp::~DomToolApp() {
    shutdown();
}

bool DomToolApp::init(const std::string &sys_backend,
                      const std::string &gfx_backend,
                      const std::string &home,
                      const std::string &load_path) {
    d_view_desc vdesc;
    const char *sys_key = sys_backend.empty() ? "win32" : sys_backend.c_str();
    const char *gfx_key = gfx_backend.empty() ? "soft" : gfx_backend.c_str();

    m_home = home;
    m_loaded_path = load_path;
    m_status = "Ready.";

    if (!d_system_init(sys_key)) {
        m_status = "d_system_init failed.";
        return false;
    }
    if (!d_gfx_init(gfx_key)) {
        m_status = "d_gfx_init failed.";
        d_system_shutdown();
        return false;
    }

    std::memset(&vdesc, 0, sizeof(vdesc));
    vdesc.id = 1u;
    vdesc.vp_x = d_q16_16_from_int(0);
    vdesc.vp_y = d_q16_16_from_int(0);
    vdesc.vp_w = d_q16_16_from_int(1);
    vdesc.vp_h = d_q16_16_from_int(1);
    vdesc.camera.fov = d_q16_16_from_int(60);
    m_view = d_view_create(&vdesc);

    dui_init_context(&m_ui);
    build_ui();

    if (!m_loaded_path.empty()) {
        (void)m_controller->load(m_loaded_path, m_status);
    }
    m_running = true;
    return true;
}

int DomToolApp::run() {
    while (m_running) {
        d_gfx_cmd_buffer *buf;
        d_view_frame frame;
        dui_rect rect;
        i32 width = 800;
        i32 height = 600;

        if (d_system_pump_events() != 0) {
            m_running = false;
            break;
        }
        process_input_events();
        update_ui();

        buf = d_gfx_cmd_buffer_begin();
        frame.cmd_buffer = buf;
        frame.view = d_view_get(m_view);
        d_gfx_get_surface_size(&width, &height);

        if (frame.view) {
            (void)d_view_render((d_world *)0, frame.view, &frame);
            rect.x = frame.view->vp_x;
            rect.y = frame.view->vp_y;
            rect.w = d_q16_16_from_int(width);
            rect.h = d_q16_16_from_int(height);
        } else {
            rect.x = d_q16_16_from_int(0);
            rect.y = d_q16_16_from_int(0);
            rect.w = d_q16_16_from_int(width);
            rect.h = d_q16_16_from_int(height);
        }

        dui_layout(&m_ui, &rect);
        dui_render(&m_ui, &frame);

        d_gfx_cmd_buffer_end(buf);
        d_gfx_submit(buf);
        d_gfx_present();
        d_system_sleep_ms(16);
    }

    shutdown();
    return 0;
}

void DomToolApp::shutdown() {
    if (m_view != 0) {
        d_view_destroy(m_view);
        m_view = 0;
    }
    if (m_ui.root) {
        dui_shutdown_context(&m_ui);
        std::memset(&m_ui, 0, sizeof(m_ui));
    }
    d_gfx_shutdown();
    d_system_shutdown();
    m_running = false;
}

void DomToolApp::build_ui() {
    dui_widget *root = m_ui.root;
    if (!root) {
        return;
    }

    dui_clear_children(m_ui, root);

    m_panel = dui_add_child_end(m_ui, root, DUI_WIDGET_PANEL);
    if (!m_panel) {
        return;
    }
    m_panel->layout_rect.h = d_q16_16_from_int(520);

    m_title = add_label(m_ui, m_panel, m_controller->tool_name());
    m_file = add_label(m_ui, m_panel, "");
    m_summary_label = add_label(m_ui, m_panel, "");
    m_status_label = add_label(m_ui, m_panel, "");

    m_btn_validate = add_button(m_ui, m_panel, "Validate", on_click_validate, this);
    m_btn_save = add_button(m_ui, m_panel, "Save", on_click_save, this);
    if (m_controller->supports_demo()) {
        m_btn_demo = add_button(m_ui, m_panel, "Open Demo", on_click_demo, this);
    } else {
        m_btn_demo = (dui_widget *)0;
    }
    m_btn_quit = add_button(m_ui, m_panel, "Quit", on_click_quit, this);
}

void DomToolApp::update_ui() {
    m_controller->summary(m_summary);

    m_file_line = std::string("File: ") + (m_loaded_path.empty() ? "(none)" : m_loaded_path);
    m_summary_line = std::string("Summary: ") + (m_summary.empty() ? "(none)" : m_summary);
    m_status_line = std::string("Status: ") + (m_status.empty() ? "(none)" : m_status);

    if (m_file) m_file->text = m_file_line.c_str();
    if (m_summary_label) m_summary_label->text = m_summary_line.c_str();
    if (m_status_label) m_status_label->text = m_status_line.c_str();
}

void DomToolApp::process_input_events() {
    d_sys_event ev;
    while (d_system_poll_event(&ev) > 0) {
        if (ev.type == D_SYS_EVENT_QUIT) {
            m_running = false;
            return;
        }
        if (ev.type == D_SYS_EVENT_MOUSE_BUTTON_DOWN) {
            (void)dui_try_click(m_ui, ev.u.mouse.x, ev.u.mouse.y);
        }
        if (ev.type == D_SYS_EVENT_KEY_DOWN) {
            if (ev.u.key.key == D_SYS_KEY_ESCAPE) {
                m_running = false;
                return;
            }
        }
    }
}

void DomToolApp::action_validate() {
    (void)m_controller->validate(m_status);
}

void DomToolApp::action_save() {
    if (m_loaded_path.empty()) {
        m_status = "No file loaded.";
        return;
    }
    (void)m_controller->save(m_loaded_path, m_status);
}

void DomToolApp::action_open_demo() {
    const std::string demo = m_controller->demo_path(m_home);
    if (demo.empty()) {
        m_status = "No demo available.";
        return;
    }
    m_loaded_path = demo;
    (void)m_controller->load(m_loaded_path, m_status);
}

void DomToolApp::action_quit() {
    m_running = false;
}

void DomToolApp::on_click_validate(dui_widget *self) {
    DomToolApp *app = self ? (DomToolApp *)self->user_data : (DomToolApp *)0;
    if (app) {
        app->action_validate();
    }
}

void DomToolApp::on_click_save(dui_widget *self) {
    DomToolApp *app = self ? (DomToolApp *)self->user_data : (DomToolApp *)0;
    if (app) {
        app->action_save();
    }
}

void DomToolApp::on_click_demo(dui_widget *self) {
    DomToolApp *app = self ? (DomToolApp *)self->user_data : (DomToolApp *)0;
    if (app) {
        app->action_open_demo();
    }
}

void DomToolApp::on_click_quit(dui_widget *self) {
    DomToolApp *app = self ? (DomToolApp *)self->user_data : (DomToolApp *)0;
    if (app) {
        app->action_quit();
    }
}

} // namespace tools
} // namespace dom
