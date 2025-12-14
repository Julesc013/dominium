#include <string.h>

#include "sim/pkt/dg_pkt_common.h"

void dg_pkt_hdr_clear(dg_pkt_hdr *hdr) {
    if (!hdr) {
        return;
    }
    memset(hdr, 0, sizeof(*hdr));
}

