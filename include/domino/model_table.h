/*
FILE: include/domino/model_table.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / model_table
RESPONSIBILITY: Defines the public contract for `model_table` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_MODEL_TABLE_H_INCLUDED
#define DOMINO_MODEL_TABLE_H_INCLUDED

#include <stddef.h>
#include "domino/baseline.h"
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_table_meta {
    uint32_t    struct_size;
    uint32_t    struct_version;
    const char* id;        /* e.g. "instances_table" */
    uint32_t    row_count;
    uint32_t    col_count;
    const char* const* col_ids;  /* e.g. { "id", "name", "path", ... } */
} dom_table_meta;

bool dom_table_get_meta(dom_core* core, const char* table_id, dom_table_meta* meta);
bool dom_table_get_cell(dom_core* core, const char* table_id, uint32_t row, uint32_t col, char* buf, size_t buf_size);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_MODEL_TABLE_H_INCLUDED */
