/*
FILE: source/tests/dom_universe_bundle_systems_roundtrip_test.cpp
MODULE: Repository
PURPOSE: Verifies systems/bodies/frames/topology chunks round-trip with stable bytes.
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
    u64 out_id = 0ull;
    dom::dom_cosmo_edge_params params;

    assert(dom::dom_cosmo_graph_init(&graph, 9ull, 0) == dom::DOM_COSMO_GRAPH_OK);
    assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_FILAMENT,
                                           "filament.sys", 0ull, &filament)
           == dom::DOM_COSMO_GRAPH_OK);
    assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_CLUSTER,
                                           "cluster.sys", filament, &cluster)
           == dom::DOM_COSMO_GRAPH_OK);
    assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_GALAXY,
                                           "galaxy.sys", cluster, &galaxy)
           == dom::DOM_COSMO_GRAPH_OK);
    assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_SYSTEM,
                                           "system.sys", galaxy, &system)
           == dom::DOM_COSMO_GRAPH_OK);

    params.duration_ticks = 10ull;
    params.cost = 1u;
    params.event_table_id = 0ull;
    assert(dom::dom_cosmo_graph_add_travel_edge(&graph, system, system, &params, &out_id)
           == dom::DOM_COSMO_GRAPH_OK);
}

int main(void) {
    const char *path_a = "tmp_universe_systems_a.dub";
    const char *path_b = "tmp_universe_systems_b.dub";
    dom_universe_bundle *bundle = dom_universe_bundle_create();
    dom_universe_bundle *read_bundle = dom_universe_bundle_create();
    dom_universe_bundle_identity id;
    dom::dom_cosmo_graph graph;
    std::vector<unsigned char> cosmo_payload;
    std::vector<unsigned char> sysm_payload;
    std::vector<unsigned char> bods_payload;
    std::vector<unsigned char> fram_payload;
    std::vector<unsigned char> topb_payload;
    std::vector<unsigned char> bytes_a;
    std::vector<unsigned char> bytes_b;
    u64 cosmo_hash = 0ull;
    u64 sysm_hash = 0ull;
    u64 bods_hash = 0ull;
    u64 fram_hash = 0ull;
    u64 topb_hash = 0ull;
    int rc;

    assert(bundle != 0);
    assert(read_bundle != 0);

    build_graph(graph);
    rc = dom::dom_cosmo_graph_serialize(&graph, &cosmo_payload);
    assert(rc == dom::DOM_COSMO_GRAPH_OK);
    assert(!cosmo_payload.empty());
    cosmo_hash = dom::core_tlv::tlv_fnv1a64(&cosmo_payload[0], cosmo_payload.size());
    assert(cosmo_hash != 0ull);

    sysm_payload.push_back('S');
    sysm_payload.push_back('Y');
    sysm_payload.push_back('S');
    sysm_payload.push_back('M');
    sysm_payload.push_back(1u);
    bods_payload.push_back('B');
    bods_payload.push_back('O');
    bods_payload.push_back('D');
    bods_payload.push_back('S');
    bods_payload.push_back(2u);
    fram_payload.push_back('F');
    fram_payload.push_back('R');
    fram_payload.push_back('A');
    fram_payload.push_back('M');
    fram_payload.push_back(3u);
    topb_payload.push_back('T');
    topb_payload.push_back('O');
    topb_payload.push_back('P');
    topb_payload.push_back('B');
    topb_payload.push_back(4u);

    sysm_hash = dom::core_tlv::tlv_fnv1a64(&sysm_payload[0], sysm_payload.size());
    bods_hash = dom::core_tlv::tlv_fnv1a64(&bods_payload[0], bods_payload.size());
    fram_hash = dom::core_tlv::tlv_fnv1a64(&fram_payload[0], fram_payload.size());
    topb_hash = dom::core_tlv::tlv_fnv1a64(&topb_payload[0], topb_payload.size());

    id.universe_id = "u_sys";
    id.universe_id_len = 5u;
    id.instance_id = "inst_sys";
    id.instance_id_len = 8u;
    id.content_graph_hash = 0x0123456789abcdefull;
    id.sim_flags_hash = 0xfedcba9876543210ull;
    id.cosmo_graph_hash = cosmo_hash;
    id.systems_hash = sysm_hash;
    id.bodies_hash = bods_hash;
    id.frames_hash = fram_hash;
    id.topology_hash = topb_hash;
    id.ups = 60u;
    id.tick_index = 0ull;
    id.feature_epoch = DOM_FEATURE_EPOCH_DEFAULT;

    rc = dom_universe_bundle_set_identity(bundle, &id);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_COSM, 1u,
                                       &cosmo_payload[0], (u32)cosmo_payload.size());
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_SYSM, 1u,
                                       &sysm_payload[0], (u32)sysm_payload.size());
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_BODS, 1u,
                                       &bods_payload[0], (u32)bods_payload.size());
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_FRAM, 1u,
                                       &fram_payload[0], (u32)fram_payload.size());
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_TOPB, 1u,
                                       &topb_payload[0], (u32)topb_payload.size());
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

    {
        const unsigned char foreign_payload[] = { 0xAA, 0xBB, 0xCC };
        rc = dom_universe_bundle_add_foreign(bundle,
                                             DOM_U32_FOURCC('X','T','R','A'),
                                             1u,
                                             0u,
                                             foreign_payload,
                                             (u32)sizeof(foreign_payload));
        assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    }

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

    std::printf("dom_universe_bundle_systems_roundtrip_test: OK\n");
    return 0;
}
