#ifndef DOMINO_MODEL_TABLE_H_INCLUDED
#define DOMINO_MODEL_TABLE_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_table_model dom_table_model;

typedef struct dom_table_column_desc {
    uint32_t   struct_size;
    uint32_t   struct_version;
    const char* id;
    const char* label;
    uint32_t   width;
} dom_table_column_desc;

typedef struct dom_table_schema {
    uint32_t                    struct_size;
    uint32_t                    struct_version;
    const dom_table_column_desc* columns;
    uint32_t                    column_count;
} dom_table_schema;

typedef struct dom_table_model_desc {
    uint32_t        struct_size;
    uint32_t        struct_version;
    dom_table_schema schema;
    uint32_t        row_count;
} dom_table_model_desc;

typedef struct dom_table_cell {
    uint32_t   struct_size;
    uint32_t   struct_version;
    const char* text;
} dom_table_cell;

dom_status dom_table_model_create(const dom_table_model_desc* desc, dom_table_model** out_model);
void       dom_table_model_destroy(dom_table_model* model);
dom_status dom_table_model_get_schema(dom_table_model* model, dom_table_schema* out_schema);
dom_status dom_table_model_get_cell(dom_table_model* model, uint32_t row, uint32_t column, dom_table_cell* out_cell);
dom_status dom_table_model_set_row_count(dom_table_model* model, uint32_t row_count);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_MODEL_TABLE_H_INCLUDED */
