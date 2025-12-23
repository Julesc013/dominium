/*
FILE: tools/tool_editor/tool_editor_docgen.cpp
MODULE: Dominium tools
RESPONSIBILITY: Generate the initial Tool Editor UI docs (TLV + JSON mirror).
*/
#include <stdio.h>

#if defined(_WIN32)
#include <direct.h>
#else
#include <sys/stat.h>
#include <sys/types.h>
#endif

#include "ui_ir_doc.h"
#include "ui_ir_props.h"
#include "ui_ir_tlv.h"
#include "ui_ir_diag.h"

static void make_dir_one(const char* path)
{
    if (!path || !path[0]) {
        return;
    }
#if defined(_WIN32)
    _mkdir(path);
#else
    mkdir(path, 0755);
#endif
}

static void ensure_tool_editor_dirs(void)
{
    make_dir_one("tools");
    make_dir_one("tools/tool_editor");
    make_dir_one("tools/tool_editor/ui");
    make_dir_one("tools/tool_editor/ui/doc");
}

static void set_text_prop(domui_widget* w, const char* text)
{
    if (!w) {
        return;
    }
    domui_string s(text ? text : "");
    w->props.set("text", domui_value_string(s));
}

static domui_widget_id add_widget(domui_doc& doc,
                                  domui_widget_type type,
                                  domui_widget_id parent_id,
                                  const char* name,
                                  int x,
                                  int y,
                                  int w_px,
                                  int h_px)
{
    domui_widget_id id = doc.create_widget(type, parent_id);
    domui_widget* w = doc.find_by_id(id);
    if (!w) {
        return 0u;
    }
    w->name.set(name ? name : "");
    w->x = x;
    w->y = y;
    w->w = w_px;
    w->h = h_px;
    return id;
}

static void set_dock(domui_doc& doc, domui_widget_id id, domui_dock_mode dock)
{
    domui_widget* w = doc.find_by_id(id);
    if (!w) {
        return;
    }
    w->dock = dock;
}

static void set_anchor(domui_doc& doc, domui_widget_id id, domui_u32 anchors)
{
    domui_widget* w = doc.find_by_id(id);
    if (!w) {
        return;
    }
    w->anchors = anchors;
}

static void set_splitter_defaults(domui_doc& doc,
                                  domui_widget_id id,
                                  const char* orient,
                                  int pos,
                                  int thickness,
                                  int min_a,
                                  int min_b)
{
    domui_widget* w = doc.find_by_id(id);
    if (!w) {
        return;
    }
    w->props.set("splitter.orientation", domui_value_string(domui_string(orient ? orient : "v")));
    w->props.set("splitter.pos", domui_value_int(pos));
    w->props.set("splitter.thickness", domui_value_int(thickness));
    w->props.set("splitter.min_a", domui_value_int(min_a));
    w->props.set("splitter.min_b", domui_value_int(min_b));
}

static void set_tabs_defaults(domui_doc& doc, domui_widget_id id)
{
    domui_widget* w = doc.find_by_id(id);
    if (!w) {
        return;
    }
    w->props.set("tabs.selected_index", domui_value_int(0));
    w->props.set("tabs.placement", domui_value_string(domui_string("top")));
}

static void set_tab_page_props(domui_doc& doc, domui_widget_id id, const char* title, int enabled)
{
    domui_widget* w = doc.find_by_id(id);
    if (!w) {
        return;
    }
    w->props.set("tab.title", domui_value_string(domui_string(title ? title : "")));
    w->props.set("tab.enabled", domui_value_bool(enabled ? 1 : 0));
}

static domui_doc build_tool_editor_ui_doc(void)
{
    domui_doc doc;
    domui_widget_id root;
    domui_widget_id top_bar;
    domui_widget_id tabs;
    domui_widget_id log_list;
    domui_widget_id split_main;
    domui_widget_id pane_left;
    domui_widget_id split_center_right;
    domui_widget_id pane_center;
    domui_widget_id pane_right;

    doc.meta.doc_name = domui_string("tool_editor");
    doc.meta.doc_version = 2u;
    doc.meta.target_backends.push_back(domui_string("win32"));

    root = add_widget(doc, DOMUI_WIDGET_CONTAINER, 0u, "root", 0, 0, 1280, 720);
    set_dock(doc, root, DOMUI_DOCK_FILL);

    top_bar = add_widget(doc, DOMUI_WIDGET_CONTAINER, root, "top_bar", 0, 0, 0, 28);
    set_dock(doc, top_bar, DOMUI_DOCK_TOP);

    tabs = add_widget(doc, DOMUI_WIDGET_TABS, top_bar, "doc_tabs", 8, 2, 400, 22);
    set_anchor(doc, tabs, DOMUI_ANCHOR_L | DOMUI_ANCHOR_R);
    set_tabs_defaults(doc, tabs);
    {
        domui_widget* w = doc.find_by_id(tabs);
        if (w) {
            w->events.set("on_tab_change", "tool_editor.tab_change");
        }
    }

    {
        const int max_tabs = 4;
        int i;
        for (i = 0; i < max_tabs; ++i) {
            char name[32];
            char title[64];
            sprintf(name, "doc_tab_%d", i);
            sprintf(title, "Doc %d", i + 1);
            {
                domui_widget_id page = add_widget(doc, DOMUI_WIDGET_TAB_PAGE, tabs, name, 0, 0, 0, 0);
                set_tab_page_props(doc, page, title, (i == 0) ? 1 : 0);
            }
        }
    }

    {
        domui_widget_id btn_new = add_widget(doc, DOMUI_WIDGET_BUTTON, top_bar, "btn_new", 8, 2, 52, 22);
        domui_widget_id btn_open = add_widget(doc, DOMUI_WIDGET_BUTTON, top_bar, "btn_open", 64, 2, 56, 22);
        domui_widget_id btn_save = add_widget(doc, DOMUI_WIDGET_BUTTON, top_bar, "btn_save", 124, 2, 56, 22);
        domui_widget_id btn_save_as = add_widget(doc, DOMUI_WIDGET_BUTTON, top_bar, "btn_save_as", 184, 2, 68, 22);
        domui_widget_id btn_validate = add_widget(doc, DOMUI_WIDGET_BUTTON, top_bar, "btn_validate", 256, 2, 72, 22);
        domui_widget* w;

        w = doc.find_by_id(btn_new);
        if (w) {
            set_text_prop(w, "New");
            w->events.set("on_click", "tool_editor.new");
        }
        w = doc.find_by_id(btn_open);
        if (w) {
            set_text_prop(w, "Open");
            w->events.set("on_click", "tool_editor.open");
        }
        w = doc.find_by_id(btn_save);
        if (w) {
            set_text_prop(w, "Save");
            w->events.set("on_click", "tool_editor.save");
        }
        w = doc.find_by_id(btn_save_as);
        if (w) {
            set_text_prop(w, "Save As");
            w->events.set("on_click", "tool_editor.save_as");
        }
        w = doc.find_by_id(btn_validate);
        if (w) {
            set_text_prop(w, "Validate");
            w->events.set("on_click", "tool_editor.validate");
        }
    }

    log_list = add_widget(doc, DOMUI_WIDGET_LISTBOX, root, "log_list", 0, 0, 0, 140);
    set_dock(doc, log_list, DOMUI_DOCK_BOTTOM);

    split_main = add_widget(doc, DOMUI_WIDGET_SPLITTER, root, "split_main", 0, 0, 0, 0);
    set_dock(doc, split_main, DOMUI_DOCK_FILL);
    set_splitter_defaults(doc, split_main, "v", 240, 4, 160, 240);

    pane_left = add_widget(doc, DOMUI_WIDGET_CONTAINER, split_main, "pane_left", 0, 0, 0, 0);
    split_center_right = add_widget(doc, DOMUI_WIDGET_SPLITTER, split_main, "split_center_right", 0, 0, 0, 0);
    set_splitter_defaults(doc, split_center_right, "v", 640, 4, 240, 240);

    {
        domui_widget_id label = add_widget(doc, DOMUI_WIDGET_STATIC_TEXT, pane_left, "label_hierarchy", 8, 6, 90, 16);
        domui_widget_id btn_add = add_widget(doc, DOMUI_WIDGET_BUTTON, pane_left, "btn_add", 100, 2, 48, 22);
        domui_widget_id btn_del = add_widget(doc, DOMUI_WIDGET_BUTTON, pane_left, "btn_delete", 152, 2, 56, 22);
        domui_widget_id list = add_widget(doc, DOMUI_WIDGET_LISTBOX, pane_left, "list_hierarchy", 8, 26, 8, 8);
        domui_widget* w;

        w = doc.find_by_id(label);
        set_text_prop(w, "Hierarchy");
        w = doc.find_by_id(btn_add);
        if (w) {
            set_text_prop(w, "Add");
            w->events.set("on_click", "tool_editor.add_widget");
        }
        w = doc.find_by_id(btn_del);
        if (w) {
            set_text_prop(w, "Delete");
            w->events.set("on_click", "tool_editor.delete_widget");
        }
        w = doc.find_by_id(list);
        if (w) {
            w->events.set("on_change", "tool_editor.hierarchy_select");
        }
        set_anchor(doc, list, DOMUI_ANCHOR_L | DOMUI_ANCHOR_R | DOMUI_ANCHOR_T | DOMUI_ANCHOR_B);
    }

    pane_center = add_widget(doc, DOMUI_WIDGET_CONTAINER, split_center_right, "pane_center", 0, 0, 0, 0);
    pane_right = add_widget(doc, DOMUI_WIDGET_CONTAINER, split_center_right, "pane_right", 0, 0, 0, 0);

    {
        domui_widget_id label = add_widget(doc, DOMUI_WIDGET_STATIC_TEXT, pane_center, "label_preview", 8, 6, 90, 16);
        domui_widget_id host = add_widget(doc, DOMUI_WIDGET_CONTAINER, pane_center, "preview_host", 8, 26, 8, 8);
        set_text_prop(doc.find_by_id(label), "Preview");
        set_anchor(doc, host, DOMUI_ANCHOR_L | DOMUI_ANCHOR_R | DOMUI_ANCHOR_T | DOMUI_ANCHOR_B);
    }

    {
        int y = 8;
        const int row = 24;
        domui_widget_id label = add_widget(doc, DOMUI_WIDGET_STATIC_TEXT, pane_right, "label_props", 8, y, 90, 16);
        set_text_prop(doc.find_by_id(label), "Properties");
        y += row;

        {
            domui_widget_id lbl = add_widget(doc, DOMUI_WIDGET_STATIC_TEXT, pane_right, "label_name", 8, y, 60, 16);
            domui_widget_id edit = add_widget(doc, DOMUI_WIDGET_EDIT, pane_right, "edit_name", 72, y - 2, 140, 20);
            set_text_prop(doc.find_by_id(lbl), "Name");
            set_anchor(doc, edit, DOMUI_ANCHOR_L | DOMUI_ANCHOR_R);
            {
                domui_widget* w = doc.find_by_id(edit);
                if (w) {
                    w->events.set("on_change", "tool_editor.prop_name");
                }
            }
        }
        y += row;
        {
            domui_widget_id lbl = add_widget(doc, DOMUI_WIDGET_STATIC_TEXT, pane_right, "label_x", 8, y, 20, 16);
            domui_widget_id edit = add_widget(doc, DOMUI_WIDGET_EDIT, pane_right, "edit_x", 72, y - 2, 60, 20);
            set_text_prop(doc.find_by_id(lbl), "X");
            {
                domui_widget* w = doc.find_by_id(edit);
                if (w) {
                    w->events.set("on_change", "tool_editor.prop_x");
                }
            }
        }
        y += row;
        {
            domui_widget_id lbl = add_widget(doc, DOMUI_WIDGET_STATIC_TEXT, pane_right, "label_y", 8, y, 20, 16);
            domui_widget_id edit = add_widget(doc, DOMUI_WIDGET_EDIT, pane_right, "edit_y", 72, y - 2, 60, 20);
            set_text_prop(doc.find_by_id(lbl), "Y");
            {
                domui_widget* w = doc.find_by_id(edit);
                if (w) {
                    w->events.set("on_change", "tool_editor.prop_y");
                }
            }
        }
        y += row;
        {
            domui_widget_id lbl = add_widget(doc, DOMUI_WIDGET_STATIC_TEXT, pane_right, "label_w", 8, y, 20, 16);
            domui_widget_id edit = add_widget(doc, DOMUI_WIDGET_EDIT, pane_right, "edit_w", 72, y - 2, 60, 20);
            set_text_prop(doc.find_by_id(lbl), "W");
            {
                domui_widget* w = doc.find_by_id(edit);
                if (w) {
                    w->events.set("on_change", "tool_editor.prop_w");
                }
            }
        }
        y += row;
        {
            domui_widget_id lbl = add_widget(doc, DOMUI_WIDGET_STATIC_TEXT, pane_right, "label_h", 8, y, 20, 16);
            domui_widget_id edit = add_widget(doc, DOMUI_WIDGET_EDIT, pane_right, "edit_h", 72, y - 2, 60, 20);
            set_text_prop(doc.find_by_id(lbl), "H");
            {
                domui_widget* w = doc.find_by_id(edit);
                if (w) {
                    w->events.set("on_change", "tool_editor.prop_h");
                }
            }
        }
    }

    return doc;
}

static domui_doc build_template_doc(void)
{
    domui_doc doc;
    domui_widget_id root;

    doc.meta.doc_name = domui_string("ui_doc_template_basic");
    doc.meta.doc_version = 2u;
    doc.meta.target_backends.push_back(domui_string("win32"));

    root = add_widget(doc, DOMUI_WIDGET_CONTAINER, 0u, "root", 0, 0, 800, 600);
    set_dock(doc, root, DOMUI_DOCK_FILL);
    {
        domui_widget_id label = add_widget(doc, DOMUI_WIDGET_STATIC_TEXT, root, "label_title", 16, 16, 200, 20);
        domui_widget_id button = add_widget(doc, DOMUI_WIDGET_BUTTON, root, "button_ok", 16, 48, 80, 24);
        domui_widget* w;
        w = doc.find_by_id(label);
        set_text_prop(w, "New UI Doc");
        w = doc.find_by_id(button);
        if (w) {
            set_text_prop(w, "OK");
        }
    }
    return doc;
}

static int save_doc(const domui_doc& doc, const char* path)
{
    domui_diag diag;
    if (!domui_doc_save_tlv(&doc, path, &diag)) {
        size_t i;
        for (i = 0u; i < diag.errors().size(); ++i) {
            fprintf(stderr, "error: %s\n", diag.errors()[i].message.c_str());
        }
        return 0;
    }
    return 1;
}

int main(void)
{
    const char* tool_doc = "tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv";
    const char* template_doc = "tools/tool_editor/ui/doc/ui_doc_template_basic.tlv";

    ensure_tool_editor_dirs();

    {
        domui_doc doc = build_tool_editor_ui_doc();
        if (!save_doc(doc, tool_doc)) {
            return 1;
        }
    }
    {
        domui_doc doc = build_template_doc();
        if (!save_doc(doc, template_doc)) {
            return 1;
        }
    }
    return 0;
}
