/*
FILE: source/tests/dom_surface_streaming_no_modal_loading_test.cpp
MODULE: Repository
PURPOSE: Ensures surface streaming does not trigger IO/stall guards.
*/
#include <cassert>
#include <cstdio>
#include <cstring>

#include "runtime/dom_body_registry.h"
#include "runtime/dom_io_guard.h"
#include "runtime/dom_surface_chunks.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
}

int main(void) {
    dom_body_registry *bodies = dom_body_registry_create();
    dom_surface_chunks_desc desc;
    dom_surface_chunks *chunks = 0;
    dom_body_id earth_id = 0ull;
    dom_topo_latlong_q16 center;
    int rc;

    dom_io_guard_reset();

    assert(bodies != 0);
    rc = dom_body_registry_add_baseline(bodies);
    assert(rc == DOM_BODY_REGISTRY_OK);
    rc = dom_id_hash64("earth", 5u, &earth_id);
    assert(rc == DOM_SPACETIME_OK);

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_SURFACE_CHUNKS_DESC_VERSION;
    desc.max_chunks = 32u;
    desc.chunk_size_m = 2048u;

    chunks = dom_surface_chunks_create(&desc);
    assert(chunks != 0);

    center.lat_turns = 0;
    center.lon_turns = 0;

    dom_io_guard_enter_ui();
    rc = dom_surface_chunks_set_interest(chunks, bodies, earth_id, &center, d_q48_16_from_int(1200));
    assert(rc == DOM_SURFACE_CHUNKS_OK);
    rc = dom_surface_chunk_pump_jobs(chunks, 1u, 0u, 1u);
    assert(rc == DOM_SURFACE_CHUNKS_OK);
    dom_io_guard_exit_ui();

    assert(dom_io_guard_violation_count() == 0u);
    assert(dom_io_guard_stall_count() == 0u);

    dom_surface_chunks_destroy(chunks);
    dom_body_registry_destroy(bodies);

    std::printf("dom_surface_streaming_no_modal_loading_test: OK\n");
    return 0;
}
