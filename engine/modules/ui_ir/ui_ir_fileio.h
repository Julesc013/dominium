/*
FILE: source/domino/ui_ir/ui_ir_fileio.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir fileio
RESPONSIBILITY: Atomic writes and backup rotation for UI IR files.
ALLOWED DEPENDENCIES: C/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Return codes with diagnostics; no printing.
DETERMINISM: Deterministic backup rotation order.
*/
#ifndef DOMINO_UI_IR_FILEIO_H_INCLUDED
#define DOMINO_UI_IR_FILEIO_H_INCLUDED

#include <stddef.h>
#include <vector>

#include "ui_ir_diag.h"

bool domui_atomic_write_file(const char* path, const void* data, size_t size, domui_diag* diag);
bool domui_read_file_bytes(const char* path, std::vector<unsigned char>& out_bytes, domui_diag* diag);

#endif /* DOMINO_UI_IR_FILEIO_H_INCLUDED */
