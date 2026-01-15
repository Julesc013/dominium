/*
FILE: source/domino/ui_ir/ui_ir_json.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir json
RESPONSIBILITY: Deterministic JSON mirror for UI IR documents.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Return codes with diagnostics; no printing.
DETERMINISM: Stable key ordering and canonical widget order.
*/
#ifndef DOMINO_UI_IR_JSON_H_INCLUDED
#define DOMINO_UI_IR_JSON_H_INCLUDED

#include "ui_ir_doc.h"
#include "ui_ir_diag.h"

bool domui_doc_save_json_mirror(const domui_doc* doc, const char* json_path, domui_diag* diag);

#endif /* DOMINO_UI_IR_JSON_H_INCLUDED */
