/*
FILE: source/tests/dom_universe_bundle_epoch_test.cpp
MODULE: Repository
PURPOSE: Validates feature_epoch mismatch refusal in universe bundle loads.
*/
#include <cassert>
#include <cstdio>
#include <vector>

#include "dominium/core_tlv.h"
#include "dominium/feature_epoch.h"
#include "runtime/dom_cosmo_graph.h"
#include "runtime/dom_universe_bundle.h"

int main(void) {
    const char *path = "tmp_universe_epoch.dub";
    dom_universe_bundle *bundle = dom_universe_bundle_create();
    dom_universe_bundle *read_ok = dom_universe_bundle_create();
    dom_universe_bundle *read_bad = dom_universe_bundle_create();
    dom_universe_bundle_identity id;
    dom_universe_bundle_identity expect;
    dom_universe_bundle_identity expect_bad;
    dom::dom_cosmo_graph graph;
    std::vector<unsigned char> cosmo_payload;
    u64 cosmo_hash = 0ull;
    int rc;

    assert(bundle != 0);
    assert(read_ok != 0);
    assert(read_bad != 0);

    id.universe_id = "u1";
    id.universe_id_len = 2u;
    id.instance_id = "inst1";
    id.instance_id_len = 5u;
    id.content_graph_hash = 0x1122334455667788ull;
    id.sim_flags_hash = 0x8899aabbccddeeffull;
    id.ups = 60u;
    id.tick_index = 0ull;
    id.feature_epoch = DOM_FEATURE_EPOCH_DEFAULT;
    id.cosmo_graph_hash = 0ull;

    rc = dom::dom_cosmo_graph_init(&graph, 0ull, 0);
    assert(rc == dom::DOM_COSMO_GRAPH_OK);
    rc = dom::dom_cosmo_graph_serialize(&graph, &cosmo_payload);
    assert(rc == dom::DOM_COSMO_GRAPH_OK);
    assert(!cosmo_payload.empty());
    cosmo_hash = dom::core_tlv::tlv_fnv1a64(&cosmo_payload[0], cosmo_payload.size());
    assert(cosmo_hash != 0ull);
    id.cosmo_graph_hash = cosmo_hash;

    rc = dom_universe_bundle_set_identity(bundle, &id);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    rc = dom_universe_bundle_set_chunk(bundle,
                                       DOM_UNIVERSE_CHUNK_COSM,
                                       1u,
                                       cosmo_payload.empty() ? (const void *)0 : &cosmo_payload[0],
                                       (u32)cosmo_payload.size());
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_CELE, 1u, (const void *)0, 0u);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_VESL, 1u, (const void *)0, 0u);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_SURF, 1u, (const void *)0, 0u);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_LOCL, 1u, (const void *)0, 0u);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_RNG, 1u, (const void *)0, 0u);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    rc = dom_universe_bundle_write_file(path, bundle);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    expect = id;
    rc = dom_universe_bundle_read_file(path, &expect, read_ok);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    expect_bad = id;
    expect_bad.feature_epoch = DOM_FEATURE_EPOCH_DEFAULT + 1u;
    rc = dom_universe_bundle_read_file(path, &expect_bad, read_bad);
    assert(rc == DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED);

    dom_universe_bundle_destroy(read_bad);
    dom_universe_bundle_destroy(read_ok);
    dom_universe_bundle_destroy(bundle);
    std::remove(path);

    std::printf("dom_universe_bundle_epoch_test: OK\n");
    return 0;
}
