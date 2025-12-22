/*
FILE: include/dui/dui_schema_tlv.h
MODULE: DUI
LAYER / SUBSYSTEM: DUI API / schema TLV
RESPONSIBILITY: Defines the TLV tags and enums for DUI schemas/state snapshots (POD-only, baseline-visible).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; launcher core headers; UI toolkit headers.
THREADING MODEL: N/A (data format constants only).
ERROR MODEL: N/A (data format constants only).
DETERMINISM: Data-driven UI only; schemas/state are inputs and must not influence simulation.
VERSIONING / ABI / DATA FORMAT NOTES: TLV format; skip-unknown; see `docs/SPEC_DUI.md`.
EXTENSION POINTS: Add new tags and enum values; old readers must skip unknown tags.
*/
#ifndef DUI_SCHEMA_TLV_H_INCLUDED
#define DUI_SCHEMA_TLV_H_INCLUDED

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* DUI schema/state TLV uses the canonical TLV record shape:
 *   u32_le tag, u32_le len, payload bytes
 *
 * Tags below are stable u32 constants. Payloads are either:
 * - nested TLV streams (for containers), or
 * - little-endian scalars (u32/u64), or
 * - UTF-8 strings (NUL-terminated is allowed but not required; use len).
 */

/* Root schema tags (payload = nested TLV). */
#define DUI_TLV_SCHEMA_V1        ((u32)0x53434831u) /* 'SCH1' */
#define DUI_TLV_FORM_V1          ((u32)0x464F524Du) /* 'FORM' */
#define DUI_TLV_NODE_V1          ((u32)0x4E4F4445u) /* 'NODE' */

/* Node properties (payload types vary). */
#define DUI_TLV_ID_U32           ((u32)0x49445F32u) /* 'ID_2' */
#define DUI_TLV_KIND_U32         ((u32)0x4B494E44u) /* 'KIND' */
#define DUI_TLV_TEXT_UTF8        ((u32)0x54455854u) /* 'TEXT' */
#define DUI_TLV_ACTION_U32       ((u32)0x4143544Eu) /* 'ACTN' */
#define DUI_TLV_BIND_U32         ((u32)0x42494E44u) /* 'BIND' */
#define DUI_TLV_FLAGS_U32        ((u32)0x464C4743u) /* 'FLGC' */
#define DUI_TLV_REQUIRED_CAPS_U64 ((u32)0x43415053u) /* 'CAPS' */
/* Optional: state-driven visibility gate (payload = le u32 bind id).
 * When present, the backend treats STATE value (bool/u32) at this bind id as:
 * - 0 => hidden (node + subtree are not rendered and do not receive input)
 * - non-zero => visible
 */
#define DUI_TLV_VISIBLE_BIND_U32 ((u32)0x56495342u) /* 'VISB' */

/* Splitter-specific properties (payload = le u32). */
#define DUI_TLV_SPLITTER_ORIENT_U32 ((u32)0x534F5249u) /* 'SORI' */
#define DUI_TLV_SPLITTER_POS_U32    ((u32)0x53504F53u) /* 'SPOS' */
#define DUI_TLV_SPLITTER_THICK_U32  ((u32)0x5354484Bu) /* 'STHK' */
#define DUI_TLV_SPLITTER_MIN_A_U32  ((u32)0x534D4E41u) /* 'SMNA' */
#define DUI_TLV_SPLITTER_MIN_B_U32  ((u32)0x534D4E42u) /* 'SMNB' */

/* Tabs-specific properties (payload = le u32). */
#define DUI_TLV_TABS_SELECTED_U32   ((u32)0x5453454Cu) /* 'TSEL' */
#define DUI_TLV_TABS_PLACEMENT_U32  ((u32)0x54504C43u) /* 'TPLC' */
#define DUI_TLV_TAB_ENABLED_U32     ((u32)0x54454E41u) /* 'TENA' */

/* Scroll panel properties (payload = le u32). */
#define DUI_TLV_SCROLL_H_ENABLED_U32 ((u32)0x53434845u) /* 'SCHE' */
#define DUI_TLV_SCROLL_V_ENABLED_U32 ((u32)0x53435645u) /* 'SCVE' */
#define DUI_TLV_SCROLL_X_U32         ((u32)0x5343585Fu) /* 'SCX_' */
#define DUI_TLV_SCROLL_Y_U32         ((u32)0x5343595Fu) /* 'SCY_' */

/* Node flags stored in DUI_TLV_FLAGS_U32 (bitset). */
#define DUI_NODE_FLAG_FOCUSABLE ((u32)1u << 0u)
#define DUI_NODE_FLAG_FLEX      ((u32)1u << 1u)

/* Nested node lists (payload = nested TLV streams). */
#define DUI_TLV_CHILDREN_V1      ((u32)0x4348494Cu) /* 'CHIL' */
#define DUI_TLV_VALIDATION_V1    ((u32)0x56414C44u) /* 'VALD' */

/* Validation tags (payload = le scalars). */
#define DUI_TLV_MIN_U32          ((u32)0x4D494E5Fu) /* 'MIN_' */
#define DUI_TLV_MAX_U32          ((u32)0x4D41585Fu) /* 'MAX_' */

/* State snapshot tags (payload = nested TLV). */
#define DUI_TLV_STATE_V1         ((u32)0x53544131u) /* 'STA1' */
#define DUI_TLV_VALUE_V1         ((u32)0x56414C55u) /* 'VALU' */

/* Value record fields. */
#define DUI_TLV_VALUE_TYPE_U32   ((u32)0x56545950u) /* 'VTYP' */
#define DUI_TLV_VALUE_U32        ((u32)0x5633325Fu) /* 'V32_' */
#define DUI_TLV_VALUE_I32        ((u32)0x4933325Fu) /* 'I32_' */
#define DUI_TLV_VALUE_U64        ((u32)0x5636345Fu) /* 'V64_' */
#define DUI_TLV_VALUE_UTF8       ((u32)0x5638545Fu) /* 'V8T_' */

/* List value subrecords (payload = nested TLV). */
#define DUI_TLV_LIST_V1          ((u32)0x4C495354u) /* 'LIST' */
#define DUI_TLV_LIST_SELECTED_U32 ((u32)0x53454C53u) /* 'SELS' */
#define DUI_TLV_LIST_ITEM_V1     ((u32)0x4954454Du) /* 'ITEM' */
#define DUI_TLV_ITEM_ID_U32      ((u32)0x49544944u) /* 'ITID' */
#define DUI_TLV_ITEM_TEXT_UTF8   ((u32)0x49545854u) /* 'ITXT' */

/* Kind enums used by schema NODEs. */
typedef enum dui_node_kind_e {
    DUI_NODE_NONE = 0,

    /* Layout primitives. */
    DUI_NODE_ROW = 1,
    DUI_NODE_COLUMN = 2,
    DUI_NODE_STACK = 3,

    /* Basic widgets. */
    DUI_NODE_LABEL = 10,
    DUI_NODE_BUTTON = 11,
    DUI_NODE_CHECKBOX = 12,
    DUI_NODE_LIST = 13,
    DUI_NODE_TEXT_FIELD = 14,
    DUI_NODE_PROGRESS = 15,

    /* Complex widgets. */
    DUI_NODE_SPLITTER = 20,
    DUI_NODE_TABS = 21,
    DUI_NODE_TAB_PAGE = 22,
    DUI_NODE_SCROLL_PANEL = 23
} dui_node_kind;

typedef enum dui_splitter_orientation_e {
    DUI_SPLIT_VERTICAL = 0,
    DUI_SPLIT_HORIZONTAL = 1
} dui_splitter_orientation;

typedef enum dui_tabs_placement_e {
    DUI_TABS_TOP = 0,
    DUI_TABS_BOTTOM = 1,
    DUI_TABS_LEFT = 2,
    DUI_TABS_RIGHT = 3
} dui_tabs_placement;

/* Value types used by STATE/VALU records. */
typedef enum dui_value_type_e {
    DUI_VALUE_NONE = 0,
    DUI_VALUE_BOOL = 1, /* stored as u32 0/1 */
    DUI_VALUE_U32  = 2,
    DUI_VALUE_I32  = 3,
    DUI_VALUE_U64  = 4,
    DUI_VALUE_TEXT = 5,
    DUI_VALUE_LIST = 6
} dui_value_type;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DUI_SCHEMA_TLV_H_INCLUDED */
