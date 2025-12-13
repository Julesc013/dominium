#ifndef DOM_GAME_TOOLS_BUILD_H
#define DOM_GAME_TOOLS_BUILD_H

#include <stddef.h>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/gfx.h"
#include "system/d_system_input.h"
#include "build/d_build.h"
}

namespace dom {

class DomGameApp;

class DomGameBuildTool {
public:
    DomGameBuildTool();

    void set_none();
    void set_place_structure(d_structure_proto_id structure_id);
    void set_draw_spline(d_spline_profile_id spline_profile_id);

    void set_mouse_pos(int x, int y);

    /* Returns 1 if the tool consumed the event (e.g. Q/E rotation, clicks). */
    int handle_event(DomGameApp &app, const d_sys_event &ev);

    void render_overlay(const DomGameApp &app,
                        d_gfx_cmd_buffer *cmd_buffer,
                        i32 width,
                        i32 height) const;

    const char *status_text() const { return m_status; }

    int is_active() const { return m_mode != 0; }
    q16_16 yaw() const { return m_yaw; }

private:
    enum Mode {
        MODE_NONE = 0,
        MODE_PLACE_STRUCTURE = 1,
        MODE_DRAW_SPLINE = 2
    };

private:
    void clear_spline();
    void rotate_step(int dir);
    void set_status(const char *text);

    int commit_place_structure(DomGameApp &app, q32_32 wx, q32_32 wy);
    int commit_draw_spline(DomGameApp &app);

    int m_mode;
    d_structure_proto_id m_structure_id;
    d_spline_profile_id m_spline_profile_id;
    q16_16 m_yaw;

    int m_mouse_x;
    int m_mouse_y;

    int m_spline_active;
    u16 m_spline_node_count;
    d_spline_node m_spline_nodes[16];

    char m_status[128];
};

} // namespace dom

#endif /* DOM_GAME_TOOLS_BUILD_H */

