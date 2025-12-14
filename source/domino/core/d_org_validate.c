#include <stdio.h>

#include "core/d_org.h"

int d_org_validate(const struct d_world *w) {
    u32 i;
    u32 count;
    (void)w;

    count = d_org_count();
    for (i = 0u; i < count; ++i) {
        d_org o;
        d_account acc;
        if (d_org_get_by_index(i, &o) != 0) {
            fprintf(stderr, "org validate: failed get_by_index %u\n", (unsigned)i);
            return -1;
        }
        if (o.id == 0u || o.account_id == 0u) {
            fprintf(stderr, "org validate: invalid org record at index %u\n", (unsigned)i);
            return -1;
        }
        if (d_account_get(o.account_id, &acc) != 0) {
            fprintf(stderr, "org validate: missing account %u for org %u\n",
                    (unsigned)o.account_id, (unsigned)o.id);
            return -1;
        }
    }
    return 0;
}

