/*
FILE: source/domino/dui/dui_schema_parse.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dui/schema_parse
RESPONSIBILITY: Implements internal TLV schema/state parsing helpers for DUI backends (skip-unknown; bounded outputs).
ALLOWED DEPENDENCIES: `include/dui/**`, `include/domino/**`, `source/domino/**` (within engine), and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Presentation-only; parsing is deterministic.
VERSIONING / ABI / DATA FORMAT NOTES: TLV is skip-unknown.
EXTENSION POINTS: Add new tags; old parsers skip unknown.
*/
#include "dui_schema_parse.h"

#include <stdlib.h>
#include <string.h>

#include "domino/io/container.h"

static u32 dui_read_u32_le(const unsigned char* p, u32 len, u32 def_v)
{
    if (!p || len < 4u) {
        return def_v;
    }
    return dtlv_le_read_u32(p);
}

static u64 dui_read_u64_le(const unsigned char* p, u32 len, u64 def_v)
{
    u64 v;
    if (!p || len < 8u) {
        return def_v;
    }
    v = (u64)dtlv_le_read_u32(p);
    v |= ((u64)dtlv_le_read_u32(p + 4u)) << 32u;
    return v;
}

static char* dui_dup_text(const unsigned char* p, u32 len)
{
    char* s;
    u32 n;
    if (!p || len == 0u) {
        return (char*)0;
    }
    n = len;
    s = (char*)malloc((size_t)(n + 1u));
    if (!s) {
        return (char*)0;
    }
    memcpy(s, p, (size_t)n);
    s[n] = '\0';
    return s;
}

static void dui_node_append_child(dui_schema_node* parent, dui_schema_node* child)
{
    dui_schema_node* cur;
    if (!parent || !child) {
        return;
    }
    if (!parent->first_child) {
        parent->first_child = child;
        return;
    }
    cur = parent->first_child;
    while (cur->next_sibling) {
        cur = cur->next_sibling;
    }
    cur->next_sibling = child;
}

static dui_schema_node* dui_parse_node_payload(const unsigned char* tlv, u32 tlv_len, dui_result* out_err);

static void dui_parse_validation(dui_schema_node* node, const unsigned char* tlv, u32 tlv_len)
{
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    if (!node || !tlv) {
        return;
    }
    off = 0u;
    while (dtlv_tlv_next(tlv, tlv_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_MIN_U32) {
            node->v_min = dui_read_u32_le(payload, payload_len, 0u);
        } else if (tag == DUI_TLV_MAX_U32) {
            node->v_max = dui_read_u32_le(payload, payload_len, 0u);
        }
    }
}

static dui_schema_node* dui_parse_children(const unsigned char* tlv, u32 tlv_len, dui_result* out_err)
{
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    dui_schema_node* first;
    dui_schema_node* last;

    first = (dui_schema_node*)0;
    last = (dui_schema_node*)0;

    if (!tlv) {
        return (dui_schema_node*)0;
    }

    off = 0u;
    while (dtlv_tlv_next(tlv, tlv_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_NODE_V1) {
            dui_schema_node* child = dui_parse_node_payload(payload, payload_len, out_err);
            if (!child) {
                continue;
            }
            if (!first) {
                first = child;
                last = child;
            } else {
                last->next_sibling = child;
                last = child;
            }
        }
    }
    return first;
}

static dui_schema_node* dui_parse_node_payload(const unsigned char* tlv, u32 tlv_len, dui_result* out_err)
{
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    dui_schema_node* node;

    node = (dui_schema_node*)malloc(sizeof(dui_schema_node));
    if (!node) {
        if (out_err) {
            *out_err = DUI_ERR;
        }
        return (dui_schema_node*)0;
    }
    memset(node, 0, sizeof(*node));
    node->v_min = 0u;
    node->v_max = 0u;

    off = 0u;
    while (dtlv_tlv_next(tlv, tlv_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_ID_U32) {
            node->id = dui_read_u32_le(payload, payload_len, 0u);
        } else if (tag == DUI_TLV_KIND_U32) {
            node->kind = dui_read_u32_le(payload, payload_len, 0u);
        } else if (tag == DUI_TLV_TEXT_UTF8) {
            if (node->text) {
                free(node->text);
            }
            node->text = dui_dup_text(payload, payload_len);
        } else if (tag == DUI_TLV_ACTION_U32) {
            node->action_id = dui_read_u32_le(payload, payload_len, 0u);
        } else if (tag == DUI_TLV_BIND_U32) {
            node->bind_id = dui_read_u32_le(payload, payload_len, 0u);
        } else if (tag == DUI_TLV_FLAGS_U32) {
            node->flags = dui_read_u32_le(payload, payload_len, 0u);
        } else if (tag == DUI_TLV_REQUIRED_CAPS_U64) {
            node->required_caps = dui_read_u64_le(payload, payload_len, 0u);
        } else if (tag == DUI_TLV_VISIBLE_BIND_U32) {
            node->visible_bind_id = dui_read_u32_le(payload, payload_len, 0u);
        } else if (tag == DUI_TLV_VALIDATION_V1) {
            dui_parse_validation(node, payload, payload_len);
        } else if (tag == DUI_TLV_CHILDREN_V1) {
            dui_schema_node* child_first = dui_parse_children(payload, payload_len, out_err);
            node->first_child = child_first;
        }
    }
    return node;
}

static dui_schema_node* dui_parse_form_first_root(const unsigned char* tlv, u32 tlv_len, dui_result* out_err)
{
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    if (!tlv) {
        return (dui_schema_node*)0;
    }
    off = 0u;
    while (dtlv_tlv_next(tlv, tlv_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_NODE_V1) {
            return dui_parse_node_payload(payload, payload_len, out_err);
        }
    }
    if (out_err) {
        *out_err = DUI_ERR_BAD_DESC;
    }
    return (dui_schema_node*)0;
}

static dui_schema_node* dui_parse_schema_first_form_root(const unsigned char* tlv, u32 tlv_len, dui_result* out_err)
{
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    if (!tlv) {
        return (dui_schema_node*)0;
    }
    off = 0u;
    while (dtlv_tlv_next(tlv, tlv_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_FORM_V1) {
            return dui_parse_form_first_root(payload, payload_len, out_err);
        }
    }
    if (out_err) {
        *out_err = DUI_ERR_BAD_DESC;
    }
    return (dui_schema_node*)0;
}

dui_schema_node* dui_schema_parse_first_form_root(const void* schema_tlv, u32 schema_len, dui_result* out_err)
{
    const unsigned char* tlv;
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;

    if (out_err) {
        *out_err = DUI_OK;
    }
    if (!schema_tlv || schema_len == 0u) {
        if (out_err) {
            *out_err = DUI_ERR_BAD_DESC;
        }
        return (dui_schema_node*)0;
    }

    tlv = (const unsigned char*)schema_tlv;

    /* Accept either:
     * - a TLV stream containing SCHEMA_V1, or
     * - a nested schema payload stream containing FORM_V1 directly.
     */
    off = 0u;
    while (dtlv_tlv_next(tlv, schema_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_SCHEMA_V1) {
            return dui_parse_schema_first_form_root(payload, payload_len, out_err);
        }
    }

    return dui_parse_schema_first_form_root(tlv, schema_len, out_err);
}

void dui_schema_free(dui_schema_node* n)
{
    dui_schema_node* child;
    if (!n) {
        return;
    }
    child = n->first_child;
    while (child) {
        dui_schema_node* next = child->next_sibling;
        dui_schema_free(child);
        child = next;
    }
    if (n->text) {
        free(n->text);
        n->text = (char*)0;
    }
    free(n);
}

dui_schema_node* dui_schema_find_by_id(dui_schema_node* root, u32 id)
{
    dui_schema_node* child;
    if (!root) {
        return (dui_schema_node*)0;
    }
    if (root->id == id) {
        return root;
    }
    child = root->first_child;
    while (child) {
        dui_schema_node* found = dui_schema_find_by_id(child, id);
        if (found) {
            return found;
        }
        child = child->next_sibling;
    }
    return (dui_schema_node*)0;
}

static i32 dui_pref_h_for_kind(u32 kind)
{
    switch ((dui_node_kind)kind) {
    case DUI_NODE_LABEL: return 20;
    case DUI_NODE_BUTTON: return 24;
    case DUI_NODE_CHECKBOX: return 24;
    case DUI_NODE_TEXT_FIELD: return 24;
    case DUI_NODE_PROGRESS: return 18;
    case DUI_NODE_LIST: return 140;
    default: break;
    }
    return 24;
}

static int dui_is_layout_kind(u32 kind)
{
    return (kind == (u32)DUI_NODE_ROW) || (kind == (u32)DUI_NODE_COLUMN) || (kind == (u32)DUI_NODE_STACK);
}

static void dui_layout_children_column(dui_schema_node* parent, i32 x, i32 y, i32 w, i32 h)
{
    const i32 margin = 8;
    const i32 spacing = 6;
    u32 child_count;
    u32 flex_count;
    i32 fixed_total;
    i32 avail;
    dui_schema_node* child;
    i32 cursor_y;

    child_count = 0u;
    flex_count = 0u;
    fixed_total = 0;

    child = parent ? parent->first_child : (dui_schema_node*)0;
    while (child) {
        if (child->flags & DUI_NODE_FLAG_FLEX) {
            flex_count += 1u;
        } else if (dui_is_layout_kind(child->kind)) {
            fixed_total += 0;
        } else {
            fixed_total += dui_pref_h_for_kind(child->kind);
        }
        child_count += 1u;
        child = child->next_sibling;
    }

    avail = h - margin - margin - (i32)((child_count > 0u) ? (spacing * (i32)(child_count - 1u)) : 0);
    if (avail < 0) {
        avail = 0;
    }

    cursor_y = y + margin;
    child = parent ? parent->first_child : (dui_schema_node*)0;
    while (child) {
        i32 ch = 0;
        if (child->flags & DUI_NODE_FLAG_FLEX) {
            ch = (flex_count > 0u) ? (avail - fixed_total) / (i32)flex_count : 0;
            if (ch < dui_pref_h_for_kind(child->kind)) {
                ch = dui_pref_h_for_kind(child->kind);
            }
        } else if (dui_is_layout_kind(child->kind)) {
            ch = (avail - fixed_total);
            if (ch < 0) {
                ch = 0;
            }
        } else {
            ch = dui_pref_h_for_kind(child->kind);
        }

        child->x = x + margin;
        child->y = cursor_y;
        child->w = w - margin - margin;
        child->h = ch;

        if (dui_is_layout_kind(child->kind)) {
            dui_schema_layout(child, child->x, child->y, child->w, child->h);
        }

        cursor_y += ch + spacing;
        child = child->next_sibling;
    }
}

static void dui_layout_children_row(dui_schema_node* parent, i32 x, i32 y, i32 w, i32 h)
{
    const i32 margin = 8;
    const i32 spacing = 6;
    u32 child_count;
    dui_schema_node* child;
    i32 inner_x;
    i32 inner_y;
    i32 inner_w;
    i32 inner_h;
    i32 each_w;
    u32 idx;

    child_count = 0u;
    child = parent ? parent->first_child : (dui_schema_node*)0;
    while (child) {
        child_count += 1u;
        child = child->next_sibling;
    }

    inner_x = x + margin;
    inner_y = y + margin;
    inner_w = w - margin - margin;
    inner_h = h - margin - margin;
    if (inner_w < 0) inner_w = 0;
    if (inner_h < 0) inner_h = 0;

    if (child_count == 0u) {
        return;
    }

    each_w = (inner_w - (i32)(spacing * (i32)(child_count - 1u))) / (i32)child_count;
    if (each_w < 0) {
        each_w = 0;
    }

    idx = 0u;
    child = parent->first_child;
    while (child) {
        child->x = inner_x + (i32)idx * (each_w + spacing);
        child->y = inner_y;
        child->w = each_w;
        child->h = inner_h;

        if (dui_is_layout_kind(child->kind)) {
            dui_schema_layout(child, child->x, child->y, child->w, child->h);
        }

        idx += 1u;
        child = child->next_sibling;
    }
}

static void dui_layout_children_stack(dui_schema_node* parent, i32 x, i32 y, i32 w, i32 h)
{
    dui_schema_node* child;
    child = parent ? parent->first_child : (dui_schema_node*)0;
    while (child) {
        child->x = x;
        child->y = y;
        child->w = w;
        child->h = h;
        if (dui_is_layout_kind(child->kind)) {
            dui_schema_layout(child, child->x, child->y, child->w, child->h);
        }
        child = child->next_sibling;
    }
}

void dui_schema_layout(dui_schema_node* root, i32 x, i32 y, i32 w, i32 h)
{
    if (!root) {
        return;
    }
    root->x = x;
    root->y = y;
    root->w = w;
    root->h = h;

    if (!root->first_child) {
        return;
    }

    if (root->kind == (u32)DUI_NODE_ROW) {
        dui_layout_children_row(root, x, y, w, h);
    } else if (root->kind == (u32)DUI_NODE_STACK) {
        dui_layout_children_stack(root, x, y, w, h);
    } else {
        /* default to column */
        dui_layout_children_column(root, x, y, w, h);
    }
}

static int dui_state_find_value_record(const unsigned char* tlv,
                                       u32 tlv_len,
                                       u32 bind_id,
                                       const unsigned char** out_payload,
                                       u32* out_payload_len)
{
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;

    if (!tlv || !out_payload || !out_payload_len) {
        return 0;
    }

    /* Expect STATE_V1 -> VALUE_V1 records */
    off = 0u;
    while (dtlv_tlv_next(tlv, tlv_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_STATE_V1) {
            u32 off2 = 0u;
            u32 tag2;
            const unsigned char* payload2;
            u32 payload2_len;
            while (dtlv_tlv_next(payload, payload_len, &off2, &tag2, &payload2, &payload2_len) == 0) {
                if (tag2 == DUI_TLV_VALUE_V1) {
                    /* Scan inside the value record for BIND_U32. */
                    u32 off3 = 0u;
                    u32 tag3;
                    const unsigned char* payload3;
                    u32 payload3_len;
                    u32 found_bind = 0u;
                    while (dtlv_tlv_next(payload2, payload2_len, &off3, &tag3, &payload3, &payload3_len) == 0) {
                        if (tag3 == DUI_TLV_BIND_U32) {
                            found_bind = dui_read_u32_le(payload3, payload3_len, 0u);
                            break;
                        }
                    }
                    if (found_bind == bind_id) {
                        *out_payload = payload2;
                        *out_payload_len = payload2_len;
                        return 1;
                    }
                }
            }
        }
    }
    return 0;
}

static int dui_state_value_type(const unsigned char* value_rec, u32 value_len, u32* out_type)
{
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    if (!value_rec || !out_type) {
        return 0;
    }
    off = 0u;
    while (dtlv_tlv_next(value_rec, value_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_VALUE_TYPE_U32) {
            *out_type = dui_read_u32_le(payload, payload_len, 0u);
            return 1;
        }
    }
    return 0;
}

int dui_state_get_u32(const void* state_tlv, u32 state_len, u32 bind_id, u32* out_v)
{
    const unsigned char* value_rec;
    u32 value_len;
    u32 t;
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    if (!out_v) {
        return 0;
    }
    *out_v = 0u;
    if (!state_tlv || state_len == 0u) {
        return 0;
    }
    if (!dui_state_find_value_record((const unsigned char*)state_tlv, state_len, bind_id, &value_rec, &value_len)) {
        return 0;
    }
    t = 0u;
    (void)dui_state_value_type(value_rec, value_len, &t);
    if (t != (u32)DUI_VALUE_U32 && t != (u32)DUI_VALUE_BOOL) {
        return 0;
    }
    off = 0u;
    while (dtlv_tlv_next(value_rec, value_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_VALUE_U32) {
            *out_v = dui_read_u32_le(payload, payload_len, 0u);
            return 1;
        }
    }
    return 0;
}

int dui_state_get_i32(const void* state_tlv, u32 state_len, u32 bind_id, i32* out_v)
{
    const unsigned char* value_rec;
    u32 value_len;
    u32 t;
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    if (!out_v) {
        return 0;
    }
    *out_v = 0;
    if (!state_tlv || state_len == 0u) {
        return 0;
    }
    if (!dui_state_find_value_record((const unsigned char*)state_tlv, state_len, bind_id, &value_rec, &value_len)) {
        return 0;
    }
    t = 0u;
    (void)dui_state_value_type(value_rec, value_len, &t);
    if (t != (u32)DUI_VALUE_I32) {
        return 0;
    }
    off = 0u;
    while (dtlv_tlv_next(value_rec, value_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_VALUE_I32) {
            *out_v = (i32)dui_read_u32_le(payload, payload_len, 0u);
            return 1;
        }
    }
    return 0;
}

int dui_state_get_u64(const void* state_tlv, u32 state_len, u32 bind_id, u64* out_v)
{
    const unsigned char* value_rec;
    u32 value_len;
    u32 t;
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    if (!out_v) {
        return 0;
    }
    *out_v = 0u;
    if (!state_tlv || state_len == 0u) {
        return 0;
    }
    if (!dui_state_find_value_record((const unsigned char*)state_tlv, state_len, bind_id, &value_rec, &value_len)) {
        return 0;
    }
    t = 0u;
    (void)dui_state_value_type(value_rec, value_len, &t);
    if (t != (u32)DUI_VALUE_U64) {
        return 0;
    }
    off = 0u;
    while (dtlv_tlv_next(value_rec, value_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_VALUE_U64) {
            *out_v = dui_read_u64_le(payload, payload_len, 0u);
            return 1;
        }
    }
    return 0;
}

int dui_state_get_text(const void* state_tlv, u32 state_len, u32 bind_id, char* out_text, u32 out_cap, u32* out_len)
{
    const unsigned char* value_rec;
    u32 value_len;
    u32 t;
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    u32 n;

    if (out_len) {
        *out_len = 0u;
    }
    if (out_text && out_cap > 0u) {
        out_text[0] = '\0';
    }
    if (!out_text || out_cap == 0u || !out_len) {
        return 0;
    }
    if (!state_tlv || state_len == 0u) {
        return 0;
    }
    if (!dui_state_find_value_record((const unsigned char*)state_tlv, state_len, bind_id, &value_rec, &value_len)) {
        return 0;
    }
    t = 0u;
    (void)dui_state_value_type(value_rec, value_len, &t);
    if (t != (u32)DUI_VALUE_TEXT) {
        return 0;
    }
    off = 0u;
    while (dtlv_tlv_next(value_rec, value_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_VALUE_UTF8) {
            n = payload_len;
            if (n >= out_cap) {
                n = out_cap - 1u;
            }
            memcpy(out_text, payload, (size_t)n);
            out_text[n] = '\0';
            *out_len = n;
            return 1;
        }
    }
    return 0;
}

static int dui_state_find_list_record(const unsigned char* value_rec, u32 value_len, const unsigned char** out_list, u32* out_list_len)
{
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    if (!value_rec || !out_list || !out_list_len) {
        return 0;
    }
    off = 0u;
    while (dtlv_tlv_next(value_rec, value_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_LIST_V1) {
            *out_list = payload;
            *out_list_len = payload_len;
            return 1;
        }
    }
    return 0;
}

int dui_state_get_list_selected_item_id(const void* state_tlv, u32 state_len, u32 bind_id, u32* out_item_id)
{
    const unsigned char* value_rec;
    u32 value_len;
    u32 t;
    const unsigned char* list_rec;
    u32 list_len;
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;

    if (!out_item_id) {
        return 0;
    }
    *out_item_id = 0u;
    if (!state_tlv || state_len == 0u) {
        return 0;
    }
    if (!dui_state_find_value_record((const unsigned char*)state_tlv, state_len, bind_id, &value_rec, &value_len)) {
        return 0;
    }
    t = 0u;
    (void)dui_state_value_type(value_rec, value_len, &t);
    if (t != (u32)DUI_VALUE_LIST) {
        return 0;
    }
    if (!dui_state_find_list_record(value_rec, value_len, &list_rec, &list_len)) {
        return 0;
    }
    off = 0u;
    while (dtlv_tlv_next(list_rec, list_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_LIST_SELECTED_U32) {
            *out_item_id = dui_read_u32_le(payload, payload_len, 0u);
            return 1;
        }
    }
    return 0;
}

int dui_state_get_list_item_count(const void* state_tlv, u32 state_len, u32 bind_id, u32* out_count)
{
    const unsigned char* value_rec;
    u32 value_len;
    u32 t;
    const unsigned char* list_rec;
    u32 list_len;
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    u32 count;

    if (!out_count) {
        return 0;
    }
    *out_count = 0u;
    if (!state_tlv || state_len == 0u) {
        return 0;
    }
    if (!dui_state_find_value_record((const unsigned char*)state_tlv, state_len, bind_id, &value_rec, &value_len)) {
        return 0;
    }
    t = 0u;
    (void)dui_state_value_type(value_rec, value_len, &t);
    if (t != (u32)DUI_VALUE_LIST) {
        return 0;
    }
    if (!dui_state_find_list_record(value_rec, value_len, &list_rec, &list_len)) {
        return 0;
    }
    count = 0u;
    off = 0u;
    while (dtlv_tlv_next(list_rec, list_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_LIST_ITEM_V1) {
            count += 1u;
        }
    }
    *out_count = count;
    return 1;
}

int dui_state_get_list_item_at(const void* state_tlv,
                               u32 state_len,
                               u32 bind_id,
                               u32 index,
                               u32* out_item_id,
                               char* out_text,
                               u32 out_cap,
                               u32* out_len)
{
    const unsigned char* value_rec;
    u32 value_len;
    u32 t;
    const unsigned char* list_rec;
    u32 list_len;
    u32 off;
    u32 tag;
    const unsigned char* payload;
    u32 payload_len;
    u32 cur;

    if (out_item_id) {
        *out_item_id = 0u;
    }
    if (out_len) {
        *out_len = 0u;
    }
    if (out_text && out_cap > 0u) {
        out_text[0] = '\0';
    }

    if (!out_item_id || !out_text || out_cap == 0u || !out_len) {
        return 0;
    }
    if (!state_tlv || state_len == 0u) {
        return 0;
    }
    if (!dui_state_find_value_record((const unsigned char*)state_tlv, state_len, bind_id, &value_rec, &value_len)) {
        return 0;
    }
    t = 0u;
    (void)dui_state_value_type(value_rec, value_len, &t);
    if (t != (u32)DUI_VALUE_LIST) {
        return 0;
    }
    if (!dui_state_find_list_record(value_rec, value_len, &list_rec, &list_len)) {
        return 0;
    }

    cur = 0u;
    off = 0u;
    while (dtlv_tlv_next(list_rec, list_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_LIST_ITEM_V1) {
            if (cur == index) {
                u32 off2 = 0u;
                u32 tag2;
                const unsigned char* payload2;
                u32 payload2_len;
                u32 item_id = 0u;
                u32 have_text = 0u;

                while (dtlv_tlv_next(payload, payload_len, &off2, &tag2, &payload2, &payload2_len) == 0) {
                    if (tag2 == DUI_TLV_ITEM_ID_U32) {
                        item_id = dui_read_u32_le(payload2, payload2_len, 0u);
                    } else if (tag2 == DUI_TLV_ITEM_TEXT_UTF8) {
                        u32 n = payload2_len;
                        if (n >= out_cap) {
                            n = out_cap - 1u;
                        }
                        memcpy(out_text, payload2, (size_t)n);
                        out_text[n] = '\0';
                        *out_len = n;
                        have_text = 1u;
                    }
                }
                *out_item_id = item_id;
                return have_text ? 1 : 0;
            }
            cur += 1u;
        }
    }
    return 0;
}
