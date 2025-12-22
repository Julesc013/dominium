/*
FILE: source/domino/ui_ir/ui_ir_legacy_import.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir legacy import
RESPONSIBILITY: Import legacy launcher UI schema TLV into UI IR.
*/
#include "ui_ir_legacy_import.h"

#include <stdio.h>

#include "dui/dui_schema_tlv.h"
#include "domino/io/container.h"

#include "ui_ir_fileio.h"

static const char* domui_event_name_for_widget(domui_widget_type t)
{
    switch (t) {
    case DOMUI_WIDGET_BUTTON:
        return "on_click";
    case DOMUI_WIDGET_CHECKBOX:
    case DOMUI_WIDGET_EDIT:
    case DOMUI_WIDGET_LISTBOX:
    case DOMUI_WIDGET_COMBOBOX:
    case DOMUI_WIDGET_SLIDER:
        return "on_change";
    default:
        break;
    }
    return "on_submit";
}

static domui_widget_type domui_map_kind_to_widget(u32 kind, domui_container_layout_mode* out_layout, domui_diag* diag)
{
    if (out_layout) {
        *out_layout = DOMUI_LAYOUT_ABSOLUTE;
    }
    switch ((dui_node_kind)kind) {
    case DUI_NODE_ROW:
        if (out_layout) *out_layout = DOMUI_LAYOUT_STACK_ROW;
        return DOMUI_WIDGET_CONTAINER;
    case DUI_NODE_COLUMN:
        if (out_layout) *out_layout = DOMUI_LAYOUT_STACK_COL;
        return DOMUI_WIDGET_CONTAINER;
    case DUI_NODE_STACK:
        if (diag) {
            diag->add_warning("legacy stack layout mapped to ABSOLUTE", 0u, "");
        }
        if (out_layout) *out_layout = DOMUI_LAYOUT_ABSOLUTE;
        return DOMUI_WIDGET_CONTAINER;
    case DUI_NODE_LABEL:
        return DOMUI_WIDGET_STATIC_TEXT;
    case DUI_NODE_BUTTON:
        return DOMUI_WIDGET_BUTTON;
    case DUI_NODE_CHECKBOX:
        return DOMUI_WIDGET_CHECKBOX;
    case DUI_NODE_LIST:
        return DOMUI_WIDGET_LISTBOX;
    case DUI_NODE_TEXT_FIELD:
        return DOMUI_WIDGET_EDIT;
    case DUI_NODE_PROGRESS:
        return DOMUI_WIDGET_PROGRESS;
    default:
        break;
    }
    if (diag) {
        diag->add_warning("legacy node kind unmapped; using CONTAINER", 0u, "");
    }
    return DOMUI_WIDGET_CONTAINER;
}

static void domui_store_legacy_props(domui_widget* w,
                                     const domui_string& text,
                                     u32 action_id,
                                     u32 bind_id,
                                     u32 flags,
                                     u64 required_caps,
                                     u32 visible_bind_id,
                                     u32 vmin,
                                     u32 vmax)
{
    if (!w) {
        return;
    }
    if (!text.empty()) {
        w->props.set("legacy.text", domui_value_string(text));
    }
    if (action_id != 0u) {
        w->props.set("legacy.action_id", domui_value_uint(action_id));
    }
    if (bind_id != 0u) {
        w->props.set("legacy.bind_id", domui_value_uint(bind_id));
    }
    if (flags != 0u) {
        w->props.set("legacy.flags", domui_value_uint(flags));
    }
    if (visible_bind_id != 0u) {
        w->props.set("legacy.visible_bind_id", domui_value_uint(visible_bind_id));
    }
    if (vmin != 0u) {
        w->props.set("legacy.validation_min", domui_value_uint(vmin));
    }
    if (vmax != 0u) {
        w->props.set("legacy.validation_max", domui_value_uint(vmax));
    }
    if (required_caps != 0u) {
        char buf[32];
        snprintf(buf, sizeof(buf), "0x%08X%08X",
                 (unsigned int)((required_caps >> 32u) & 0xFFFFFFFFu),
                 (unsigned int)(required_caps & 0xFFFFFFFFu));
        w->props.set("legacy.required_caps", domui_value_string(domui_string(buf)));
    }
}

static domui_widget_id domui_insert_or_remap(domui_doc* doc,
                                             const domui_widget& candidate,
                                             domui_diag* diag,
                                             domui_widget_id legacy_id)
{
    if (!doc) {
        return 0u;
    }
    if (legacy_id != 0u && doc->insert_widget_with_id(candidate)) {
        return legacy_id;
    }
    if (diag) {
        diag->add_warning("legacy id remapped", legacy_id, "");
    }
    {
        domui_widget_id new_id = doc->create_widget(candidate.type, candidate.parent_id);
        domui_widget* w = doc->find_by_id(new_id);
        if (!w) {
            return 0u;
        }
        w->type = candidate.type;
        w->name = candidate.name;
        w->parent_id = candidate.parent_id;
        w->z_order = candidate.z_order;
        w->x = candidate.x;
        w->y = candidate.y;
        w->w = candidate.w;
        w->h = candidate.h;
        w->layout_mode = candidate.layout_mode;
        w->dock = candidate.dock;
        w->anchors = candidate.anchors;
        w->margin = candidate.margin;
        w->padding = candidate.padding;
        w->min_w = candidate.min_w;
        w->min_h = candidate.min_h;
        w->max_w = candidate.max_w;
        w->max_h = candidate.max_h;
        w->props = candidate.props;
        w->events = candidate.events;
        return new_id;
    }
}

static domui_widget_id domui_import_node(domui_doc* doc,
                                         const unsigned char* tlv,
                                         u32 tlv_len,
                                         domui_widget_id parent_id,
                                         domui_diag* diag);

static void domui_import_children(domui_doc* doc,
                                  const unsigned char* tlv,
                                  u32 tlv_len,
                                  domui_widget_id parent_id,
                                  domui_diag* diag)
{
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* payload = 0;
    u32 payload_len = 0u;
    while (dtlv_tlv_next(tlv, tlv_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_NODE_V1) {
            (void)domui_import_node(doc, payload, payload_len, parent_id, diag);
        } else {
            if (diag) {
                diag->add_warning("legacy: unknown child tag", parent_id, "");
            }
        }
    }
}

static domui_widget_id domui_import_node(domui_doc* doc,
                                         const unsigned char* tlv,
                                         u32 tlv_len,
                                         domui_widget_id parent_id,
                                         domui_diag* diag)
{
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* payload = 0;
    u32 payload_len = 0u;

    u32 legacy_id = 0u;
    u32 kind = 0u;
    u32 action_id = 0u;
    u32 bind_id = 0u;
    u32 flags = 0u;
    u64 required_caps = 0u;
    u32 visible_bind_id = 0u;
    u32 vmin = 0u;
    u32 vmax = 0u;
    domui_string text;
    const unsigned char* children = 0;
    u32 children_len = 0u;

    while (dtlv_tlv_next(tlv, tlv_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_ID_U32) {
            if (payload_len >= 4u) {
                legacy_id = dtlv_le_read_u32(payload);
            }
        } else if (tag == DUI_TLV_KIND_U32) {
            if (payload_len >= 4u) {
                kind = dtlv_le_read_u32(payload);
            }
        } else if (tag == DUI_TLV_TEXT_UTF8) {
            text.set_bytes((const char*)payload, (size_t)payload_len);
        } else if (tag == DUI_TLV_ACTION_U32) {
            if (payload_len >= 4u) {
                action_id = dtlv_le_read_u32(payload);
            }
        } else if (tag == DUI_TLV_BIND_U32) {
            if (payload_len >= 4u) {
                bind_id = dtlv_le_read_u32(payload);
            }
        } else if (tag == DUI_TLV_FLAGS_U32) {
            if (payload_len >= 4u) {
                flags = dtlv_le_read_u32(payload);
            }
        } else if (tag == DUI_TLV_REQUIRED_CAPS_U64) {
            if (payload_len >= 8u) {
                required_caps = (u64)dtlv_le_read_u32(payload);
                required_caps |= ((u64)dtlv_le_read_u32(payload + 4u)) << 32u;
            }
        } else if (tag == DUI_TLV_VISIBLE_BIND_U32) {
            if (payload_len >= 4u) {
                visible_bind_id = dtlv_le_read_u32(payload);
            }
        } else if (tag == DUI_TLV_VALIDATION_V1) {
            u32 voff = 0u;
            u32 vtag = 0u;
            const unsigned char* vpayload = 0;
            u32 vlen = 0u;
            while (dtlv_tlv_next(payload, payload_len, &voff, &vtag, &vpayload, &vlen) == 0) {
                if (vtag == DUI_TLV_MIN_U32 && vlen >= 4u) {
                    vmin = dtlv_le_read_u32(vpayload);
                } else if (vtag == DUI_TLV_MAX_U32 && vlen >= 4u) {
                    vmax = dtlv_le_read_u32(vpayload);
                }
            }
        } else if (tag == DUI_TLV_CHILDREN_V1) {
            children = payload;
            children_len = payload_len;
        }
    }

    {
        domui_container_layout_mode layout_mode = DOMUI_LAYOUT_ABSOLUTE;
        domui_widget w;
        char name_buf[32];
        const char* event_name;
        char action_key[64];

        w.parent_id = parent_id;
        w.type = domui_map_kind_to_widget(kind, &layout_mode, diag);
        w.layout_mode = layout_mode;
        snprintf(name_buf, sizeof(name_buf), "legacy.%u", (unsigned int)legacy_id);
        w.name.set(name_buf);
        w.id = legacy_id;

        domui_store_legacy_props(&w, text, action_id, bind_id, flags, required_caps, visible_bind_id, vmin, vmax);
        w.props.set("legacy.kind", domui_value_uint(kind));

        if (action_id != 0u) {
            event_name = domui_event_name_for_widget(w.type);
            snprintf(action_key, sizeof(action_key), "legacy.%u.%s", (unsigned int)action_id, event_name);
            w.events.set(event_name, action_key);
        }

        {
            domui_widget_id new_id = domui_insert_or_remap(doc, w, diag, legacy_id);
            if (children && children_len != 0u && new_id != 0u) {
                domui_import_children(doc, children, children_len, new_id, diag);
            }
            return new_id;
        }
    }
}

static const unsigned char* domui_find_form_payload(const unsigned char* tlv, u32 tlv_len, u32* out_len)
{
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* payload = 0;
    u32 payload_len = 0u;

    if (out_len) {
        *out_len = 0u;
    }
    if (!tlv || tlv_len == 0u) {
        return 0;
    }
    off = 0u;
    while (dtlv_tlv_next(tlv, tlv_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_SCHEMA_V1) {
            return domui_find_form_payload(payload, payload_len, out_len);
        }
        if (tag == DUI_TLV_FORM_V1) {
            if (out_len) {
                *out_len = payload_len;
            }
            return payload;
        }
    }
    return 0;
}

bool domui_doc_import_legacy_launcher_tlv(domui_doc* out, const char* legacy_path, domui_diag* diag)
{
    std::vector<unsigned char> bytes;
    const unsigned char* form_payload = 0;
    u32 form_len = 0u;
    u32 off = 0u;
    u32 tag = 0u;
    const unsigned char* payload = 0;
    u32 payload_len = 0u;

    if (!out || !legacy_path) {
        if (diag) {
            diag->add_error("legacy import: invalid args", 0u, "");
        }
        return false;
    }

    out->clear();

    if (!domui_read_file_bytes(legacy_path, bytes, diag)) {
        return false;
    }
    if (bytes.size() < 8u) {
        if (diag) {
            diag->add_error("legacy import: file too small", 0u, legacy_path);
        }
        return false;
    }

    form_payload = domui_find_form_payload(&bytes[0], (u32)bytes.size(), &form_len);
    if (!form_payload || form_len == 0u) {
        if (diag) {
            diag->add_error("legacy import: missing form payload", 0u, legacy_path);
        }
        return false;
    }

    off = 0u;
    while (dtlv_tlv_next(form_payload, form_len, &off, &tag, &payload, &payload_len) == 0) {
        if (tag == DUI_TLV_NODE_V1) {
            (void)domui_import_node(out, payload, payload_len, 0u, diag);
        }
    }

    out->recompute_next_id_from_widgets();
    if (out->widget_count() == 0u) {
        if (diag) {
            diag->add_warning("legacy import: no widgets found", 0u, legacy_path);
        }
    }
    return true;
}
