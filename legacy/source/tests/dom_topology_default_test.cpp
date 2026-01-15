/*
FILE: source/tests/dom_topology_default_test.cpp
MODULE: Repository
PURPOSE: Ensures Earth defaults to sphere/ellipsoid topology (not torus).
*/
#include <cassert>
#include <cstdio>

#include "runtime/dom_body_registry.h"
#include "runtime/dom_surface_topology.h"

extern "C" {
#include "domino/core/spacetime.h"
}

int main(void) {
    dom_body_registry *bodies = dom_body_registry_create();
    dom_topology_binding binding;
    dom_body_id earth_id = 0ull;
    int rc;

    assert(bodies != 0);
    rc = dom_body_registry_add_baseline(bodies);
    assert(rc == DOM_BODY_REGISTRY_OK);

    rc = dom_id_hash64("earth", 5u, &earth_id);
    assert(rc == DOM_SPACETIME_OK);

    rc = dom_surface_topology_select(bodies, earth_id, 0u, &binding);
    assert(rc == DOM_TOPOLOGY_OK);
    assert(binding.kind == DOM_TOPOLOGY_KIND_SPHERE ||
           binding.kind == DOM_TOPOLOGY_KIND_ELLIPSOID);
    assert(binding.kind != DOM_TOPOLOGY_KIND_TORUS);

    dom_body_registry_destroy(bodies);

    std::printf("dom_topology_default_test: OK\n");
    return 0;
}
