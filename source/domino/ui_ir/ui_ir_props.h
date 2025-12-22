/*
FILE: source/domino/ui_ir/ui_ir_props.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir props
RESPONSIBILITY: Deterministic property bag for UI IR (sorted by key).
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher, TLV I/O.
THREADING MODEL: Data-only; no internal synchronization.
ERROR MODEL: Return codes/booleans; no exceptions.
DETERMINISM: Keys stored and iterated in lexicographic byte order.
*/
#ifndef DOMINO_UI_IR_PROPS_H_INCLUDED
#define DOMINO_UI_IR_PROPS_H_INCLUDED

#include <vector>

#include "ui_ir_types.h"
#include "ui_ir_string.h"

typedef enum domui_value_type_e {
    DOMUI_VALUE_INT = 0,
    DOMUI_VALUE_UINT,
    DOMUI_VALUE_BOOL,
    DOMUI_VALUE_STRING,
    DOMUI_VALUE_VEC2I,
    DOMUI_VALUE_RECTI
} domui_value_type;

typedef struct domui_value {
    domui_value_type type;
    int v_int;
    domui_u32 v_uint;
    int v_bool;
    domui_vec2i v_vec2i;
    domui_recti v_recti;
    domui_string v_string;

    domui_value();
} domui_value;

domui_value domui_value_int(int v);
domui_value domui_value_uint(domui_u32 v);
domui_value domui_value_bool(int v);
domui_value domui_value_string(const domui_string& v);
domui_value domui_value_vec2i(domui_vec2i v);
domui_value domui_value_recti(domui_recti v);

typedef struct domui_prop_entry {
    domui_string key;
    domui_value value;
} domui_prop_entry;

class domui_props {
public:
    typedef std::vector<domui_prop_entry> list_type;

    domui_props();

    bool set(const domui_string& key, const domui_value& value);
    bool set(const char* key, const domui_value& value);

    bool get(const domui_string& key, domui_value* out_value) const;
    bool get(const char* key, domui_value* out_value) const;

    bool has(const domui_string& key) const;
    bool has(const char* key) const;

    bool erase(const domui_string& key);
    bool erase(const char* key);

    void clear();
    size_t size() const;

    const list_type& entries() const;
    void canonical_keys(std::vector<domui_string>& out_keys) const;

private:
    list_type m_entries;

    size_t find_index(const domui_string& key, bool* out_found) const;
};

#endif /* DOMINO_UI_IR_PROPS_H_INCLUDED */
