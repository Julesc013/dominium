/*
FILE: source/domino/ui_ir/ui_ir_types.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir types
RESPONSIBILITY: Defines core UI IR primitive types and enums (C++98, deterministic).
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher, TLV I/O.
THREADING MODEL: Data-only; no internal synchronization.
ERROR MODEL: N/A (types).
DETERMINISM: Plain data types only.
*/
#ifndef DOMINO_UI_IR_TYPES_H_INCLUDED
#define DOMINO_UI_IR_TYPES_H_INCLUDED

typedef unsigned int domui_u32;
typedef domui_u32 domui_widget_id;
typedef domui_u32 domui_action_id;

typedef struct domui_vec2i {
    int x;
    int y;
} domui_vec2i;

typedef struct domui_recti {
    int x;
    int y;
    int w;
    int h;
} domui_recti;

typedef struct domui_box {
    int left;
    int right;
    int top;
    int bottom;
} domui_box;

typedef enum domui_widget_type_e {
    DOMUI_WIDGET_CONTAINER = 0,
    DOMUI_WIDGET_STATIC_TEXT,
    DOMUI_WIDGET_BUTTON,
    DOMUI_WIDGET_EDIT,
    DOMUI_WIDGET_LISTBOX,
    DOMUI_WIDGET_COMBOBOX,
    DOMUI_WIDGET_CHECKBOX,
    DOMUI_WIDGET_RADIO,
    DOMUI_WIDGET_TAB,
    DOMUI_WIDGET_TREEVIEW,
    DOMUI_WIDGET_LISTVIEW,
    DOMUI_WIDGET_PROGRESS,
    DOMUI_WIDGET_SLIDER,
    DOMUI_WIDGET_GROUPBOX,
    DOMUI_WIDGET_IMAGE,
    DOMUI_WIDGET_SPLITTER,
    DOMUI_WIDGET_SCROLLPANEL,
    DOMUI_WIDGET_TABS,
    DOMUI_WIDGET_TAB_PAGE
} domui_widget_type;

typedef enum domui_container_layout_mode_e {
    DOMUI_LAYOUT_ABSOLUTE = 0,
    DOMUI_LAYOUT_STACK_ROW,
    DOMUI_LAYOUT_STACK_COL,
    DOMUI_LAYOUT_GRID
} domui_container_layout_mode;

typedef enum domui_dock_mode_e {
    DOMUI_DOCK_NONE = 0,
    DOMUI_DOCK_LEFT,
    DOMUI_DOCK_RIGHT,
    DOMUI_DOCK_TOP,
    DOMUI_DOCK_BOTTOM,
    DOMUI_DOCK_FILL
} domui_dock_mode;

typedef enum domui_anchor_mask_e {
    DOMUI_ANCHOR_L = 1,
    DOMUI_ANCHOR_R = 2,
    DOMUI_ANCHOR_T = 4,
    DOMUI_ANCHOR_B = 8
} domui_anchor_mask;

#endif /* DOMINO_UI_IR_TYPES_H_INCLUDED */
