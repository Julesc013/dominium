/*
FILE: source/domino/ui_ir/ui_ir_tlv.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir tlv
RESPONSIBILITY: TLV load/save for UI IR documents (DTLV container).
*/
#include "ui_ir_tlv.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "domino/io/container.h"

#include "ui_ir_fileio.h"
#include "ui_ir_json.h"

#define DOMUI_TAG(a,b,c,d) ((domui_u32)((domui_u32)(a) << 24u) | ((domui_u32)(b) << 16u) | ((domui_u32)(c) << 8u) | ((domui_u32)(d)))

static const domui_u32 DOMUI_CHUNK_META     = DOMUI_TAG('M','E','T','A');
static const domui_u32 DOMUI_CHUNK_WIDGETS  = DOMUI_TAG('W','I','D','G');
static const domui_u32 DOMUI_CHUNK_RESOURCES= DOMUI_TAG('R','S','R','C');
static const domui_u32 DOMUI_CHUNK_EVENTS   = DOMUI_TAG('E','V','N','T');
static const domui_u32 DOMUI_CHUNK_ORDERING = DOMUI_TAG('O','R','D','R');

static const domui_u32 DOMUI_TLV_DOC_VERSION   = DOMUI_TAG('V','E','R','S');
static const domui_u32 DOMUI_TLV_DOC_NAME      = DOMUI_TAG('N','A','M','E');
static const domui_u32 DOMUI_TLV_DOC_GUID      = DOMUI_TAG('G','U','I','D');
static const domui_u32 DOMUI_TLV_TARGET_BACKENDS = DOMUI_TAG('B','A','C','K');
static const domui_u32 DOMUI_TLV_TARGET_TIERS  = DOMUI_TAG('T','I','E','R');
static const domui_u32 DOMUI_TLV_LIST_V1       = DOMUI_TAG('L','I','S','T');
static const domui_u32 DOMUI_TLV_ITEM_UTF8     = DOMUI_TAG('I','T','E','M');

static const domui_u32 DOMUI_TLV_WIDGET_V1     = DOMUI_TAG('W','I','D','1');
static const domui_u32 DOMUI_TLV_ID_U32        = DOMUI_TAG('I','D','_','_');
static const domui_u32 DOMUI_TLV_TYPE_U32      = DOMUI_TAG('T','Y','P','E');
static const domui_u32 DOMUI_TLV_NAME_UTF8     = DOMUI_TAG('N','A','M','E');
static const domui_u32 DOMUI_TLV_PARENT_U32    = DOMUI_TAG('P','A','R','_');
static const domui_u32 DOMUI_TLV_Z_ORDER_U32   = DOMUI_TAG('Z','O','R','D');
static const domui_u32 DOMUI_TLV_RECT_I32      = DOMUI_TAG('R','E','C','T');
static const domui_u32 DOMUI_TLV_LAYOUT_U32    = DOMUI_TAG('L','A','Y','O');
static const domui_u32 DOMUI_TLV_DOCK_U32      = DOMUI_TAG('D','O','C','K');
static const domui_u32 DOMUI_TLV_ANCHOR_U32    = DOMUI_TAG('A','N','C','H');
static const domui_u32 DOMUI_TLV_MARGIN_I32    = DOMUI_TAG('M','A','R','G');
static const domui_u32 DOMUI_TLV_PADDING_I32   = DOMUI_TAG('P','A','D','D');
static const domui_u32 DOMUI_TLV_MIN_W_I32     = DOMUI_TAG('M','I','N','W');
static const domui_u32 DOMUI_TLV_MIN_H_I32     = DOMUI_TAG('M','I','N','H');
static const domui_u32 DOMUI_TLV_MAX_W_I32     = DOMUI_TAG('M','A','X','W');
static const domui_u32 DOMUI_TLV_MAX_H_I32     = DOMUI_TAG('M','A','X','H');
static const domui_u32 DOMUI_TLV_PROPS_V1      = DOMUI_TAG('P','R','O','P');
static const domui_u32 DOMUI_TLV_PROP_V1       = DOMUI_TAG('P','R','P','1');
static const domui_u32 DOMUI_TLV_PROP_KEY      = DOMUI_TAG('P','K','E','Y');
static const domui_u32 DOMUI_TLV_PROP_TYPE     = DOMUI_TAG('P','T','Y','P');
static const domui_u32 DOMUI_TLV_PROP_I32      = DOMUI_TAG('P','I','N','T');
static const domui_u32 DOMUI_TLV_PROP_U32      = DOMUI_TAG('P','U','N','T');
static const domui_u32 DOMUI_TLV_PROP_BOOL     = DOMUI_TAG('P','B','O','L');
static const domui_u32 DOMUI_TLV_PROP_STR      = DOMUI_TAG('P','S','T','R');
static const domui_u32 DOMUI_TLV_PROP_VEC2I    = DOMUI_TAG('P','V','2','I');
static const domui_u32 DOMUI_TLV_PROP_RECTI    = DOMUI_TAG('P','R','C','T');
static const domui_u32 DOMUI_TLV_EVENTS_V1     = DOMUI_TAG('E','V','T','S');
static const domui_u32 DOMUI_TLV_EVENT_V1      = DOMUI_TAG('E','V','T','1');
static const domui_u32 DOMUI_TLV_EVENT_NAME    = DOMUI_TAG('E','N','A','M');
static const domui_u32 DOMUI_TLV_ACTION_KEY    = DOMUI_TAG('A','C','T','N');

static bool domui_buf_write(std::vector<unsigned char>& out, const void* data, size_t len)
{
    const unsigned char* p = (const unsigned char*)data;
    if (len == 0u) {
        return true;
    }
    if (!p) {
        return false;
    }
    out.insert(out.end(), p, p + len);
    return true;
}

static bool domui_buf_write_u32(std::vector<unsigned char>& out, domui_u32 v)
{
    unsigned char tmp[4];
    dtlv_le_write_u32(tmp, v);
    return domui_buf_write(out, tmp, sizeof(tmp));
}

static bool domui_buf_write_i32(std::vector<unsigned char>& out, int v)
{
    return domui_buf_write_u32(out, (domui_u32)v);
}

static bool domui_buf_write_tlv(std::vector<unsigned char>& out, domui_u32 tag, const void* payload, size_t payload_len)
{
    if (!domui_buf_write_u32(out, tag)) {
        return false;
    }
    if (!domui_buf_write_u32(out, (domui_u32)payload_len)) {
        return false;
    }
    if (payload_len != 0u) {
        return domui_buf_write(out, payload, payload_len);
    }
    return true;
}

static bool domui_buf_write_string(std::vector<unsigned char>& out, domui_u32 tag, const domui_string& s)
{
    const std::string& v = s.str();
    return domui_buf_write_tlv(out, tag, v.c_str(), v.size());
}

static bool domui_buf_write_rect(std::vector<unsigned char>& out, domui_u32 tag, int x, int y, int w, int h)
{
    unsigned char tmp[16];
    dtlv_le_write_u32(tmp + 0u, (domui_u32)x);
    dtlv_le_write_u32(tmp + 4u, (domui_u32)y);
    dtlv_le_write_u32(tmp + 8u, (domui_u32)w);
    dtlv_le_write_u32(tmp + 12u, (domui_u32)h);
    return domui_buf_write_tlv(out, tag, tmp, sizeof(tmp));
}

static bool domui_buf_write_box(std::vector<unsigned char>& out, domui_u32 tag, const domui_box& b)
{
    unsigned char tmp[16];
    dtlv_le_write_u32(tmp + 0u, (domui_u32)b.left);
    dtlv_le_write_u32(tmp + 4u, (domui_u32)b.right);
    dtlv_le_write_u32(tmp + 8u, (domui_u32)b.top);
    dtlv_le_write_u32(tmp + 12u, (domui_u32)b.bottom);
    return domui_buf_write_tlv(out, tag, tmp, sizeof(tmp));
}

static bool domui_write_meta_payload(const domui_doc& doc, std::vector<unsigned char>& out)
{
    std::vector<unsigned char> list_payload;
    domui_u32 doc_version = doc.meta.doc_version;
    if (doc_version < 2u) {
        doc_version = 2u;
    }
    domui_buf_write_u32(out, DOMUI_TLV_DOC_VERSION);
    domui_buf_write_u32(out, 4u);
    domui_buf_write_u32(out, doc_version);

    domui_buf_write_string(out, DOMUI_TLV_DOC_NAME, doc.meta.doc_name);

    if (!doc.meta.doc_guid.empty()) {
        domui_buf_write_string(out, DOMUI_TLV_DOC_GUID, doc.meta.doc_guid);
    }

    list_payload.clear();
    if (!doc.meta.target_backends.empty()) {
        size_t i;
        for (i = 0u; i < doc.meta.target_backends.size(); ++i) {
            domui_buf_write_string(list_payload, DOMUI_TLV_ITEM_UTF8, doc.meta.target_backends[i]);
        }
    }
    domui_buf_write_tlv(out, DOMUI_TLV_TARGET_BACKENDS, list_payload.empty() ? 0 : &list_payload[0], list_payload.size());

    list_payload.clear();
    if (!doc.meta.target_tiers.empty()) {
        size_t i;
        for (i = 0u; i < doc.meta.target_tiers.size(); ++i) {
            domui_buf_write_string(list_payload, DOMUI_TLV_ITEM_UTF8, doc.meta.target_tiers[i]);
        }
    }
    domui_buf_write_tlv(out, DOMUI_TLV_TARGET_TIERS, list_payload.empty() ? 0 : &list_payload[0], list_payload.size());
    return true;
}

static bool domui_write_props_payload(const domui_props& props, std::vector<unsigned char>& out)
{
    size_t i;
    const domui_props::list_type& entries = props.entries();
    for (i = 0u; i < entries.size(); ++i) {
        std::vector<unsigned char> prop_payload;
        const domui_prop_entry& e = entries[i];
        domui_buf_write_string(prop_payload, DOMUI_TLV_PROP_KEY, e.key);
        domui_buf_write_u32(prop_payload, DOMUI_TLV_PROP_TYPE);
        domui_buf_write_u32(prop_payload, 4u);
        domui_buf_write_u32(prop_payload, (domui_u32)e.value.type);

        switch (e.value.type) {
        case DOMUI_VALUE_INT:
            {
                std::vector<unsigned char> v;
                domui_buf_write_i32(v, e.value.v_int);
                domui_buf_write_tlv(prop_payload, DOMUI_TLV_PROP_I32, &v[0], v.size());
            }
            break;
        case DOMUI_VALUE_UINT:
            {
                std::vector<unsigned char> v;
                domui_buf_write_u32(v, e.value.v_uint);
                domui_buf_write_tlv(prop_payload, DOMUI_TLV_PROP_U32, &v[0], v.size());
            }
            break;
        case DOMUI_VALUE_BOOL:
            {
                std::vector<unsigned char> v;
                domui_buf_write_u32(v, (domui_u32)(e.value.v_bool ? 1 : 0));
                domui_buf_write_tlv(prop_payload, DOMUI_TLV_PROP_BOOL, &v[0], v.size());
            }
            break;
        case DOMUI_VALUE_STRING:
            domui_buf_write_string(prop_payload, DOMUI_TLV_PROP_STR, e.value.v_string);
            break;
        case DOMUI_VALUE_VEC2I:
            {
                unsigned char tmp[8];
                dtlv_le_write_u32(tmp + 0u, (domui_u32)e.value.v_vec2i.x);
                dtlv_le_write_u32(tmp + 4u, (domui_u32)e.value.v_vec2i.y);
                domui_buf_write_tlv(prop_payload, DOMUI_TLV_PROP_VEC2I, tmp, sizeof(tmp));
            }
            break;
        case DOMUI_VALUE_RECTI:
            {
                unsigned char tmp[16];
                dtlv_le_write_u32(tmp + 0u, (domui_u32)e.value.v_recti.x);
                dtlv_le_write_u32(tmp + 4u, (domui_u32)e.value.v_recti.y);
                dtlv_le_write_u32(tmp + 8u, (domui_u32)e.value.v_recti.w);
                dtlv_le_write_u32(tmp + 12u, (domui_u32)e.value.v_recti.h);
                domui_buf_write_tlv(prop_payload, DOMUI_TLV_PROP_RECTI, tmp, sizeof(tmp));
            }
            break;
        default:
            break;
        }

        domui_buf_write_tlv(out, DOMUI_TLV_PROP_V1, prop_payload.empty() ? 0 : &prop_payload[0], prop_payload.size());
    }
    return true;
}

static bool domui_write_events_payload(const domui_events& events, std::vector<unsigned char>& out)
{
    size_t i;
    const domui_events::list_type& entries = events.entries();
    for (i = 0u; i < entries.size(); ++i) {
        std::vector<unsigned char> ev_payload;
        domui_buf_write_string(ev_payload, DOMUI_TLV_EVENT_NAME, entries[i].event_name);
        domui_buf_write_string(ev_payload, DOMUI_TLV_ACTION_KEY, entries[i].action_key);
        domui_buf_write_tlv(out, DOMUI_TLV_EVENT_V1, ev_payload.empty() ? 0 : &ev_payload[0], ev_payload.size());
    }
    return true;
}

static bool domui_write_widgets_payload(const domui_doc& doc, std::vector<unsigned char>& out)
{
    std::vector<domui_widget_id> order;
    size_t i;

    doc.canonical_widget_order(order);
    for (i = 0u; i < order.size(); ++i) {
        const domui_widget* w = doc.find_by_id(order[i]);
        std::vector<unsigned char> payload;
        std::vector<unsigned char> props_payload;
        std::vector<unsigned char> events_payload;
        if (!w) {
            continue;
        }
        domui_buf_write_u32(payload, DOMUI_TLV_ID_U32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_u32(payload, w->id);

        domui_buf_write_u32(payload, DOMUI_TLV_TYPE_U32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_u32(payload, (domui_u32)w->type);

        domui_buf_write_string(payload, DOMUI_TLV_NAME_UTF8, w->name);

        domui_buf_write_u32(payload, DOMUI_TLV_PARENT_U32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_u32(payload, w->parent_id);

        domui_buf_write_u32(payload, DOMUI_TLV_Z_ORDER_U32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_u32(payload, w->z_order);

        domui_buf_write_rect(payload, DOMUI_TLV_RECT_I32, w->x, w->y, w->w, w->h);

        domui_buf_write_u32(payload, DOMUI_TLV_LAYOUT_U32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_u32(payload, (domui_u32)w->layout_mode);

        domui_buf_write_u32(payload, DOMUI_TLV_DOCK_U32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_u32(payload, (domui_u32)w->dock);

        domui_buf_write_u32(payload, DOMUI_TLV_ANCHOR_U32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_u32(payload, w->anchors);

        domui_buf_write_box(payload, DOMUI_TLV_MARGIN_I32, w->margin);
        domui_buf_write_box(payload, DOMUI_TLV_PADDING_I32, w->padding);

        domui_buf_write_u32(payload, DOMUI_TLV_MIN_W_I32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_i32(payload, w->min_w);

        domui_buf_write_u32(payload, DOMUI_TLV_MIN_H_I32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_i32(payload, w->min_h);

        domui_buf_write_u32(payload, DOMUI_TLV_MAX_W_I32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_i32(payload, w->max_w);

        domui_buf_write_u32(payload, DOMUI_TLV_MAX_H_I32);
        domui_buf_write_u32(payload, 4u);
        domui_buf_write_i32(payload, w->max_h);

        props_payload.clear();
        domui_write_props_payload(w->props, props_payload);
        domui_buf_write_tlv(payload, DOMUI_TLV_PROPS_V1, props_payload.empty() ? 0 : &props_payload[0], props_payload.size());

        events_payload.clear();
        domui_write_events_payload(w->events, events_payload);
        domui_buf_write_tlv(payload, DOMUI_TLV_EVENTS_V1, events_payload.empty() ? 0 : &events_payload[0], events_payload.size());

        domui_buf_write_tlv(out, DOMUI_TLV_WIDGET_V1, payload.empty() ? 0 : &payload[0], payload.size());
    }
    return true;
}

static bool domui_read_u32(const unsigned char* payload, u32 payload_len, domui_u32* out_v)
{
    if (!out_v) {
        return false;
    }
    *out_v = 0u;
    if (!payload || payload_len < 4u) {
        return false;
    }
    *out_v = dtlv_le_read_u32(payload);
    return true;
}

static bool domui_read_i32(const unsigned char* payload, u32 payload_len, int* out_v)
{
    domui_u32 v;
    if (!out_v) {
        return false;
    }
    *out_v = 0;
    if (!domui_read_u32(payload, payload_len, &v)) {
        return false;
    }
    *out_v = (int)v;
    return true;
}

static bool domui_read_rect(const unsigned char* payload, u32 payload_len, domui_recti* out_rect)
{
    if (!out_rect || !payload || payload_len < 16u) {
        return false;
    }
    out_rect->x = (int)dtlv_le_read_u32(payload + 0u);
    out_rect->y = (int)dtlv_le_read_u32(payload + 4u);
    out_rect->w = (int)dtlv_le_read_u32(payload + 8u);
    out_rect->h = (int)dtlv_le_read_u32(payload + 12u);
    return true;
}

static bool domui_read_box(const unsigned char* payload, u32 payload_len, domui_box* out_box)
{
    if (!out_box || !payload || payload_len < 16u) {
        return false;
    }
    out_box->left = (int)dtlv_le_read_u32(payload + 0u);
    out_box->right = (int)dtlv_le_read_u32(payload + 4u);
    out_box->top = (int)dtlv_le_read_u32(payload + 8u);
    out_box->bottom = (int)dtlv_le_read_u32(payload + 12u);
    return true;
}

static void domui_parse_list_strings(const unsigned char* payload, u32 payload_len, domui_string_list& out_list)
{
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* p = 0;
    u32 len = 0u;
    out_list.clear();
    while (dtlv_tlv_next(payload, payload_len, &off, &tag, &p, &len) == 0) {
        if (tag == DOMUI_TLV_ITEM_UTF8) {
            domui_string s;
            s.set_bytes((const char*)p, (size_t)len);
            out_list.push_back(s);
        }
    }
}

static bool domui_parse_meta(const unsigned char* payload, u32 payload_len, domui_doc& out_doc, domui_diag* diag)
{
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* p = 0;
    u32 len = 0u;
    domui_u32 v = 0u;

    while (dtlv_tlv_next(payload, payload_len, &off, &tag, &p, &len) == 0) {
        if (tag == DOMUI_TLV_DOC_VERSION) {
            if (domui_read_u32(p, len, &v)) {
                out_doc.meta.doc_version = v;
            }
        } else if (tag == DOMUI_TLV_DOC_NAME) {
            out_doc.meta.doc_name.set_bytes((const char*)p, (size_t)len);
        } else if (tag == DOMUI_TLV_DOC_GUID) {
            out_doc.meta.doc_guid.set_bytes((const char*)p, (size_t)len);
        } else if (tag == DOMUI_TLV_TARGET_BACKENDS) {
            domui_parse_list_strings(p, len, out_doc.meta.target_backends);
        } else if (tag == DOMUI_TLV_TARGET_TIERS) {
            domui_parse_list_strings(p, len, out_doc.meta.target_tiers);
        } else {
            if (diag) {
                diag->add_warning("tlv: unknown meta tag", 0u, "");
            }
        }
    }
    return true;
}

static void domui_parse_prop_record(const unsigned char* payload, u32 payload_len, domui_props& props, domui_diag* diag)
{
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* p = 0;
    u32 len = 0u;
    domui_string key;
    domui_value_type type = DOMUI_VALUE_INT;
    domui_value value;
    int have_value = 0;
    int have_type = 0;

    while (dtlv_tlv_next(payload, payload_len, &off, &tag, &p, &len) == 0) {
        if (tag == DOMUI_TLV_PROP_KEY) {
            key.set_bytes((const char*)p, (size_t)len);
        } else if (tag == DOMUI_TLV_PROP_TYPE) {
            domui_u32 t = 0u;
            if (domui_read_u32(p, len, &t)) {
                type = (domui_value_type)t;
                have_type = 1;
            }
        } else if (tag == DOMUI_TLV_PROP_I32) {
            int v = 0;
            if (domui_read_i32(p, len, &v)) {
                value = domui_value_int(v);
                have_value = 1;
            }
        } else if (tag == DOMUI_TLV_PROP_U32) {
            domui_u32 v = 0u;
            if (domui_read_u32(p, len, &v)) {
                value = domui_value_uint(v);
                have_value = 1;
            }
        } else if (tag == DOMUI_TLV_PROP_BOOL) {
            domui_u32 v = 0u;
            if (domui_read_u32(p, len, &v)) {
                value = domui_value_bool(v ? 1 : 0);
                have_value = 1;
            }
        } else if (tag == DOMUI_TLV_PROP_STR) {
            domui_string s;
            s.set_bytes((const char*)p, (size_t)len);
            value = domui_value_string(s);
            have_value = 1;
        } else if (tag == DOMUI_TLV_PROP_VEC2I) {
            if (len >= 8u) {
                domui_vec2i v2;
                v2.x = (int)dtlv_le_read_u32(p + 0u);
                v2.y = (int)dtlv_le_read_u32(p + 4u);
                value = domui_value_vec2i(v2);
                have_value = 1;
            }
        } else if (tag == DOMUI_TLV_PROP_RECTI) {
            if (len >= 16u) {
                domui_recti r;
                r.x = (int)dtlv_le_read_u32(p + 0u);
                r.y = (int)dtlv_le_read_u32(p + 4u);
                r.w = (int)dtlv_le_read_u32(p + 8u);
                r.h = (int)dtlv_le_read_u32(p + 12u);
                value = domui_value_recti(r);
                have_value = 1;
            }
        }
    }

    if (!key.empty() && have_value) {
        if (have_type) {
            value.type = type;
        }
        props.set(key, value);
    } else if (diag) {
        diag->add_warning("tlv: invalid prop record", 0u, "");
    }
}

static void domui_parse_event_record(const unsigned char* payload, u32 payload_len, domui_events& events)
{
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* p = 0;
    u32 len = 0u;
    domui_string name;
    domui_string action;
    while (dtlv_tlv_next(payload, payload_len, &off, &tag, &p, &len) == 0) {
        if (tag == DOMUI_TLV_EVENT_NAME) {
            name.set_bytes((const char*)p, (size_t)len);
        } else if (tag == DOMUI_TLV_ACTION_KEY) {
            action.set_bytes((const char*)p, (size_t)len);
        }
    }
    if (!name.empty()) {
        events.set(name, action);
    }
}

static void domui_parse_widget_record(const unsigned char* payload, u32 payload_len, domui_doc& doc, domui_diag* diag)
{
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* p = 0;
    u32 len = 0u;
    domui_widget w;
    domui_u32 tmp_u32 = 0u;
    int tmp_i32 = 0;

    while (dtlv_tlv_next(payload, payload_len, &off, &tag, &p, &len) == 0) {
        if (tag == DOMUI_TLV_ID_U32) {
            if (domui_read_u32(p, len, &tmp_u32)) {
                w.id = tmp_u32;
            }
        } else if (tag == DOMUI_TLV_TYPE_U32) {
            if (domui_read_u32(p, len, &tmp_u32)) {
                w.type = (domui_widget_type)tmp_u32;
            }
        } else if (tag == DOMUI_TLV_NAME_UTF8) {
            w.name.set_bytes((const char*)p, (size_t)len);
        } else if (tag == DOMUI_TLV_PARENT_U32) {
            if (domui_read_u32(p, len, &tmp_u32)) {
                w.parent_id = tmp_u32;
            }
        } else if (tag == DOMUI_TLV_Z_ORDER_U32) {
            if (domui_read_u32(p, len, &tmp_u32)) {
                w.z_order = tmp_u32;
            }
        } else if (tag == DOMUI_TLV_RECT_I32) {
            domui_recti r;
            if (domui_read_rect(p, len, &r)) {
                w.x = r.x;
                w.y = r.y;
                w.w = r.w;
                w.h = r.h;
            }
        } else if (tag == DOMUI_TLV_LAYOUT_U32) {
            if (domui_read_u32(p, len, &tmp_u32)) {
                w.layout_mode = (domui_container_layout_mode)tmp_u32;
            }
        } else if (tag == DOMUI_TLV_DOCK_U32) {
            if (domui_read_u32(p, len, &tmp_u32)) {
                w.dock = (domui_dock_mode)tmp_u32;
            }
        } else if (tag == DOMUI_TLV_ANCHOR_U32) {
            if (domui_read_u32(p, len, &tmp_u32)) {
                w.anchors = tmp_u32;
            }
        } else if (tag == DOMUI_TLV_MARGIN_I32) {
            domui_box b;
            if (domui_read_box(p, len, &b)) {
                w.margin = b;
            }
        } else if (tag == DOMUI_TLV_PADDING_I32) {
            domui_box b;
            if (domui_read_box(p, len, &b)) {
                w.padding = b;
            }
        } else if (tag == DOMUI_TLV_MIN_W_I32) {
            if (domui_read_i32(p, len, &tmp_i32)) {
                w.min_w = tmp_i32;
            }
        } else if (tag == DOMUI_TLV_MIN_H_I32) {
            if (domui_read_i32(p, len, &tmp_i32)) {
                w.min_h = tmp_i32;
            }
        } else if (tag == DOMUI_TLV_MAX_W_I32) {
            if (domui_read_i32(p, len, &tmp_i32)) {
                w.max_w = tmp_i32;
            }
        } else if (tag == DOMUI_TLV_MAX_H_I32) {
            if (domui_read_i32(p, len, &tmp_i32)) {
                w.max_h = tmp_i32;
            }
        } else if (tag == DOMUI_TLV_PROPS_V1) {
            u32 poff = 0u;
            u32 ptag = 0u;
            const unsigned char* pp = 0;
            u32 plen = 0u;
            while (dtlv_tlv_next(p, len, &poff, &ptag, &pp, &plen) == 0) {
                if (ptag == DOMUI_TLV_PROP_V1) {
                    domui_parse_prop_record(pp, plen, w.props, diag);
                }
            }
        } else if (tag == DOMUI_TLV_EVENTS_V1) {
            u32 eoff = 0u;
            u32 etag = 0u;
            const unsigned char* ep = 0;
            u32 elen = 0u;
            while (dtlv_tlv_next(p, len, &eoff, &etag, &ep, &elen) == 0) {
                if (etag == DOMUI_TLV_EVENT_V1) {
                    domui_parse_event_record(ep, elen, w.events);
                }
            }
        }
    }

    if (w.id == 0u) {
        if (diag) {
            diag->add_warning("tlv: widget id missing; allocating new", 0u, "");
        }
        w.id = doc.next_id();
    }
    if (!doc.insert_widget_with_id(w)) {
        if (diag) {
            diag->add_warning("tlv: duplicate widget id; allocating new", w.id, "");
        }
        w.id = doc.next_id();
        (void)doc.insert_widget_with_id(w);
    }
}

static bool domui_parse_widgets(const unsigned char* payload, u32 payload_len, domui_doc& doc, domui_diag* diag)
{
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* p = 0;
    u32 len = 0u;
    while (dtlv_tlv_next(payload, payload_len, &off, &tag, &p, &len) == 0) {
        if (tag == DOMUI_TLV_WIDGET_V1) {
            domui_parse_widget_record(p, len, doc, diag);
        } else if (diag) {
            diag->add_warning("tlv: unknown widget tag", 0u, "");
        }
    }
    return true;
}

static std::string domui_json_path_from_tlv(const char* path)
{
    std::string p = path ? path : "";
    size_t pos = p.rfind('.');
    if (pos != std::string::npos) {
        p = p.substr(0u, pos);
    }
    p += ".json";
    return p;
}

static void domui_apply_default_prop(domui_widget* w, const char* key, const domui_value& value)
{
    if (!w || !key) {
        return;
    }
    if (!w->props.has(key)) {
        w->props.set(key, value);
    }
}

static void domui_migrate_v1_to_v2(domui_doc& doc, domui_diag* diag)
{
    std::vector<domui_widget_id> order;
    size_t i;

    doc.meta.doc_version = 2u;

    doc.canonical_widget_order(order);
    for (i = 0u; i < order.size(); ++i) {
        domui_widget* w = doc.find_by_id(order[i]);
        if (!w) {
            continue;
        }
        switch (w->type) {
        case DOMUI_WIDGET_SPLITTER:
            domui_apply_default_prop(w, "splitter.orientation", domui_value_string(domui_string("v")));
            domui_apply_default_prop(w, "splitter.pos", domui_value_int(-1));
            domui_apply_default_prop(w, "splitter.thickness", domui_value_int(4));
            domui_apply_default_prop(w, "splitter.min_a", domui_value_int(0));
            domui_apply_default_prop(w, "splitter.min_b", domui_value_int(0));
            break;
        case DOMUI_WIDGET_TABS:
            domui_apply_default_prop(w, "tabs.selected_index", domui_value_int(0));
            domui_apply_default_prop(w, "tabs.placement", domui_value_string(domui_string("top")));
            break;
        case DOMUI_WIDGET_TAB_PAGE:
            domui_apply_default_prop(w, "tab.title", domui_value_string(domui_string("")));
            domui_apply_default_prop(w, "tab.enabled", domui_value_bool(1));
            break;
        case DOMUI_WIDGET_SCROLLPANEL:
            domui_apply_default_prop(w, "scroll.h_enabled", domui_value_bool(1));
            domui_apply_default_prop(w, "scroll.v_enabled", domui_value_bool(1));
            domui_apply_default_prop(w, "scroll.x", domui_value_int(0));
            domui_apply_default_prop(w, "scroll.y", domui_value_int(0));
            break;
        default:
            break;
        }
    }

    if (diag) {
        diag->add_warning("tlv: migrated doc version 1 -> 2", 0u, "");
    }
}

static void domui_apply_migrations(domui_doc& doc, domui_diag* diag)
{
    if (doc.meta.doc_version < 2u) {
        domui_migrate_v1_to_v2(doc, diag);
    }
}

bool domui_doc_save_tlv(const domui_doc* doc, const char* path, domui_diag* diag)
{
    std::vector<unsigned char> meta_payload;
    std::vector<unsigned char> widgets_payload;
    std::vector<unsigned char> file_bytes;
    dtlv_writer writer;
    u32 total_size = 0u;
    u64 total_size64 = 0u;
    u32 entry_count = 2u;
    u32 file_size = 0u;

    if (!doc || !path) {
        if (diag) {
            diag->add_error("save tlv: invalid args", 0u, "");
        }
        return false;
    }

    meta_payload.clear();
    widgets_payload.clear();
    domui_write_meta_payload(*doc, meta_payload);
    domui_write_widgets_payload(*doc, widgets_payload);

    if (meta_payload.size() > 0xFFFFFFFFu || widgets_payload.size() > 0xFFFFFFFFu) {
        if (diag) {
            diag->add_error("save tlv: payload too large", 0u, "");
        }
        return false;
    }
    total_size64 = (u64)DTLV_HEADER_SIZE_V1;
    total_size64 += (u64)meta_payload.size();
    total_size64 += (u64)widgets_payload.size();
    total_size64 += (u64)entry_count * (u64)DTLV_DIR_ENTRY_SIZE_V1;
    if (total_size64 > (u64)0xFFFFFFFFu) {
        if (diag) {
            diag->add_error("save tlv: total size too large", 0u, "");
        }
        return false;
    }
    total_size = (u32)total_size64;

    file_bytes.resize((size_t)total_size);
    dtlv_writer_init(&writer);
    if (dtlv_writer_init_mem(&writer, &file_bytes[0], total_size) != 0) {
        if (diag) {
            diag->add_error("save tlv: writer init failed", 0u, "");
        }
        dtlv_writer_dispose(&writer);
        return false;
    }

    if (dtlv_writer_begin_chunk(&writer, DOMUI_CHUNK_META, 2u, 0u) != 0) {
        if (diag) {
            diag->add_error("save tlv: begin meta chunk failed", 0u, "");
        }
        dtlv_writer_dispose(&writer);
        return false;
    }
    if (!meta_payload.empty()) {
        if (dtlv_writer_write(&writer, &meta_payload[0], (u32)meta_payload.size()) != 0) {
            if (diag) {
                diag->add_error("save tlv: write meta failed", 0u, "");
            }
            dtlv_writer_dispose(&writer);
            return false;
        }
    }
    if (dtlv_writer_end_chunk(&writer) != 0) {
        if (diag) {
            diag->add_error("save tlv: end meta chunk failed", 0u, "");
        }
        dtlv_writer_dispose(&writer);
        return false;
    }

    if (dtlv_writer_begin_chunk(&writer, DOMUI_CHUNK_WIDGETS, 2u, 0u) != 0) {
        if (diag) {
            diag->add_error("save tlv: begin widgets chunk failed", 0u, "");
        }
        dtlv_writer_dispose(&writer);
        return false;
    }
    if (!widgets_payload.empty()) {
        if (dtlv_writer_write(&writer, &widgets_payload[0], (u32)widgets_payload.size()) != 0) {
            if (diag) {
                diag->add_error("save tlv: write widgets failed", 0u, "");
            }
            dtlv_writer_dispose(&writer);
            return false;
        }
    }
    if (dtlv_writer_end_chunk(&writer) != 0) {
        if (diag) {
            diag->add_error("save tlv: end widgets chunk failed", 0u, "");
        }
        dtlv_writer_dispose(&writer);
        return false;
    }

    if (dtlv_writer_finalize(&writer) != 0) {
        if (diag) {
            diag->add_error("save tlv: finalize failed", 0u, "");
        }
        dtlv_writer_dispose(&writer);
        return false;
    }

    file_size = dtlv_writer_mem_size(&writer);
    if (file_size == 0u || file_size > (u32)file_bytes.size()) {
        if (diag) {
            diag->add_error("save tlv: writer size invalid", 0u, "");
        }
        dtlv_writer_dispose(&writer);
        return false;
    }
    if (!domui_atomic_write_file(path, &file_bytes[0], (size_t)file_size, diag)) {
        dtlv_writer_dispose(&writer);
        return false;
    }
    dtlv_writer_dispose(&writer);

    {
#if DOMUI_ENABLE_JSON_MIRROR
        std::string json_path = domui_json_path_from_tlv(path);
        if (!domui_doc_save_json_mirror(doc, json_path.c_str(), diag)) {
            if (diag) {
                diag->add_warning("save tlv: json mirror failed", 0u, json_path.c_str());
            }
            return false;
        }
#else
        (void)doc;
#endif
    }
    return true;
}

bool domui_doc_load_tlv(domui_doc* out, const char* path, domui_diag* diag)
{
    std::vector<unsigned char> bytes;
    dtlv_reader reader;
    const dtlv_dir_entry* meta_entry = 0;
    const dtlv_dir_entry* widgets_entry = 0;
    unsigned char* meta_payload = 0;
    unsigned char* widgets_payload = 0;
    u32 meta_len = 0u;
    u32 widgets_len = 0u;

    if (!out || !path) {
        if (diag) {
            diag->add_error("load tlv: invalid args", 0u, "");
        }
        return false;
    }

    dtlv_reader_init(&reader);
    out->clear();

    if (!domui_read_file_bytes(path, bytes, diag)) {
        return false;
    }
    if (dtlv_reader_init_mem(&reader, &bytes[0], (u64)bytes.size()) != 0) {
        if (diag) {
            diag->add_error("load tlv: bad container", 0u, path);
        }
        dtlv_reader_dispose(&reader);
        return false;
    }

    meta_entry = dtlv_reader_find_first(&reader, DOMUI_CHUNK_META, 2u);
    if (!meta_entry) {
        meta_entry = dtlv_reader_find_first(&reader, DOMUI_CHUNK_META, 1u);
    }
    widgets_entry = dtlv_reader_find_first(&reader, DOMUI_CHUNK_WIDGETS, 2u);
    if (!widgets_entry) {
        widgets_entry = dtlv_reader_find_first(&reader, DOMUI_CHUNK_WIDGETS, 1u);
    }
    if (!meta_entry || !widgets_entry) {
        if (diag) {
            diag->add_error("load tlv: missing required chunks", 0u, path);
        }
        dtlv_reader_dispose(&reader);
        return false;
    }

    if (dtlv_reader_read_chunk_alloc(&reader, meta_entry, &meta_payload, &meta_len) != 0) {
        dtlv_reader_dispose(&reader);
        return false;
    }
    if (dtlv_reader_read_chunk_alloc(&reader, widgets_entry, &widgets_payload, &widgets_len) != 0) {
        if (meta_payload) {
            free(meta_payload);
        }
        dtlv_reader_dispose(&reader);
        return false;
    }

    domui_parse_meta(meta_payload, meta_len, *out, diag);
    domui_parse_widgets(widgets_payload, widgets_len, *out, diag);
    domui_apply_migrations(*out, diag);
    out->recompute_next_id_from_widgets();

    if (meta_payload) {
        free(meta_payload);
    }
    if (widgets_payload) {
        free(widgets_payload);
    }
    dtlv_reader_dispose(&reader);

    return true;
}
