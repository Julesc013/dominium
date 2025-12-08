#include <string.h>
#include "core_internal.h"

static const char* g_instances_table_cols[] = { "id", "name", "path" };

bool dom_table_get_meta(dom_core* core, const char* table_id, dom_table_meta* meta)
{
    (void)core;

    if (!meta || !table_id) {
        return false;
    }

    if (strcmp(table_id, "instances_table") != 0) {
        return false;
    }

    meta->struct_size = sizeof(dom_table_meta);
    meta->struct_version = 1;
    meta->id = "instances_table";
    meta->row_count = 0;
    meta->col_count = 3;
    meta->col_ids = g_instances_table_cols;
    return true;
}

bool dom_table_get_cell(dom_core* core, const char* table_id, uint32_t row, uint32_t col, char* buf, size_t buf_size)
{
    (void)core;
    (void)row;
    (void)col;
    (void)buf_size;

    if (!table_id || !buf || buf_size == 0) {
        return false;
    }

    if (strcmp(table_id, "instances_table") != 0) {
        return false;
    }

    buf[0] = '\0';
    return false;
}
