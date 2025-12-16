/*
FILE: source/dominium/tools/common/dom_tool_app.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_app
RESPONSIBILITY: Defines internal contract for `dom_tool_app`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TOOL_APP_H
#define DOM_TOOL_APP_H

#include <string>

extern "C" {
#include "view/d_view.h"
#include "ui/d_ui.h"
}

namespace dom {
namespace tools {

class DomToolController {
public:
    virtual ~DomToolController() {}

    virtual const char *tool_id() const = 0;
    virtual const char *tool_name() const = 0;
    virtual const char *tool_description() const = 0;

    virtual bool supports_demo() const { return false; }
    virtual std::string demo_path(const std::string &home) const { (void)home; return std::string(); }

    virtual bool load(const std::string &path, std::string &status) = 0;
    virtual bool validate(std::string &status) = 0;
    virtual bool save(const std::string &path, std::string &status) = 0;

    virtual void summary(std::string &out) const = 0;
};

class DomToolApp {
public:
    explicit DomToolApp(DomToolController &controller);
    ~DomToolApp();

    bool init(const std::string &sys_backend,
              const std::string &gfx_backend,
              const std::string &home,
              const std::string &load_path);

    int run();
    void shutdown();

private:
    DomToolApp(const DomToolApp &);
    DomToolApp &operator=(const DomToolApp &);

    void build_ui();
    void update_ui();
    void process_input_events();

    void action_validate();
    void action_save();
    void action_open_demo();
    void action_quit();

    static void on_click_validate(dui_widget *self);
    static void on_click_save(dui_widget *self);
    static void on_click_demo(dui_widget *self);
    static void on_click_quit(dui_widget *self);

private:
    DomToolController *m_controller;

    d_view_id    m_view;
    dui_context  m_ui;
    bool         m_running;

    std::string  m_home;
    std::string  m_loaded_path;
    std::string  m_status;
    std::string  m_summary;
    std::string  m_file_line;
    std::string  m_summary_line;
    std::string  m_status_line;

    dui_widget  *m_panel;
    dui_widget  *m_title;
    dui_widget  *m_file;
    dui_widget  *m_summary_label;
    dui_widget  *m_status_label;
    dui_widget  *m_btn_validate;
    dui_widget  *m_btn_save;
    dui_widget  *m_btn_demo;
    dui_widget  *m_btn_quit;
};

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_APP_H */
