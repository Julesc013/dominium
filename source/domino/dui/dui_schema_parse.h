/*
FILE: source/domino/dui/dui_schema_parse.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dui/schema_parse
RESPONSIBILITY: Internal TLV schema/state parsing helpers for DUI backends (skip-unknown; bounded outputs).
ALLOWED DEPENDENCIES: `include/dui/**`, `include/domino/**`, `source/domino/**` (within engine), and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Presentation-only; parsing is deterministic for a given byte stream.
VERSIONING / ABI / DATA FORMAT NOTES: TLV is skip-unknown; see `include/dui/dui_schema_tlv.h`.
EXTENSION POINTS: Add new tags; old parsers skip unknown.
*/
#ifndef DOMINO_DUI_SCHEMA_PARSE_H
#define DOMINO_DUI_SCHEMA_PARSE_H

#include "dui/dui_api_v1.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dui_schema_node {
    u32 id;
    u32 kind; /* dui_node_kind */
    u32 action_id;
    u32 bind_id;
    u32 flags;
    u64 required_caps;
    u32 visible_bind_id; /* optional: STATE bind id that gates visibility (0 => always visible) */

    u32 v_min;
    u32 v_max;

    char* text; /* heap; may be NULL */

    /* Layout rect (pixels). */
    i32 x;
    i32 y;
    i32 w;
    i32 h;

    /* Backend-native handle (e.g., HWND); opaque to parser. */
    void* native;

    struct dui_schema_node* first_child;
    struct dui_schema_node* next_sibling;
} dui_schema_node;

dui_schema_node* dui_schema_parse_first_form_root(const void* schema_tlv, u32 schema_len, dui_result* out_err);
void             dui_schema_free(dui_schema_node* n);
dui_schema_node* dui_schema_find_by_id(dui_schema_node* root, u32 id);

/* Layout helper shared by backends (simple row/column/stack). */
void dui_schema_layout(dui_schema_node* root, i32 x, i32 y, i32 w, i32 h);

/* State lookup helpers (scan TLV; no allocations). */
int dui_state_get_u32(const void* state_tlv, u32 state_len, u32 bind_id, u32* out_v);
int dui_state_get_i32(const void* state_tlv, u32 state_len, u32 bind_id, i32* out_v);
int dui_state_get_u64(const void* state_tlv, u32 state_len, u32 bind_id, u64* out_v);
int dui_state_get_text(const void* state_tlv, u32 state_len, u32 bind_id, char* out_text, u32 out_cap, u32* out_len);

/* List helpers. List selection is by item_id (0 means none). */
int dui_state_get_list_selected_item_id(const void* state_tlv, u32 state_len, u32 bind_id, u32* out_item_id);
int dui_state_get_list_item_count(const void* state_tlv, u32 state_len, u32 bind_id, u32* out_count);
int dui_state_get_list_item_at(const void* state_tlv,
                               u32 state_len,
                               u32 bind_id,
                               u32 index,
                               u32* out_item_id,
                               char* out_text,
                               u32 out_cap,
                               u32* out_len);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_DUI_SCHEMA_PARSE_H */
