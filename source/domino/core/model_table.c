#include "domino/model_table.h"

#include <stdlib.h>
#include <string.h>

struct dom_table_model {
    dom_table_model_desc desc;
};

dom_status dom_table_model_create(const dom_table_model_desc* desc, dom_table_model** out_model)
{
    dom_table_model* model;
    dom_table_model_desc local_desc;

    if (!out_model) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_model = NULL;

    model = (dom_table_model*)malloc(sizeof(dom_table_model));
    if (!model) {
        return DOM_STATUS_ERROR;
    }
    memset(model, 0, sizeof(*model));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
    }
    local_desc.struct_size = sizeof(dom_table_model_desc);
    model->desc = local_desc;

    *out_model = model;
    return DOM_STATUS_OK;
}

void dom_table_model_destroy(dom_table_model* model)
{
    if (!model) {
        return;
    }
    free(model);
}

dom_status dom_table_model_get_schema(dom_table_model* model, dom_table_schema* out_schema)
{
    if (!model || !out_schema) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_schema = model->desc.schema;
    out_schema->struct_size = sizeof(dom_table_schema);
    return DOM_STATUS_OK;
}

dom_status dom_table_model_get_cell(dom_table_model* model, uint32_t row, uint32_t column, dom_table_cell* out_cell)
{
    (void)row;
    (void)column;
    if (!model || !out_cell) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    memset(out_cell, 0, sizeof(*out_cell));
    out_cell->struct_size = sizeof(dom_table_cell);
    out_cell->struct_version = 1u;
    out_cell->text = "";
    return DOM_STATUS_OK;
}

dom_status dom_table_model_set_row_count(dom_table_model* model, uint32_t row_count)
{
    if (!model) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    model->desc.row_count = row_count;
    return DOM_STATUS_OK;
}
