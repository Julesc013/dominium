/*
FILE: source/tests/dom_universe_editor_roundtrip_test.cpp
MODULE: Dominium Tests
PURPOSE: Verify universe editor edits round-trip deterministically.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "runtime/dom_universe_bundle.h"
#include "universe_editor/ue_commands.h"

static bool read_file_bytes(const std::string &path, std::vector<unsigned char> &out) {
    FILE *f = std::fopen(path.c_str(), "rb");
    long size = 0;
    size_t got = 0u;
    out.clear();
    if (!f) {
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    size = std::ftell(f);
    if (size < 0) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    if (size == 0) {
        std::fclose(f);
        return true;
    }
    out.resize((size_t)size);
    got = std::fread(&out[0], 1u, (size_t)size, f);
    std::fclose(f);
    return got == (size_t)size;
}

int main() {
    const char *path_a = "tmp_universe_editor_a.dub";
    const char *path_b = "tmp_universe_editor_b.dub";
    dom_universe_bundle *bundle = dom_universe_bundle_create();
    dom_universe_bundle *loaded = dom_universe_bundle_create();
    dom_universe_bundle_identity id;
    std::string err;
    dom::tools::UeRouteEntry route;
    std::vector<dom::tools::UeSystemEntry> systems;
    std::vector<dom::tools::UeRouteEntry> routes;
    std::vector<unsigned char> bytes_a;
    std::vector<unsigned char> bytes_b;
    int rc;

    assert(bundle);
    assert(loaded);
    std::memset(&id, 0, sizeof(id));
    id.universe_id = "u1";
    id.universe_id_len = 2u;
    id.instance_id = "inst1";
    id.instance_id_len = 5u;
    id.ups = 60u;
    id.tick_index = 0ull;
    id.feature_epoch = 1u;
    rc = dom_universe_bundle_set_identity(bundle, &id);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_SYSM, 1u, (const void *)0, 0u);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    rc = dom_universe_bundle_set_chunk(bundle, DOM_UNIVERSE_CHUNK_ROUT, 1u, (const void *)0, 0u);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    assert(dom::tools::ue_add_system(bundle, "sol", 0ull, &err));

    std::memset(&route, 0, sizeof(route));
    route.id = 1ull;
    route.src_station_id = 2ull;
    route.dst_station_id = 3ull;
    route.duration_ticks = 60ull;
    route.capacity_units = 10ull;
    assert(dom::tools::ue_upsert_route(bundle, route, &err));

    rc = dom_universe_bundle_write_file(path_a, bundle);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    rc = dom_universe_bundle_read_file(path_a, 0, loaded);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);
    assert(dom::tools::ue_load_systems(loaded, systems, &err));
    assert(dom::tools::ue_load_routes(loaded, routes, &err));
    assert(systems.size() == 1u);
    assert(routes.size() == 1u);
    assert(routes[0].duration_ticks == route.duration_ticks);
    assert(routes[0].capacity_units == route.capacity_units);

    rc = dom_universe_bundle_write_file(path_b, loaded);
    assert(rc == DOM_UNIVERSE_BUNDLE_OK);

    assert(read_file_bytes(path_a, bytes_a));
    assert(read_file_bytes(path_b, bytes_b));
    assert(bytes_a == bytes_b);

    dom_universe_bundle_destroy(loaded);
    dom_universe_bundle_destroy(bundle);
    std::remove(path_a);
    std::remove(path_b);

    std::printf("dom_universe_editor_roundtrip_test: OK\n");
    return 0;
}
