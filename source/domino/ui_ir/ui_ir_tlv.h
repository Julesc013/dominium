/*
FILE: source/domino/ui_ir/ui_ir_tlv.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir tlv
RESPONSIBILITY: TLV load/save for UI IR documents (DTLV container).
ALLOWED DEPENDENCIES: C++98 standard headers, domino io/container.
FORBIDDEN DEPENDENCIES: UI backends, launcher.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Return codes with diagnostics; no printing.
DETERMINISM: Canonical ordering on write.
*/
#ifndef DOMINO_UI_IR_TLV_H_INCLUDED
#define DOMINO_UI_IR_TLV_H_INCLUDED

#include "ui_ir_doc.h"
#include "ui_ir_diag.h"

bool domui_doc_load_tlv(domui_doc* out, const char* path, domui_diag* diag);
bool domui_doc_save_tlv(const domui_doc* doc, const char* path, domui_diag* diag);

#endif /* DOMINO_UI_IR_TLV_H_INCLUDED */
