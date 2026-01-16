/*
FILE: source/domino/ui_ir/ui_layout.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir layout
RESPONSIBILITY: Deterministic layout computation for UI IR documents.
*/
#include "ui_layout.h"

#include <vector>

typedef struct domui_layout_writer {
    domui_layout_result* out;
    int capacity;
    int count;
} domui_layout_writer;

static void domui_diag_warn(domui_diag* diag,
                            const char* message,
                            domui_widget_id widget_id,
                            const char* context)
{
    if (diag) {
        diag->add_warning(message, widget_id, context);
    }
}

static void domui_diag_error(domui_diag* diag,
                             const char* message,
                             domui_widget_id widget_id,
                             const char* context)
{
    if (diag) {
        diag->add_error(message, widget_id, context);
    }
}

static domui_layout_rect domui_make_rect(int x, int y, int w, int h)
{
    domui_layout_rect r;
    r.x = x;
    r.y = y;
    r.w = w;
    r.h = h;
    return r;
}

static domui_layout_rect domui_inset_rect(const domui_layout_rect& r, const domui_box& inset)
{
    domui_layout_rect out = r;
    out.x += inset.left;
    out.y += inset.top;
    out.w -= (inset.left + inset.right);
    out.h -= (inset.top + inset.bottom);
    return out;
}

static void domui_clamp_nonnegative(domui_layout_rect& r)
{
    if (r.w < 0) {
        r.w = 0;
    }
    if (r.h < 0) {
        r.h = 0;
    }
}

static int domui_clamp_dim(int value, int min_v, int max_v)
{
    int v = value;
    if (v < min_v) {
        v = min_v;
    }
    if (max_v >= 0 && v > max_v) {
        v = max_v;
    }
    return v;
}

static void domui_apply_constraints(const domui_widget* w,
                                    domui_layout_rect& rect,
                                    bool align_right,
                                    int right_edge,
                                    bool align_bottom,
                                    int bottom_edge,
                                    domui_diag* diag)
{
    if (!w) {
        return;
    }
    rect.w = domui_clamp_dim(rect.w, w->min_w, w->max_w);
    rect.h = domui_clamp_dim(rect.h, w->min_h, w->max_h);

    if (align_right) {
        rect.x = right_edge - rect.w;
    }
    if (align_bottom) {
        rect.y = bottom_edge - rect.h;
    }

    if (rect.w < 0 || rect.h < 0) {
        domui_diag_error(diag, "layout: negative size after constraints", w->id, "size");
        if (rect.w < 0) {
            rect.w = 0;
        }
        if (rect.h < 0) {
            rect.h = 0;
        }
    }
}

static bool domui_outer_fits_parent(const domui_layout_rect& parent_content,
                                    const domui_layout_rect& rect,
                                    const domui_box& margin)
{
    int outer_left = rect.x - margin.left;
    int outer_top = rect.y - margin.top;
    int outer_right = rect.x + rect.w + margin.right;
    int outer_bottom = rect.y + rect.h + margin.bottom;

    if (outer_left < parent_content.x || outer_top < parent_content.y) {
        return false;
    }
    if (outer_right > parent_content.x + parent_content.w) {
        return false;
    }
    if (outer_bottom > parent_content.y + parent_content.h) {
        return false;
    }
    return true;
}

static void domui_layout_write(domui_layout_writer& writer,
                               domui_widget_id widget_id,
                               const domui_layout_rect& rect)
{
    if (writer.out && writer.count < writer.capacity) {
        writer.out[writer.count].widget_id = widget_id;
        writer.out[writer.count].rect = rect;
    }
    writer.count += 1;
}

static void domui_layout_children(const domui_doc* doc,
                                  const domui_widget* parent_widget,
                                  domui_widget_id parent_id,
                                  const domui_layout_rect& parent_rect,
                                  domui_layout_writer& writer,
                                  domui_diag* diag);

static int domui_prop_get_int_default(const domui_props& props, const char* key, int def_v)
{
    domui_value v;
    if (!props.get(key, &v)) {
        return def_v;
    }
    switch (v.type) {
    case DOMUI_VALUE_INT:
        return v.v_int;
    case DOMUI_VALUE_UINT:
        return (int)v.v_uint;
    case DOMUI_VALUE_BOOL:
        return v.v_bool ? 1 : 0;
    default:
        break;
    }
    return def_v;
}

static int domui_prop_get_string(const domui_props& props, const char* key, domui_string& out)
{
    domui_value v;
    if (!props.get(key, &v)) {
        return 0;
    }
    if (v.type != DOMUI_VALUE_STRING) {
        return 0;
    }
    out = v.v_string;
    return 1;
}

static void domui_layout_hide_subtree(const domui_doc* doc,
                                      domui_widget_id widget_id,
                                      domui_layout_writer& writer)
{
    std::vector<domui_widget_id> children;
    domui_layout_rect zero = domui_make_rect(0, 0, 0, 0);
    domui_layout_write(writer, widget_id, zero);
    if (!doc) {
        return;
    }
    doc->enumerate_children(widget_id, children);
    for (size_t i = 0u; i < children.size(); ++i) {
        domui_layout_hide_subtree(doc, children[i], writer);
    }
}

static void domui_layout_children_splitter(const domui_doc* doc,
                                           const domui_widget* splitter,
                                           domui_widget_id parent_id,
                                           const domui_layout_rect& parent_content,
                                           domui_layout_writer& writer,
                                           domui_diag* diag)
{
    std::vector<domui_widget_id> children;
    domui_layout_rect region_a;
    domui_layout_rect region_b;
    int is_horizontal = 0;
    int thickness = 4;
    int pos = -1;
    int min_a = 0;
    int min_b = 0;
    int axis_len = 0;
    int avail_axis = 0;
    int max_pos = 0;

    if (!doc || !splitter) {
        return;
    }

    {
        domui_string orient;
        if (domui_prop_get_string(splitter->props, "splitter.orientation", orient)) {
            const char* s = orient.c_str();
            if (s && (s[0] == 'h' || s[0] == 'H')) {
                is_horizontal = 1;
            }
        }
    }

    thickness = domui_prop_get_int_default(splitter->props, "splitter.thickness", 4);
    if (thickness < 1) {
        thickness = 1;
    }
    pos = domui_prop_get_int_default(splitter->props, "splitter.pos", -1);
    min_a = domui_prop_get_int_default(splitter->props, "splitter.min_a", 0);
    min_b = domui_prop_get_int_default(splitter->props, "splitter.min_b", 0);
    if (min_a < 0) min_a = 0;
    if (min_b < 0) min_b = 0;

    axis_len = is_horizontal ? parent_content.h : parent_content.w;
    avail_axis = axis_len - thickness;
    if (avail_axis < 0) {
        avail_axis = 0;
    }
    if (pos < 0) {
        pos = avail_axis / 2;
    }

    if ((min_a + min_b) > avail_axis) {
        domui_diag_error(diag, "layout: parent rect too small for splitter constraints", splitter->id, "splitter");
    }
    max_pos = avail_axis - min_b;
    if (max_pos < 0) {
        max_pos = 0;
    }
    if (pos < min_a) {
        pos = min_a;
    }
    if (pos > max_pos) {
        pos = max_pos;
    }
    if (pos < 0) {
        pos = 0;
    }

    if (is_horizontal) {
        region_a = domui_make_rect(parent_content.x, parent_content.y, parent_content.w, pos);
        region_b = domui_make_rect(parent_content.x,
                                   parent_content.y + pos + thickness,
                                   parent_content.w,
                                   avail_axis - pos);
    } else {
        region_a = domui_make_rect(parent_content.x, parent_content.y, pos, parent_content.h);
        region_b = domui_make_rect(parent_content.x + pos + thickness,
                                   parent_content.y,
                                   avail_axis - pos,
                                   parent_content.h);
    }
    domui_clamp_nonnegative(region_a);
    domui_clamp_nonnegative(region_b);

    doc->enumerate_children(parent_id, children);
    for (size_t i = 0u; i < children.size(); ++i) {
        const domui_widget* w = doc->find_by_id(children[i]);
        if (!w) {
            continue;
        }
        if (i >= 2u) {
            domui_layout_hide_subtree(doc, w->id, writer);
            continue;
        }
        {
            domui_layout_rect rect = (i == 0u) ? region_a : region_b;
            rect = domui_inset_rect(rect, w->margin);
            domui_apply_constraints(w, rect, false, 0, false, 0, diag);
            if (!domui_outer_fits_parent((i == 0u) ? region_a : region_b, rect, w->margin)) {
                domui_diag_error(diag, "layout: parent rect too small for child constraints", w->id, "constraints");
            }
            domui_layout_write(writer, w->id, rect);
            domui_layout_children(doc, w, w->id, rect, writer, diag);
        }
    }
}

static void domui_layout_children_tabs(const domui_doc* doc,
                                       const domui_widget* tabs,
                                       domui_widget_id parent_id,
                                       const domui_layout_rect& parent_content,
                                       domui_layout_writer& writer,
                                       domui_diag* diag)
{
    std::vector<domui_widget_id> children;
    std::vector<domui_widget_id> pages;
    domui_layout_rect content = parent_content;
    domui_string placement;
    int selected_index = 0;
    int strip_thickness = 24;
    size_t i;
    size_t selected_page = 0u;
    int use_explicit_pages = 0;

    if (!doc || !tabs) {
        return;
    }

    doc->enumerate_children(parent_id, children);
    for (i = 0u; i < children.size(); ++i) {
        const domui_widget* w = doc->find_by_id(children[i]);
        if (w && w->type == DOMUI_WIDGET_TAB_PAGE) {
            use_explicit_pages = 1;
            break;
        }
    }
    for (i = 0u; i < children.size(); ++i) {
        const domui_widget* w = doc->find_by_id(children[i]);
        if (!w) {
            continue;
        }
        if (!use_explicit_pages || w->type == DOMUI_WIDGET_TAB_PAGE) {
            pages.push_back(w->id);
        }
    }

    selected_index = domui_prop_get_int_default(tabs->props, "tabs.selected_index", 0);
    if (selected_index < 0) {
        selected_index = 0;
    }
    if (!pages.empty()) {
        if ((size_t)selected_index >= pages.size()) {
            selected_index = (int)(pages.size() - 1u);
        }
        selected_page = (size_t)selected_index;
    }

    if (domui_prop_get_string(tabs->props, "tabs.placement", placement)) {
        const char* s = placement.c_str();
        if (s && (s[0] == 'b' || s[0] == 'B')) {
            content.h -= strip_thickness;
        } else if (s && (s[0] == 'l' || s[0] == 'L')) {
            content.x += strip_thickness;
            content.w -= strip_thickness;
        } else if (s && (s[0] == 'r' || s[0] == 'R')) {
            content.w -= strip_thickness;
        } else {
            content.y += strip_thickness;
            content.h -= strip_thickness;
        }
    } else {
        content.y += strip_thickness;
        content.h -= strip_thickness;
    }
    domui_clamp_nonnegative(content);

    for (i = 0u; i < children.size(); ++i) {
        const domui_widget* w = doc->find_by_id(children[i]);
        size_t page_index = 0u;
        int is_page = 0;
        if (!w) {
            continue;
        }
        if (use_explicit_pages && w->type == DOMUI_WIDGET_TAB_PAGE) {
            is_page = 1;
        } else if (!use_explicit_pages) {
            is_page = 1;
        }

        if (is_page) {
            size_t j;
            for (j = 0u; j < pages.size(); ++j) {
                if (pages[j] == w->id) {
                    page_index = j;
                    break;
                }
            }
        }

        if (!is_page || pages.empty() || page_index != selected_page) {
            domui_layout_hide_subtree(doc, w->id, writer);
            continue;
        }

        {
            domui_layout_rect rect = domui_inset_rect(content, w->margin);
            domui_apply_constraints(w, rect, false, 0, false, 0, diag);
            domui_layout_write(writer, w->id, rect);
            domui_layout_children(doc, w, w->id, rect, writer, diag);
        }
    }
}

static void domui_layout_children_scrollpanel(const domui_doc* doc,
                                              const domui_widget* panel,
                                              domui_widget_id parent_id,
                                              const domui_layout_rect& parent_content,
                                              domui_layout_writer& writer,
                                              domui_diag* diag)
{
    std::vector<domui_widget_id> children;
    size_t i;

    if (!doc || !panel) {
        return;
    }

    doc->enumerate_children(parent_id, children);
    for (i = 0u; i < children.size(); ++i) {
        const domui_widget* w = doc->find_by_id(children[i]);
        if (!w) {
            continue;
        }
        if (i >= 1u) {
            domui_layout_hide_subtree(doc, w->id, writer);
            continue;
        }
        {
            domui_layout_rect rect = parent_content;
            rect.x = parent_content.x + w->margin.left;
            rect.y = parent_content.y + w->margin.top;
            rect.w = w->w;
            rect.h = w->h;
            if (rect.w == 0) {
                rect.w = parent_content.w - (w->margin.left + w->margin.right);
            }
            if (rect.h == 0) {
                rect.h = parent_content.h - (w->margin.top + w->margin.bottom);
            }
            domui_apply_constraints(w, rect, false, 0, false, 0, diag);
            domui_layout_write(writer, w->id, rect);
            domui_layout_children(doc, w, w->id, rect, writer, diag);
        }
    }
}

static void domui_layout_children_stack(const domui_doc* doc,
                                        domui_widget_id parent_id,
                                        const domui_layout_rect& parent_content,
                                        bool row,
                                        domui_layout_writer& writer,
                                        domui_diag* diag)
{
    std::vector<domui_widget_id> children;
    int cursor = 0;
    size_t i;

    doc->enumerate_children(parent_id, children);
    for (i = 0u; i < children.size(); ++i) {
        const domui_widget* w = doc->find_by_id(children[i]);
        domui_layout_rect rect;
        int reserved;
        if (!w) {
            continue;
        }

        rect.w = w->w;
        rect.h = w->h;
        if (row) {
            rect.x = parent_content.x + cursor + w->margin.left;
            rect.y = parent_content.y + w->margin.top;
        } else {
            rect.x = parent_content.x + w->margin.left;
            rect.y = parent_content.y + cursor + w->margin.top;
        }

        domui_apply_constraints(w, rect, false, 0, false, 0, diag);

        if (!domui_outer_fits_parent(parent_content, rect, w->margin)) {
            domui_diag_error(diag, "layout: parent rect too small for child constraints", w->id, "constraints");
        }

        domui_layout_write(writer, w->id, rect);
        domui_layout_children(doc, w, w->id, rect, writer, diag);

        if (row) {
            reserved = rect.w + w->margin.left + w->margin.right;
        } else {
            reserved = rect.h + w->margin.top + w->margin.bottom;
        }
        cursor += reserved;
    }
}

static void domui_layout_children_default(const domui_doc* doc,
                                          domui_widget_id parent_id,
                                          const domui_layout_rect& parent_content,
                                          domui_layout_writer& writer,
                                          domui_diag* diag)
{
    std::vector<domui_widget_id> children;
    domui_layout_rect avail = parent_content;
    int fill_count = 0;
    size_t i;

    doc->enumerate_children(parent_id, children);
    for (i = 0u; i < children.size(); ++i) {
        const domui_widget* w = doc->find_by_id(children[i]);
        domui_layout_rect rect;
        bool align_right = false;
        bool align_bottom = false;
        int right_edge = 0;
        int bottom_edge = 0;
        bool should_fit_parent = false;
        domui_layout_rect fit_rect = parent_content;
        domui_dock_mode dock;
        if (!w) {
            continue;
        }

        dock = w->dock;
        if (dock != DOMUI_DOCK_NONE) {
            fit_rect = avail;
            should_fit_parent = true;
            switch (dock) {
            case DOMUI_DOCK_LEFT:
                rect.x = avail.x + w->margin.left;
                rect.y = avail.y + w->margin.top;
                rect.w = w->w;
                rect.h = avail.h - (w->margin.top + w->margin.bottom);
                break;
            case DOMUI_DOCK_RIGHT:
                right_edge = avail.x + avail.w - w->margin.right;
                rect.y = avail.y + w->margin.top;
                rect.w = w->w;
                rect.h = avail.h - (w->margin.top + w->margin.bottom);
                rect.x = right_edge - rect.w;
                align_right = true;
                break;
            case DOMUI_DOCK_TOP:
                rect.x = avail.x + w->margin.left;
                rect.y = avail.y + w->margin.top;
                rect.w = avail.w - (w->margin.left + w->margin.right);
                rect.h = w->h;
                break;
            case DOMUI_DOCK_BOTTOM:
                rect.x = avail.x + w->margin.left;
                bottom_edge = avail.y + avail.h - w->margin.bottom;
                rect.w = avail.w - (w->margin.left + w->margin.right);
                rect.h = w->h;
                rect.y = bottom_edge - rect.h;
                align_bottom = true;
                break;
            case DOMUI_DOCK_FILL:
                rect.x = avail.x + w->margin.left;
                rect.y = avail.y + w->margin.top;
                rect.w = avail.w - (w->margin.left + w->margin.right);
                rect.h = avail.h - (w->margin.top + w->margin.bottom);
                if (fill_count >= 1) {
                    domui_diag_warn(diag, "layout: multiple dock fill children", w->id, "dock.fill");
                }
                fill_count += 1;
                break;
            default:
                rect = domui_make_rect(0, 0, 0, 0);
                break;
            }
        } else if (w->anchors != 0u) {
            bool anchor_l = (w->anchors & DOMUI_ANCHOR_L) != 0u;
            bool anchor_r = (w->anchors & DOMUI_ANCHOR_R) != 0u;
            bool anchor_t = (w->anchors & DOMUI_ANCHOR_T) != 0u;
            bool anchor_b = (w->anchors & DOMUI_ANCHOR_B) != 0u;
            should_fit_parent = true;

            if (anchor_l && anchor_r) {
                int left = w->x + w->margin.left;
                int right = w->w + w->margin.right;
                rect.x = parent_content.x + left;
                rect.w = parent_content.w - left - right;
            } else if (anchor_l) {
                int left = w->x + w->margin.left;
                rect.x = parent_content.x + left;
                rect.w = w->w;
            } else if (anchor_r) {
                int right = w->x + w->margin.right;
                right_edge = parent_content.x + parent_content.w - right;
                rect.w = w->w;
                rect.x = right_edge - rect.w;
                align_right = true;
            } else {
                rect.x = parent_content.x + w->x + w->margin.left;
                rect.w = w->w;
            }

            if (anchor_t && anchor_b) {
                int top = w->y + w->margin.top;
                int bottom = w->h + w->margin.bottom;
                rect.y = parent_content.y + top;
                rect.h = parent_content.h - top - bottom;
            } else if (anchor_t) {
                int top = w->y + w->margin.top;
                rect.y = parent_content.y + top;
                rect.h = w->h;
            } else if (anchor_b) {
                int bottom = w->y + w->margin.bottom;
                bottom_edge = parent_content.y + parent_content.h - bottom;
                rect.h = w->h;
                rect.y = bottom_edge - rect.h;
                align_bottom = true;
            } else {
                rect.y = parent_content.y + w->y + w->margin.top;
                rect.h = w->h;
            }
        } else {
            rect.x = parent_content.x + w->x + w->margin.left;
            rect.y = parent_content.y + w->y + w->margin.top;
            rect.w = w->w;
            rect.h = w->h;
        }

        domui_apply_constraints(w, rect, align_right, right_edge, align_bottom, bottom_edge, diag);

        if (should_fit_parent && !domui_outer_fits_parent(fit_rect, rect, w->margin)) {
            domui_diag_error(diag, "layout: parent rect too small for child constraints", w->id, "constraints");
        }

        domui_layout_write(writer, w->id, rect);
        domui_layout_children(doc, w, w->id, rect, writer, diag);

        if (dock != DOMUI_DOCK_NONE) {
            if (dock == DOMUI_DOCK_LEFT || dock == DOMUI_DOCK_RIGHT) {
                int reserved = rect.w + w->margin.left + w->margin.right;
                if (dock == DOMUI_DOCK_LEFT) {
                    avail.x += reserved;
                    avail.w -= reserved;
                } else {
                    avail.w -= reserved;
                }
            } else if (dock == DOMUI_DOCK_TOP || dock == DOMUI_DOCK_BOTTOM) {
                int reserved = rect.h + w->margin.top + w->margin.bottom;
                if (dock == DOMUI_DOCK_TOP) {
                    avail.y += reserved;
                    avail.h -= reserved;
                } else {
                    avail.h -= reserved;
                }
            } else if (dock == DOMUI_DOCK_FILL) {
                avail.x = avail.x + avail.w;
                avail.y = avail.y + avail.h;
                avail.w = 0;
                avail.h = 0;
            }
        }
    }
}

static void domui_layout_children(const domui_doc* doc,
                                  const domui_widget* parent_widget,
                                  domui_widget_id parent_id,
                                  const domui_layout_rect& parent_rect,
                                  domui_layout_writer& writer,
                                  domui_diag* diag)
{
    domui_layout_rect content = parent_rect;
    domui_container_layout_mode layout_mode = DOMUI_LAYOUT_ABSOLUTE;
    if (parent_widget) {
        content = domui_inset_rect(parent_rect, parent_widget->padding);
        layout_mode = parent_widget->layout_mode;
    }
    domui_clamp_nonnegative(content);

    if (parent_widget) {
        if (parent_widget->type == DOMUI_WIDGET_SPLITTER) {
            domui_layout_children_splitter(doc, parent_widget, parent_id, content, writer, diag);
            return;
        }
        if (parent_widget->type == DOMUI_WIDGET_TABS) {
            domui_layout_children_tabs(doc, parent_widget, parent_id, content, writer, diag);
            return;
        }
        if (parent_widget->type == DOMUI_WIDGET_SCROLLPANEL) {
            domui_layout_children_scrollpanel(doc, parent_widget, parent_id, content, writer, diag);
            return;
        }
    }

    if (layout_mode == DOMUI_LAYOUT_STACK_ROW) {
        domui_layout_children_stack(doc, parent_id, content, true, writer, diag);
    } else if (layout_mode == DOMUI_LAYOUT_STACK_COL) {
        domui_layout_children_stack(doc, parent_id, content, false, writer, diag);
    } else {
        domui_layout_children_default(doc, parent_id, content, writer, diag);
    }
}

bool domui_compute_layout(const domui_doc* doc,
                          domui_widget_id root_id,
                          int root_x,
                          int root_y,
                          int root_w,
                          int root_h,
                          domui_layout_result* out_results,
                          int* inout_result_count,
                          domui_diag* diag)
{
    domui_layout_writer writer;
    int capacity;

    if (!doc || !inout_result_count) {
        domui_diag_error(diag, "layout: invalid arguments", 0u, "layout");
        return false;
    }

    if (diag) {
        diag->clear();
    }

    capacity = *inout_result_count;
    if (capacity < 0) {
        capacity = 0;
    }
    if (!out_results && capacity > 0) {
        domui_diag_error(diag, "layout: output buffer is null", 0u, "layout");
        *inout_result_count = 0;
        return false;
    }

    writer.out = out_results;
    writer.capacity = capacity;
    writer.count = 0;

    if (root_id == 0u) {
        domui_layout_rect root_rect = domui_make_rect(root_x, root_y, root_w, root_h);
        domui_layout_children(doc, 0, 0u, root_rect, writer, diag);
    } else {
        const domui_widget* root = doc->find_by_id(root_id);
        domui_layout_rect root_rect;
        if (!root) {
            domui_diag_error(diag, "layout: root id not found", root_id, "layout");
            *inout_result_count = 0;
            return false;
        }
        root_rect = domui_make_rect(root_x, root_y, root_w, root_h);
        domui_apply_constraints(root, root_rect, false, 0, false, 0, diag);
        domui_layout_write(writer, root->id, root_rect);
        domui_layout_children(doc, root, root->id, root_rect, writer, diag);
    }

    *inout_result_count = writer.count;
    if (writer.count > writer.capacity) {
        domui_diag_error(diag, "layout: output buffer too small", 0u, "layout");
        return false;
    }
    return true;
}
