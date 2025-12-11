#include <stdio.h>
#include <string.h>

#include "d_worldgen.h"
#include "d_world.h"

#define D_WORLDGEN_MAX 64u

static d_worldgen_provider g_providers[D_WORLDGEN_MAX];
static u32 g_provider_count = 0u;

int d_worldgen_register(const d_worldgen_provider *prov) {
    u32 i;
    if (!prov || prov->id == 0u) {
        fprintf(stderr, "d_worldgen_register: invalid provider\n");
        return -1;
    }
    for (i = 0u; i < g_provider_count; ++i) {
        if (g_providers[i].id == prov->id) {
            fprintf(stderr, "d_worldgen_register: duplicate id %u\n", (unsigned int)prov->id);
            return -2;
        }
    }
    if (g_provider_count >= D_WORLDGEN_MAX) {
        fprintf(stderr, "d_worldgen_register: registry full\n");
        return -3;
    }
    g_providers[g_provider_count] = *prov;
    g_provider_count += 1u;
    return 0;
}

static int d_worldgen_deps_satisfied(const d_worldgen_provider *prov, const unsigned char *done_flags) {
    const d_worldgen_provider_id *dep;
    if (!prov || !done_flags) {
        return 0;
    }
    dep = prov->depends_on;
    if (!dep) {
        return 1;
    }
    while (*dep != 0u) {
        d_worldgen_provider_id dep_id = *dep;
        u32 i;
        int found = 0;
        for (i = 0u; i < g_provider_count; ++i) {
            if (g_providers[i].id == dep_id) {
                if (done_flags[i]) {
                    found = 1;
                } else {
                    return 0;
                }
                break;
            }
        }
        if (!found) {
            return 0;
        }
        ++dep;
    }
    return 1;
}

int d_worldgen_run(struct d_world *w, struct d_chunk *chunk) {
    unsigned char done[D_WORLDGEN_MAX];
    u32 processed;
    u32 i;

    if (!w || !chunk) {
        return -1;
    }
    if (g_provider_count == 0u) {
        return 0;
    }

    memset(done, 0, sizeof(done));
    processed = 0u;

    while (processed < g_provider_count) {
        int progress = 0;
        for (i = 0u; i < g_provider_count; ++i) {
            const d_worldgen_provider *prov = &g_providers[i];
            if (done[i]) {
                continue;
            }
            if (!d_worldgen_deps_satisfied(prov, done)) {
                continue;
            }
            if (prov->populate_chunk) {
                prov->populate_chunk(w, chunk);
            }
            done[i] = 1;
            processed += 1u;
            progress = 1;
        }
        if (!progress) {
            fprintf(stderr, "d_worldgen_run: dependency cycle detected\n");
            return -1;
        }
    }

    return 0;
}
