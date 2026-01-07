/*
FILE: source/tests/dom_cosmo_bundle_roundtrip_test.cpp
MODULE: Repository
PURPOSE: Verifies COSMO_GRAPH chunk round-trips with identical bytes.
*/
#include <cassert>
#include <cstdio>
#include <vector>

#include "dominium/core_tlv.h"
#include "dominium/feature_epoch.h"
#include "runtime/dom_cosmo_graph.h"
#include "runtime/dom_universe_bundle.h"

static bool read_file_bytes(const char *path, std::vector<unsigned char> &out) {
    std::FILE *fp = std::fopen(path, "rb");
    long size = 0;
    size_t got = 0;
    if (!fp) {
        return false;
    }
    if (std::fseek(fp, 0, SEEK_END) != 0) {
        std::fclose(fp);
        return false;
    }
    size = std::ftell(fp);
    if (size < 0) {
        std::fclose(fp);
        return false;
    }
    if (std::fseek(fp, 0, SEEK_SET) != 0) {
        std::fclose(fp);
        return false;
    }
    out.resize((size_t)size);
    if (size > 0) {
        got = std::fread(&out[0], 1, (size_t)size, fp);
        if (got != (size_t)size) {
            std::fclose(fp);
            return false;
        }
    }
    std::fclose(fp);
    return true;
}

static void build_graph(dom::dom_cosmo_graph &graph) {
    u64 filament = 0ull;
    u64 cluster = 0ull;
    u64 galaxy = 0ull;
    u64 system = 0ull;
    u64 system_peer = 0ull;
    u64 out_id = 0ull;
    dom::dom_cosmo_edge_params params;

    assert(dom::dom_cosmo_graph_init(&graph, 7ull, 0) == dom::DOM_COSMO_GRAPH_OK);
    assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_FILAMENT,
                                           "filament.root", 0ull, &filament)
           == dom::DOM_COSMO_GRAPH_OK);
    assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_CLUSTER,
                                           "cluster.root", filament, &cluster)
           == dom::DOM_COSMO_GRAPH_OK);
    assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_GALAXY,
                                           "galaxy.root", cluster, &galaxy)
           == dom::DOM_COSMO_GRAPH_OK);
    assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_SYSTEM,
                                           "system.root", galaxy, &system)
           == dom::DOM_COSMO_GRAPH_OK);
    assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_SYSTEM,
                                           "system.peer", galaxy, &system_peer)
           == dom::DOM_COSMO_GRAPH_OK);

    params.duration_ticks = 90ull;
    params.cost = 2u;
    params.event_table_id = 0ull;
    assert(dom::dom_cosmo_graph_add_travel_edge(&graph, system, system_peer, &params, &out_id)
           == dom::DOM_COSMO_GRAPH_OK);
}

int main(void) {
    const char *path_a = "tmp_cosmo_roundtrip_a.dub";
    const char *path_b = "tmp_cosmo_roundtrip_b.dub";
    dom::dom_cosmo_graph graph;
    std::vector<unsigned char> cosmo_payload;
    u64 cosmo_hash = 0ull;
    dom_universe_bundle *bundle = dom_universe_bundle_create();
    dom_universe_bundle *read_bundle = dom_universe_bundle_create();
    dom_universe_bundle_identity id;
    std::vector<unsigned char> bytes_a;
    std::vector<unsigned char> bytes_b;
    int rc;

    assert(bundle != 0);
    assert(read_bundle != 0);

    build_graph(graph);
    rc = dom::dom_cosmo_graph_serialize(&graph, &cosmo_payload);
    assert(rc == dom::DOM_COSMO_GRAPH_OK);
    assert(!cosmo_payload.empty());
    cosmo_hash = dom::core_tlv::tlv_fnv1a64(&cosmo_payload[0], cosmo_payload.size());
    assert(cosmo_hash != 0ull);

    id.universe_id = "cosmo_u1";
    id.universe_id_len = 8u;
    id.instance_id = "inst_a";
    id.instance_id_len = 6u;
    id.content_graph_hash = 0xabcddcba11223344ull;
    id.sim_flags_hash = 0x11223344abcddcbaull;
    id.cosmo_graph_hash = cosmo_hash;
    id.ups = 60u;
    id.tick_index = 0ull;
    id.feature_epoch = DOM_FEATURE_EPOCH_DEFAULT;

    rc = dom_universe_bundle_set_identity(bundle, &id);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    rc = dom_universe_bundle_set_chunk(bundle,
                                       DOM_UNIVERSE_CHUNK_COSM,
                                       1u,
                                       &cosmo_payload[0],
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

    rc = dom_universe_bundle_write_file(path_a, bundle);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    rc = dom_universe_bundle_read_file(path_a, &id, read_bundle);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    rc = dom_universe_bundle_write_file(path_b, read_bundle);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    assert(read_file_bytes(path_a, bytes_a));
    assert(read_file_bytes(path_b, bytes_b));
    assert(bytes_a.size() == bytes_b.size());
    assert(bytes_a == bytes_b);

    dom_universe_bundle_destroy(read_bundle);
    dom_universe_bundle_destroy(bundle);
    std::remove(path_a);
    std::remove(path_b);

    std::printf("dom_cosmo_bundle_roundtrip_test: OK\n");
    return 0;
}
