#include <string.h>

#include "struct/d_struct_instance.h"

void d_struct_instance_reset(d_struct_instance *inst) {
    if (!inst) {
        return;
    }
    memset(inst, 0, sizeof(*inst));
}

