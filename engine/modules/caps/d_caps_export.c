/*
FILE: source/domino/caps/d_caps_export.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / caps/d_caps_export
RESPONSIBILITY: Writes capability exports to DTLV containers (capabilities.tlv).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Output is deterministic for the same selection and backend state.
VERSIONING / ABI / DATA FORMAT NOTES: DTLV container v1; see `docs/specs/SPEC_CONTAINER_TLV.md`.
EXTENSION POINTS: Extend by adding TLV tags or new chunk versions.
*/
#include "domino/caps.h"

#include "domino/io/container.h"
#include "domino/sys.h"
#include "d_gfx_caps.h"

#include <string.h>
#include <stdlib.h>

#define DOM_CAPS_TAG(a,b,c,d) \
    ((u32)(a) | ((u32)(b) << 8u) | ((u32)(c) << 16u) | ((u32)(d) << 24u))

#define DOM_CAPS_CHUNK_CAPS DOM_CAPS_TAG('C','A','P','S')

#define DOM_CAPS_TLV_RESULT DOM_CAPS_TAG('R','S','L','T')
#define DOM_CAPS_TLV_ENTRY  DOM_CAPS_TAG('E','N','T','R')
#define DOM_CAPS_TLV_HW     DOM_CAPS_TAG('H','W','C','P')
#define DOM_CAPS_TLV_DSYS   DOM_CAPS_TAG('D','S','Y','S')
#define DOM_CAPS_TLV_DGFX   DOM_CAPS_TAG('D','G','F','X')

static const char* caps_find_selected_backend(const dom_selection* sel,
                                              dom_subsystem_id subsystem_id)
{
    u32 i;
    if (!sel) {
        return "";
    }
    for (i = 0u; i < sel->entry_count; ++i) {
        const dom_selection_entry* e = &sel->entries[i];
        if (e->subsystem_id == subsystem_id) {
            return e->backend_name ? e->backend_name : "";
        }
    }
    return "";
}

static int caps_write_tlv_str_fields(dtlv_writer* w,
                                     u32 tag,
                                     const char* name,
                                     const u32* fields,
                                     u32 field_count)
{
    u32 name_len;
    u32 payload_len;
    unsigned char* payload;
    u32 off;
    u32 i;
    int rc;

    if (!w) {
        return -1;
    }
    if (!name) {
        name = "";
    }
    name_len = (u32)strlen(name);
    payload_len = (field_count + 1u) * 4u + name_len;
    payload = (unsigned char*)malloc((size_t)payload_len);
    if (!payload) {
        return -2;
    }

    off = 0u;
    dtlv_le_write_u32(payload + off, name_len);
    off += 4u;
    for (i = 0u; i < field_count; ++i) {
        dtlv_le_write_u32(payload + off, fields[i]);
        off += 4u;
    }
    if (name_len > 0u) {
        memcpy(payload + off, name, (size_t)name_len);
    }

    rc = dtlv_writer_write_tlv(w, tag, payload, payload_len);
    free(payload);
    return rc;
}

static int caps_write_entry(dtlv_writer* w, const dom_selection_entry* e)
{
    const char* backend;
    const char* subsystem;
    u32 backend_len;
    u32 subsystem_len;
    u32 payload_len;
    unsigned char* payload;
    u32 off;
    int rc;

    if (!w || !e) {
        return -1;
    }
    backend = e->backend_name ? e->backend_name : "";
    subsystem = e->subsystem_name ? e->subsystem_name : "";
    backend_len = (u32)strlen(backend);
    subsystem_len = (u32)strlen(subsystem);
    payload_len = 7u * 4u + backend_len + subsystem_len;

    payload = (unsigned char*)malloc((size_t)payload_len);
    if (!payload) {
        return -2;
    }
    off = 0u;
    dtlv_le_write_u32(payload + off, e->subsystem_id); off += 4u;
    dtlv_le_write_u32(payload + off, (u32)e->determinism); off += 4u;
    dtlv_le_write_u32(payload + off, (u32)e->perf_class); off += 4u;
    dtlv_le_write_u32(payload + off, e->backend_priority); off += 4u;
    dtlv_le_write_u32(payload + off, e->chosen_by_override); off += 4u;
    dtlv_le_write_u32(payload + off, backend_len); off += 4u;
    dtlv_le_write_u32(payload + off, subsystem_len); off += 4u;
    if (backend_len > 0u) {
        memcpy(payload + off, backend, (size_t)backend_len);
        off += backend_len;
    }
    if (subsystem_len > 0u) {
        memcpy(payload + off, subsystem, (size_t)subsystem_len);
    }

    rc = dtlv_writer_write_tlv(w, DOM_CAPS_TLV_ENTRY, payload, payload_len);
    free(payload);
    return rc;
}

dom_caps_result dom_caps_write_capabilities_tlv(const dom_selection* sel,
                                                const char* path)
{
    dtlv_writer writer;
    dom_hw_caps hw;
    dsys_caps sys_caps;
    const char* gfx_name;
    u32 gfx_mask;
    unsigned char result_buf[12];
    unsigned char hw_buf[12];
    u32 sys_fields[5];
    u32 gfx_fields[1];
    u32 i;
    int rc;

    if (!sel || !path) {
        return DOM_CAPS_ERR_NULL;
    }

    dtlv_writer_init(&writer);
    rc = dtlv_writer_open_file(&writer, path);
    if (rc != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_CAPS_ERR;
    }
    if (dtlv_writer_begin_chunk(&writer, DOM_CAPS_CHUNK_CAPS, 1u, 0u) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_CAPS_ERR;
    }

    dtlv_le_write_u32(result_buf + 0u, (u32)sel->result);
    dtlv_le_write_u32(result_buf + 4u, (u32)sel->fail_reason);
    dtlv_le_write_u32(result_buf + 8u, (u32)sel->fail_subsystem_id);
    if (dtlv_writer_write_tlv(&writer, DOM_CAPS_TLV_RESULT, result_buf, (u32)sizeof(result_buf)) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_CAPS_ERR;
    }

    memset(&hw, 0, sizeof(hw));
    if (dom_hw_caps_probe_host(&hw) != 0) {
        memset(&hw, 0, sizeof(hw));
    }
    dtlv_le_write_u32(hw_buf + 0u, hw.os_flags);
    dtlv_le_write_u32(hw_buf + 4u, hw.cpu_flags);
    dtlv_le_write_u32(hw_buf + 8u, hw.gpu_flags);
    if (dtlv_writer_write_tlv(&writer, DOM_CAPS_TLV_HW, hw_buf, (u32)sizeof(hw_buf)) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_CAPS_ERR;
    }

    sys_caps = dsys_get_caps();
    sys_fields[0] = (u32)sys_caps.ui_modes;
    sys_fields[1] = sys_caps.has_windows ? 1u : 0u;
    sys_fields[2] = sys_caps.has_mouse ? 1u : 0u;
    sys_fields[3] = sys_caps.has_gamepad ? 1u : 0u;
    sys_fields[4] = sys_caps.has_high_res_timer ? 1u : 0u;
    if (caps_write_tlv_str_fields(&writer,
                                  DOM_CAPS_TLV_DSYS,
                                  sys_caps.name,
                                  sys_fields,
                                  5u) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_CAPS_ERR;
    }

    gfx_name = caps_find_selected_backend(sel, DOM_SUBSYS_DGFX);
    if (gfx_name && gfx_name[0]) {
        gfx_mask = d_gfx_get_opcode_mask_for_backend(gfx_name);
    } else {
        gfx_name = d_gfx_get_backend_name();
        gfx_mask = d_gfx_get_opcode_mask();
    }
    gfx_fields[0] = gfx_mask;
    if (caps_write_tlv_str_fields(&writer,
                                  DOM_CAPS_TLV_DGFX,
                                  gfx_name,
                                  gfx_fields,
                                  1u) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_CAPS_ERR;
    }

    for (i = 0u; i < sel->entry_count; ++i) {
        if (caps_write_entry(&writer, &sel->entries[i]) != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_CAPS_ERR;
        }
    }

    if (dtlv_writer_end_chunk(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_CAPS_ERR;
    }
    if (dtlv_writer_finalize(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_CAPS_ERR;
    }
    dtlv_writer_dispose(&writer);
    return DOM_CAPS_OK;
}
