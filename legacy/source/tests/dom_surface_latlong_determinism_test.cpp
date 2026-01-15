/*
FILE: source/tests/dom_surface_latlong_determinism_test.cpp
MODULE: Repository
PURPOSE: Verify deterministic lat/long <-> body-fixed transforms (round-trip stability).
*/
#include <cassert>
#include <cstdio>
#include <cstring>

#include "runtime/dom_body_registry.h"
#include "runtime/dom_surface_topology.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
}

static q48_16 abs_q48_16(q48_16 v) {
    return (v < 0) ? (q48_16)(-v) : v;
}

static void check_roundtrip(const dom_topology_binding *binding,
                            const dom_topo_latlong_q16 *seed,
                            q48_16 altitude_m) {
    dom_posseg_q16 pos_a;
    dom_posseg_q16 pos_b;
    dom_topo_latlong_q16 ll_a;
    dom_topo_latlong_q16 ll_b;
    q48_16 alt_a = 0;
    q48_16 alt_b = 0;
    int rc;

    std::memset(&pos_a, 0, sizeof(pos_a));
    std::memset(&pos_b, 0, sizeof(pos_b));

    rc = dom_surface_topology_pos_from_latlong(binding, seed, altitude_m, &pos_a);
    assert(rc == DOM_TOPOLOGY_OK);

    rc = dom_surface_topology_latlong(binding, &pos_a, &ll_a);
    assert(rc == DOM_TOPOLOGY_OK);

    rc = dom_surface_topology_altitude(binding, &pos_a, &alt_a);
    assert(rc == DOM_TOPOLOGY_OK);

    rc = dom_surface_topology_pos_from_latlong(binding, &ll_a, alt_a, &pos_b);
    assert(rc == DOM_TOPOLOGY_OK);

    rc = dom_surface_topology_latlong(binding, &pos_b, &ll_b);
    assert(rc == DOM_TOPOLOGY_OK);

    rc = dom_surface_topology_altitude(binding, &pos_b, &alt_b);
    assert(rc == DOM_TOPOLOGY_OK);

    assert(ll_a.lat_turns == ll_b.lat_turns);
    assert(ll_a.lon_turns == ll_b.lon_turns);
    assert(abs_q48_16(d_q48_16_sub(alt_a, alt_b)) <= d_q48_16_from_int(1));
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

    {
        const dom_topo_latlong_q16 seeds[] = {
            { 0, 0 },
            { 0, (q16_16)0x4000 },
            { 0, (q16_16)0x8000 },
            { (q16_16)0x2000, 0 },
            { (q16_16)-0x2000, 0 }
        };
        const q48_16 altitudes[] = {
            d_q48_16_from_int(0),
            d_q48_16_from_int(500)
        };
        size_t i;
        size_t j;
        for (i = 0u; i < sizeof(seeds) / sizeof(seeds[0]); ++i) {
            for (j = 0u; j < sizeof(altitudes) / sizeof(altitudes[0]); ++j) {
                check_roundtrip(&binding, &seeds[i], altitudes[j]);
            }
        }
    }

    dom_body_registry_destroy(bodies);
    std::printf("dom_surface_latlong_determinism_test: OK\n");
    return 0;
}
