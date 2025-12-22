/*
FILE: source/domino/ui_ir/ui_validate.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir validate
RESPONSIBILITY: Validate UI IR documents against backend/tier capabilities.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher runtime.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Diagnostics collected; no printing.
DETERMINISM: Stable ordering for diagnostics.
*/
#ifndef DOMINO_UI_IR_VALIDATE_H_INCLUDED
#define DOMINO_UI_IR_VALIDATE_H_INCLUDED

#include "ui_ir_doc.h"
#include "ui_ir_diag.h"
#include "ui_caps.h"

bool domui_validate_doc(const domui_doc* doc, const domui_target_set* targets, domui_diag* out_diag);

#endif /* DOMINO_UI_IR_VALIDATE_H_INCLUDED */
