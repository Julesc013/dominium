/*
FILE: include/domino/ui_layout.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ui_layout
RESPONSIBILITY: Defines the public contract for `ui_layout` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_UI_LAYOUT_H_INCLUDED
#define DOMINO_UI_LAYOUT_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum ui_dir {
    UI_DIR_ROW = 0,
    UI_DIR_COL
} ui_dir;

typedef struct ui_box {
    int x;
    int y;
    int w;
    int h;
} ui_box;

typedef struct ui_layout_ctx {
    ui_box viewport;
    int    dpi;
} ui_layout_ctx;

typedef struct ui_node {
    const char* id;
    ui_dir      dir;
    int         flex;
    int         min_w;
    int         min_h;
    int         max_w;
    int         max_h;
    int         pad[4];
    int         gap;
    ui_box      box;
    struct ui_node* first_child;
    struct ui_node* next_sibling;
} ui_node;

void ui_layout_compute(ui_layout_ctx* ctx, ui_node* root);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_UI_LAYOUT_H_INCLUDED */
