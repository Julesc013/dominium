#include <string.h>

#include "struct/d_struct_instance.h"

void d_struct_inventory_clear(d_struct_inventory *inv) {
    if (!inv) {
        return;
    }
    inv->item_id = 0u;
    inv->count = 0u;
}

int d_struct_inventory_add(d_struct_inventory *inv, u32 item_id, u32 count) {
    if (!inv || item_id == 0u || count == 0u) {
        return -1;
    }
    if (inv->item_id == 0u) {
        inv->item_id = item_id;
    } else if (inv->item_id != item_id) {
        return -1;
    }
    if (count > 0xFFFFFFFFu - inv->count) {
        inv->count = 0xFFFFFFFFu;
        return -1;
    }
    inv->count += count;
    return 0;
}
