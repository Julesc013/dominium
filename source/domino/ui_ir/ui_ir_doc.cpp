/*
FILE: source/domino/ui_ir/ui_ir_doc.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir doc
RESPONSIBILITY: Implements canonical UI IR document model and ordering rules.
*/
#include "ui_ir_doc.h"

#include <algorithm>
#include <utility>

struct domui_child_sort {
    domui_u32 z;
    domui_widget_id id;
};

struct domui_child_sort_less {
    bool operator()(const domui_child_sort& a, const domui_child_sort& b) const
    {
        if (a.z != b.z) {
            return a.z < b.z;
        }
        return a.id < b.id;
    }
};

domui_events::domui_events()
    : m_entries()
{
}

size_t domui_events::find_index(const domui_string& key, bool* out_found) const
{
    size_t lo = 0u;
    size_t hi = m_entries.size();

    while (lo < hi) {
        size_t mid = (lo + hi) / 2u;
        int cmp = domui_string_compare(m_entries[mid].event_name, key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (out_found) {
        if (lo < m_entries.size() && domui_string_equal(m_entries[lo].event_name, key)) {
            *out_found = true;
        } else {
            *out_found = false;
        }
    }
    return lo;
}

bool domui_events::set(const domui_string& event_name, const domui_string& action_key)
{
    bool found = false;
    size_t idx = find_index(event_name, &found);
    if (found) {
        m_entries[idx].action_key = action_key;
        return true;
    }
    domui_event_binding entry;
    entry.event_name = event_name;
    entry.action_key = action_key;
    m_entries.insert(m_entries.begin() + (domui_events::list_type::difference_type)idx, entry);
    return true;
}

bool domui_events::set(const char* event_name, const char* action_key)
{
    return set(domui_string(event_name ? event_name : ""), domui_string(action_key ? action_key : ""));
}

bool domui_events::get(const domui_string& event_name, domui_string* out_action_key) const
{
    bool found = false;
    size_t idx = find_index(event_name, &found);
    if (!found) {
        return false;
    }
    if (out_action_key) {
        *out_action_key = m_entries[idx].action_key;
    }
    return true;
}

bool domui_events::get(const char* event_name, domui_string* out_action_key) const
{
    return get(domui_string(event_name ? event_name : ""), out_action_key);
}

bool domui_events::has(const domui_string& event_name) const
{
    bool found = false;
    (void)find_index(event_name, &found);
    return found;
}

bool domui_events::has(const char* event_name) const
{
    return has(domui_string(event_name ? event_name : ""));
}

bool domui_events::erase(const domui_string& event_name)
{
    bool found = false;
    size_t idx = find_index(event_name, &found);
    if (!found) {
        return false;
    }
    m_entries.erase(m_entries.begin() + (domui_events::list_type::difference_type)idx);
    return true;
}

bool domui_events::erase(const char* event_name)
{
    return erase(domui_string(event_name ? event_name : ""));
}

void domui_events::clear()
{
    m_entries.clear();
}

size_t domui_events::size() const
{
    return m_entries.size();
}

const domui_events::list_type& domui_events::entries() const
{
    return m_entries;
}

void domui_events::canonical_event_names(std::vector<domui_string>& out_names) const
{
    size_t i;
    out_names.clear();
    out_names.reserve(m_entries.size());
    for (i = 0u; i < m_entries.size(); ++i) {
        out_names.push_back(m_entries[i].event_name);
    }
}

domui_widget::domui_widget()
    : id(0u),
      type(DOMUI_WIDGET_CONTAINER),
      name(),
      parent_id(0u),
      z_order(0u),
      x(0),
      y(0),
      w(0),
      h(0),
      layout_mode(DOMUI_LAYOUT_ABSOLUTE),
      dock(DOMUI_DOCK_NONE),
      anchors(0u),
      margin(),
      padding(),
      min_w(0),
      min_h(0),
      max_w(-1),
      max_h(-1),
      props(),
      events()
{
    margin.left = 0;
    margin.right = 0;
    margin.top = 0;
    margin.bottom = 0;
    padding.left = 0;
    padding.right = 0;
    padding.top = 0;
    padding.bottom = 0;
}

void domui_widget::canonical_prop_order(std::vector<domui_string>& out_keys) const
{
    props.canonical_keys(out_keys);
}

void domui_widget::canonical_event_order(std::vector<domui_string>& out_names) const
{
    events.canonical_event_names(out_names);
}

domui_doc_meta::domui_doc_meta()
    : doc_version(1u),
      doc_name(),
      doc_guid(),
      target_backends(),
      target_tiers()
{
}

domui_doc::domui_doc()
    : meta(),
      m_widgets(),
      m_next_id(1u)
{
}

void domui_doc::clear()
{
    m_widgets.clear();
    m_next_id = 1u;
    meta = domui_doc_meta();
}

domui_widget_id domui_doc::create_widget(domui_widget_type type, domui_widget_id parent_id)
{
    domui_widget_id new_id;
    domui_widget w;
    if (parent_id != 0u && m_widgets.find(parent_id) == m_widgets.end()) {
        return 0u;
    }
    new_id = m_next_id;
    while (m_widgets.find(new_id) != m_widgets.end()) {
        new_id += 1u;
    }
    m_next_id = new_id + 1u;

    w.id = new_id;
    w.type = type;
    w.parent_id = parent_id;
    m_widgets.insert(std::make_pair(new_id, w));
    return new_id;
}

void domui_doc::collect_subtree_ids(domui_widget_id id, std::vector<domui_widget_id>& out_ids) const
{
    size_t i;
    std::vector<domui_widget_id> children;
    if (m_widgets.find(id) == m_widgets.end()) {
        return;
    }
    out_ids.push_back(id);
    enumerate_children(id, children);
    for (i = 0u; i < children.size(); ++i) {
        collect_subtree_ids(children[i], out_ids);
    }
}

bool domui_doc::delete_widget(domui_widget_id id)
{
    size_t i;
    std::vector<domui_widget_id> ids;
    if (m_widgets.find(id) == m_widgets.end()) {
        return false;
    }
    collect_subtree_ids(id, ids);
    for (i = 0u; i < ids.size(); ++i) {
        m_widgets.erase(ids[i]);
    }
    return true;
}

bool domui_doc::is_descendant(domui_widget_id ancestor_id, domui_widget_id candidate_id) const
{
    size_t guard = 0u;
    domui_widget_id cur = candidate_id;
    while (cur != 0u && guard <= m_widgets.size()) {
        if (cur == ancestor_id) {
            return true;
        }
        widget_map::const_iterator it = m_widgets.find(cur);
        if (it == m_widgets.end()) {
            break;
        }
        cur = it->second.parent_id;
        guard += 1u;
    }
    return false;
}

bool domui_doc::reparent_widget(domui_widget_id id, domui_widget_id new_parent_id, domui_u32 new_z_order)
{
    widget_map::iterator it = m_widgets.find(id);
    if (it == m_widgets.end()) {
        return false;
    }
    if (new_parent_id != 0u && m_widgets.find(new_parent_id) == m_widgets.end()) {
        return false;
    }
    if (new_parent_id == id || is_descendant(id, new_parent_id)) {
        return false;
    }
    it->second.parent_id = new_parent_id;
    it->second.z_order = new_z_order;
    return true;
}

bool domui_doc::set_rect(domui_widget_id id, int x, int y, int w, int h)
{
    widget_map::iterator it = m_widgets.find(id);
    if (it == m_widgets.end()) {
        return false;
    }
    it->second.x = x;
    it->second.y = y;
    it->second.w = w;
    it->second.h = h;
    return true;
}

bool domui_doc::set_layout(domui_widget_id id, domui_dock_mode dock, domui_u32 anchors, const domui_box& margin)
{
    widget_map::iterator it = m_widgets.find(id);
    if (it == m_widgets.end()) {
        return false;
    }
    it->second.dock = dock;
    it->second.anchors = anchors;
    it->second.margin = margin;
    return true;
}

bool domui_doc::set_padding(domui_widget_id id, const domui_box& padding)
{
    widget_map::iterator it = m_widgets.find(id);
    if (it == m_widgets.end()) {
        return false;
    }
    it->second.padding = padding;
    return true;
}

bool domui_doc::rename_widget(domui_widget_id id, const domui_string& name)
{
    widget_map::iterator it = m_widgets.find(id);
    if (it == m_widgets.end()) {
        return false;
    }
    it->second.name = name;
    return true;
}

domui_widget* domui_doc::find_by_id(domui_widget_id id)
{
    widget_map::iterator it = m_widgets.find(id);
    if (it == m_widgets.end()) {
        return 0;
    }
    return &it->second;
}

const domui_widget* domui_doc::find_by_id(domui_widget_id id) const
{
    widget_map::const_iterator it = m_widgets.find(id);
    if (it == m_widgets.end()) {
        return 0;
    }
    return &it->second;
}

domui_widget* domui_doc::find_by_name(const domui_string& name)
{
    widget_map::iterator it;
    for (it = m_widgets.begin(); it != m_widgets.end(); ++it) {
        if (domui_string_equal(it->second.name, name)) {
            return &it->second;
        }
    }
    return 0;
}

const domui_widget* domui_doc::find_by_name(const domui_string& name) const
{
    widget_map::const_iterator it;
    for (it = m_widgets.begin(); it != m_widgets.end(); ++it) {
        if (domui_string_equal(it->second.name, name)) {
            return &it->second;
        }
    }
    return 0;
}

void domui_doc::enumerate_children(domui_widget_id parent_id, std::vector<domui_widget_id>& out_ids) const
{
    widget_map::const_iterator it;
    std::vector<domui_child_sort> temp;
    out_ids.clear();
    for (it = m_widgets.begin(); it != m_widgets.end(); ++it) {
        if (it->second.parent_id == parent_id) {
            domui_child_sort entry;
            entry.z = it->second.z_order;
            entry.id = it->second.id;
            temp.push_back(entry);
        }
    }
    std::sort(temp.begin(), temp.end(), domui_child_sort_less());
    out_ids.reserve(temp.size());
    {
        size_t i;
        for (i = 0u; i < temp.size(); ++i) {
            out_ids.push_back(temp[i].id);
        }
    }
}

static void domui_traverse(const domui_doc& doc, domui_widget_id parent_id, std::vector<domui_widget_id>& out_ids)
{
    size_t i;
    std::vector<domui_widget_id> children;
    doc.enumerate_children(parent_id, children);
    for (i = 0u; i < children.size(); ++i) {
        out_ids.push_back(children[i]);
        domui_traverse(doc, children[i], out_ids);
    }
}

void domui_doc::canonical_widget_order(std::vector<domui_widget_id>& out_ids) const
{
    out_ids.clear();
    domui_traverse(*this, 0u, out_ids);
}

void domui_doc::recompute_next_id_from_widgets()
{
    widget_map::const_iterator it;
    domui_widget_id max_id = 0u;
    for (it = m_widgets.begin(); it != m_widgets.end(); ++it) {
        if (it->first > max_id) {
            max_id = it->first;
        }
    }
    m_next_id = max_id + 1u;
    if (m_next_id == 0u) {
        m_next_id = 1u;
    }
}

domui_widget_id domui_doc::next_id() const
{
    return m_next_id;
}

size_t domui_doc::widget_count() const
{
    return m_widgets.size();
}

bool domui_doc::insert_widget_with_id(const domui_widget& w)
{
    if (w.id == 0u) {
        return false;
    }
    if (m_widgets.find(w.id) != m_widgets.end()) {
        return false;
    }
    m_widgets.insert(std::make_pair(w.id, w));
    if (w.id >= m_next_id) {
        m_next_id = w.id + 1u;
        if (m_next_id == 0u) {
            m_next_id = 1u;
        }
    }
    return true;
}
