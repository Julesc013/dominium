/*
FILE: source/tests/dom_surface_chunk_activation_determinism_test.cpp
MODULE: Repository
PURPOSE: Ensures surface chunk activation is deterministic for a fixed bubble path.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

#include "runtime/dom_body_registry.h"
#include "runtime/dom_surface_chunks.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
}

static void collect_active(dom_surface_chunks *chunks,
                           std::vector<dom_surface_chunk_status> &out) {
    u32 count = 0u;
    int rc = dom_surface_chunks_list_active(chunks, 0, 0u, &count);
    assert(rc == DOM_SURFACE_CHUNKS_OK);
    out.clear();
    if (count == 0u) {
        return;
    }
    out.resize(count);
    rc = dom_surface_chunks_list_active(chunks, &out[0], count, &count);
    assert(rc == DOM_SURFACE_CHUNKS_OK);
    if (out.size() != count) {
        out.resize(count);
    }
}

static void compare_lists(const std::vector<dom_surface_chunk_status> &a,
                          const std::vector<dom_surface_chunk_status> &b) {
    size_t i;
    assert(a.size() == b.size());
    for (i = 0u; i < a.size(); ++i) {
        assert(a[i].key.body_id == b[i].key.body_id);
        assert(a[i].key.step_turns_q16 == b[i].key.step_turns_q16);
        assert(a[i].key.lat_index == b[i].key.lat_index);
        assert(a[i].key.lon_index == b[i].key.lon_index);
        assert(a[i].state == b[i].state);
    }
}

int main(void) {
    dom_body_registry *bodies = dom_body_registry_create();
    dom_body_id earth_id = 0ull;
    dom_surface_chunks_desc desc;
    dom_surface_chunks *chunks_a = 0;
    dom_surface_chunks *chunks_b = 0;
    int rc;

    assert(bodies != 0);
    rc = dom_body_registry_add_baseline(bodies);
    assert(rc == DOM_BODY_REGISTRY_OK);
    rc = dom_id_hash64("earth", 5u, &earth_id);
    assert(rc == DOM_SPACETIME_OK);

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_SURFACE_CHUNKS_DESC_VERSION;
    desc.max_chunks = 64u;
    desc.chunk_size_m = 2048u;

    chunks_a = dom_surface_chunks_create(&desc);
    chunks_b = dom_surface_chunks_create(&desc);
    assert(chunks_a != 0);
    assert(chunks_b != 0);

    {
        const dom_topo_latlong_q16 path[] = {
            { 0, 0 },
            { 0, (q16_16)0x0100 },
            { (q16_16)0x0080, (q16_16)0x0200 }
        };
        const q48_16 radius = d_q48_16_from_int(1200);
        std::vector<dom_surface_chunk_status> list_a;
        std::vector<dom_surface_chunk_status> list_b;
        size_t i;

        for (i = 0u; i < sizeof(path) / sizeof(path[0]); ++i) {
            rc = dom_surface_chunks_set_interest(chunks_a, bodies, earth_id, &path[i], radius);
            assert(rc == DOM_SURFACE_CHUNKS_OK);
            rc = dom_surface_chunks_set_interest(chunks_b, bodies, earth_id, &path[i], radius);
            assert(rc == DOM_SURFACE_CHUNKS_OK);

            collect_active(chunks_a, list_a);
            collect_active(chunks_b, list_b);
            compare_lists(list_a, list_b);
        }
    }

    dom_surface_chunks_destroy(chunks_b);
    dom_surface_chunks_destroy(chunks_a);
    dom_body_registry_destroy(bodies);

    std::printf("dom_surface_chunk_activation_determinism_test: OK\n");
    return 0;
}
