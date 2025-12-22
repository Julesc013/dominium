/*
FILE: source/domino/ui_ir/ui_layout.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir layout
RESPONSIBILITY: Deterministic layout engine for UI IR documents.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher runtime.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Return false on invalid args or insufficient output buffer; diagnostics collected.
DETERMINISM: Canonical ordering only; integer math only.
*/
#ifndef DOMINO_UI_IR_LAYOUT_H_INCLUDED
#define DOMINO_UI_IR_LAYOUT_H_INCLUDED

#include "ui_ir_doc.h"
#include "ui_ir_diag.h"

struct domui_layout_rect {
    int x;
    int y;
    int w;
    int h;
};

struct domui_layout_result {
    domui_widget_id widget_id;
    domui_layout_rect rect;
};

bool domui_compute_layout(
    const domui_doc* doc,
    domui_widget_id root_id,
    int root_x,
    int root_y,
    int root_w,
    int root_h,
    domui_layout_result* out_results,
    int* inout_result_count,
    domui_diag* diag
);

#endif /* DOMINO_UI_IR_LAYOUT_H_INCLUDED */
