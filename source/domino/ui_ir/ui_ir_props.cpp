/*
FILE: source/domino/ui_ir/ui_ir_props.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir props
RESPONSIBILITY: Implements deterministic property bag for UI IR.
*/
#include "ui_ir_props.h"

domui_value::domui_value()
    : type(DOMUI_VALUE_INT),
      v_int(0),
      v_uint(0u),
      v_bool(0),
      v_vec2i(),
      v_recti(),
      v_string()
{
    v_vec2i.x = 0;
    v_vec2i.y = 0;
    v_recti.x = 0;
    v_recti.y = 0;
    v_recti.w = 0;
    v_recti.h = 0;
}

domui_value domui_value_int(int v)
{
    domui_value out;
    out.type = DOMUI_VALUE_INT;
    out.v_int = v;
    return out;
}

domui_value domui_value_uint(domui_u32 v)
{
    domui_value out;
    out.type = DOMUI_VALUE_UINT;
    out.v_uint = v;
    return out;
}

domui_value domui_value_bool(int v)
{
    domui_value out;
    out.type = DOMUI_VALUE_BOOL;
    out.v_bool = v ? 1 : 0;
    return out;
}

domui_value domui_value_string(const domui_string& v)
{
    domui_value out;
    out.type = DOMUI_VALUE_STRING;
    out.v_string = v;
    return out;
}

domui_value domui_value_vec2i(domui_vec2i v)
{
    domui_value out;
    out.type = DOMUI_VALUE_VEC2I;
    out.v_vec2i = v;
    return out;
}

domui_value domui_value_recti(domui_recti v)
{
    domui_value out;
    out.type = DOMUI_VALUE_RECTI;
    out.v_recti = v;
    return out;
}

domui_props::domui_props()
    : m_entries()
{
}

size_t domui_props::find_index(const domui_string& key, bool* out_found) const
{
    size_t lo = 0u;
    size_t hi = m_entries.size();

    while (lo < hi) {
        size_t mid = (lo + hi) / 2u;
        int cmp = domui_string_compare(m_entries[mid].key, key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (out_found) {
        if (lo < m_entries.size() && domui_string_equal(m_entries[lo].key, key)) {
            *out_found = true;
        } else {
            *out_found = false;
        }
    }
    return lo;
}

bool domui_props::set(const domui_string& key, const domui_value& value)
{
    bool found = false;
    size_t idx = find_index(key, &found);
    if (found) {
        m_entries[idx].value = value;
        return true;
    }
    domui_prop_entry entry;
    entry.key = key;
    entry.value = value;
    m_entries.insert(m_entries.begin() + (domui_props::list_type::difference_type)idx, entry);
    return true;
}

bool domui_props::set(const char* key, const domui_value& value)
{
    return set(domui_string(key ? key : ""), value);
}

bool domui_props::get(const domui_string& key, domui_value* out_value) const
{
    bool found = false;
    size_t idx = find_index(key, &found);
    if (!found) {
        return false;
    }
    if (out_value) {
        *out_value = m_entries[idx].value;
    }
    return true;
}

bool domui_props::get(const char* key, domui_value* out_value) const
{
    return get(domui_string(key ? key : ""), out_value);
}

bool domui_props::has(const domui_string& key) const
{
    bool found = false;
    (void)find_index(key, &found);
    return found;
}

bool domui_props::has(const char* key) const
{
    return has(domui_string(key ? key : ""));
}

bool domui_props::erase(const domui_string& key)
{
    bool found = false;
    size_t idx = find_index(key, &found);
    if (!found) {
        return false;
    }
    m_entries.erase(m_entries.begin() + (domui_props::list_type::difference_type)idx);
    return true;
}

bool domui_props::erase(const char* key)
{
    return erase(domui_string(key ? key : ""));
}

void domui_props::clear()
{
    m_entries.clear();
}

size_t domui_props::size() const
{
    return m_entries.size();
}

const domui_props::list_type& domui_props::entries() const
{
    return m_entries;
}

void domui_props::canonical_keys(std::vector<domui_string>& out_keys) const
{
    size_t i;
    out_keys.clear();
    out_keys.reserve(m_entries.size());
    for (i = 0u; i < m_entries.size(); ++i) {
        out_keys.push_back(m_entries[i].key);
    }
}
