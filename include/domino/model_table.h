#ifndef DOMINO_MODEL_TABLE_H_INCLUDED
#define DOMINO_MODEL_TABLE_H_INCLUDED

#include <stddef.h>
#include <stdint.h>
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
    const char** col_ids;  /* e.g. { "id", "name", "path", ... } */
} dom_table_meta;

bool dom_table_get_meta(dom_core* core, const char* table_id, dom_table_meta* meta);
bool dom_table_get_cell(dom_core* core, const char* table_id, uint32_t row, uint32_t col, char* buf, size_t buf_size);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_MODEL_TABLE_H_INCLUDED */
