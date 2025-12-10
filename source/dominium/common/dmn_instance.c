#include "dominium/instance.h"
#include <stdlib.h>
#include <string.h>

int dmn_instance_load(const char* instance_id, DmnInstance* out)
{
    if (!instance_id || !out) return -1;
    memset(out, 0, sizeof(*out));
    strncpy(out->instance_id, instance_id, sizeof(out->instance_id) - 1);
    strncpy(out->label, instance_id, sizeof(out->label) - 1);
    out->flags.demo_mode = 0;
    return 0;
}

int dmn_instance_save(const DmnInstance* inst)
{
    (void)inst;
    return -1;
}

int dmn_instance_list(DmnInstanceList* out)
{
    if (out) {
        out->instances = NULL;
        out->count = 0;
    }
    return 0;
}

void dmn_instance_list_free(DmnInstanceList* list)
{
    if (!list) return;
    if (list->instances) {
        free(list->instances);
        list->instances = NULL;
    }
    list->count = 0;
}
