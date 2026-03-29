/*
FILE: source/domino/ui_ir/ui_ir_legacy_import.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir legacy import
RESPONSIBILITY: Import legacy launcher_ui_v1.tlv into UI IR.
ALLOWED DEPENDENCIES: C++98 standard headers, DUI schema tags, domino io/container.
FORBIDDEN DEPENDENCIES: UI backends, launcher runtime.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Return codes with diagnostics; no printing.
DETERMINISM: Stable ID remap policy and canonical ordering.
*/
#ifndef DOMINO_UI_IR_LEGACY_IMPORT_H_INCLUDED
#define DOMINO_UI_IR_LEGACY_IMPORT_H_INCLUDED

#include "ui_ir_doc.h"
#include "ui_ir_diag.h"

bool domui_doc_import_legacy_launcher_tlv(domui_doc* out, const char* legacy_path, domui_diag* diag);

#endif /* DOMINO_UI_IR_LEGACY_IMPORT_H_INCLUDED */
