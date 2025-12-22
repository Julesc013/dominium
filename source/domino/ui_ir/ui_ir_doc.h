/*
FILE: source/domino/ui_ir/ui_ir_doc.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir doc
RESPONSIBILITY: Canonical UI IR document model and deterministic ordering rules.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher, TLV I/O.
THREADING MODEL: Data-only; no internal synchronization.
ERROR MODEL: Return codes/booleans; no exceptions.
DETERMINISM: Canonical ordering by (z_order, id) and lexicographic keys.
*/
#ifndef DOMINO_UI_IR_DOC_H_INCLUDED
#define DOMINO_UI_IR_DOC_H_INCLUDED

#include <map>
#include <vector>

#include "ui_ir_props.h"

typedef struct domui_event_binding {
    domui_string event_name;
    domui_string action_key;
} domui_event_binding;

class domui_events {
public:
    typedef std::vector<domui_event_binding> list_type;

    domui_events();

    bool set(const domui_string& event_name, const domui_string& action_key);
    bool set(const char* event_name, const char* action_key);

    bool get(const domui_string& event_name, domui_string* out_action_key) const;
    bool get(const char* event_name, domui_string* out_action_key) const;

    bool has(const domui_string& event_name) const;
    bool has(const char* event_name) const;

    bool erase(const domui_string& event_name);
    bool erase(const char* event_name);

    void clear();
    size_t size() const;

    const list_type& entries() const;
    void canonical_event_names(std::vector<domui_string>& out_names) const;

private:
    list_type m_entries;

    size_t find_index(const domui_string& key, bool* out_found) const;
};

typedef struct domui_widget {
    domui_widget_id id;
    domui_widget_type type;
    domui_string name;
    domui_widget_id parent_id;
    domui_u32 z_order;

    int x;
    int y;
    int w;
    int h;

    domui_dock_mode dock;
    domui_u32 anchors;
    domui_box margin;
    domui_box padding;

    int min_w;
    int min_h;
    int max_w;
    int max_h;

    domui_props props;
    domui_events events;

    domui_widget();

    void canonical_prop_order(std::vector<domui_string>& out_keys) const;
    void canonical_event_order(std::vector<domui_string>& out_names) const;
} domui_widget;

typedef struct domui_doc_meta {
    domui_u32 doc_version;
    domui_string doc_name;
    domui_string doc_guid;
    domui_string_list target_backends;
    domui_string_list target_tiers;

    domui_doc_meta();
} domui_doc_meta;

class domui_doc {
public:
    domui_doc();

    domui_widget_id create_widget(domui_widget_type type, domui_widget_id parent_id);
    bool delete_widget(domui_widget_id id);
    bool reparent_widget(domui_widget_id id, domui_widget_id new_parent_id, domui_u32 new_z_order);

    bool set_rect(domui_widget_id id, int x, int y, int w, int h);
    bool set_layout(domui_widget_id id, domui_dock_mode dock, domui_u32 anchors, const domui_box& margin);
    bool set_padding(domui_widget_id id, const domui_box& padding);
    bool rename_widget(domui_widget_id id, const domui_string& name);

    domui_widget* find_by_id(domui_widget_id id);
    const domui_widget* find_by_id(domui_widget_id id) const;

    domui_widget* find_by_name(const domui_string& name);
    const domui_widget* find_by_name(const domui_string& name) const;

    void enumerate_children(domui_widget_id parent_id, std::vector<domui_widget_id>& out_ids) const;
    void canonical_widget_order(std::vector<domui_widget_id>& out_ids) const;

    void recompute_next_id_from_widgets();
    domui_widget_id next_id() const;

    domui_doc_meta meta;

private:
    typedef std::map<domui_widget_id, domui_widget> widget_map;

    widget_map m_widgets;
    domui_widget_id m_next_id;

    void collect_subtree_ids(domui_widget_id id, std::vector<domui_widget_id>& out_ids) const;
    bool is_descendant(domui_widget_id ancestor_id, domui_widget_id candidate_id) const;
};

#endif /* DOMINO_UI_IR_DOC_H_INCLUDED */
