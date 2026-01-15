/*
FILE: source/tests/dom_construction_overlap_refusal_test.cpp
MODULE: Repository
PURPOSE: Ensures overlapping construction placement is refused deterministically.
*/
#include <cassert>
#include <cstdio>
#include <cstring>

#include "runtime/dom_construction_registry.h"

extern "C" {
#include "domino/core/spacetime.h"
}

static void fill_instance(dom_construction_instance &inst,
                          dom_construction_instance_id id,
                          dom_body_id body_id,
                          i32 cell_x,
                          i32 cell_y) {
    std::memset(&inst, 0, sizeof(inst));
    inst.instance_id = id;
    inst.type_id = DOM_CONSTRUCTION_TYPE_STORAGE;
    inst.body_id = body_id;
    inst.chunk_key.body_id = body_id;
    inst.chunk_key.step_turns_q16 = 0x0100;
    inst.chunk_key.lat_index = 0;
    inst.chunk_key.lon_index = 0;
    inst.local_pos_m[0] = 0;
    inst.local_pos_m[1] = 0;
    inst.local_pos_m[2] = 0;
    inst.orientation = 0u;
    inst.cell_x = cell_x;
    inst.cell_y = cell_y;
}

int main(void) {
    dom_construction_registry *registry = dom_construction_registry_create();
    dom_body_id earth_id = 0ull;
    dom_construction_instance a;
    dom_construction_instance b;
    int rc;

    assert(registry != 0);
    rc = dom_id_hash64("earth", 5u, &earth_id);
    assert(rc == DOM_SPACETIME_OK);

    fill_instance(a, 1ull, earth_id, 0, 0);
    fill_instance(b, 2ull, earth_id, 0, 0);

    rc = dom_construction_register_instance(registry, &a, 0);
    assert(rc == DOM_CONSTRUCTION_OK);
    rc = dom_construction_register_instance(registry, &b, 0);
    assert(rc == DOM_CONSTRUCTION_OVERLAP);

    dom_construction_registry_destroy(registry);

    std::printf("dom_construction_overlap_refusal_test: OK\n");
    return 0;
}
