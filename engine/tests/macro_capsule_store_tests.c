#include <stdio.h>
#include <string.h>

#include "domino/sim/sim.h"
#include "domino/scale/macro_capsule_store.h"

static int fail(const char* msg)
{
    fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static int test_store_roundtrip(void)
{
    d_world_config cfg;
    d_world* world;
    d_world* loaded;
    dom_macro_capsule_blob blob;
    const unsigned char payload_a[] = "MACRO_CAPSULE_V1\ncapsule_id=1001\nEND_MACRO_CAPSULE\n";
    const unsigned char payload_b[] = "MACRO_CAPSULE_V1\ncapsule_id=2002\next=x.y.z\nEND_MACRO_CAPSULE\n";
    const char* path = "engine/tests/tmp_macro_capsule.save";
    int ok = 0;

    cfg.seed = 7u;
    cfg.width = 4u;
    cfg.height = 4u;
    world = d_world_create_from_config(&cfg);
    if (!world) {
        return fail("world create failed");
    }

    if (dom_macro_capsule_store_set_blob(world, 1001u, 10u, 55, payload_a,
                                         (u32)(sizeof(payload_a) - 1u)) != 0) {
        d_world_destroy(world);
        return fail("set blob a failed");
    }
    if (dom_macro_capsule_store_set_blob(world, 2002u, 20u, 77, payload_b,
                                         (u32)(sizeof(payload_b) - 1u)) != 0) {
        d_world_destroy(world);
        return fail("set blob b failed");
    }

    if (dom_macro_capsule_store_count(world) != 2u) {
        d_world_destroy(world);
        return fail("store count mismatch");
    }
    if (dom_macro_capsule_store_get_blob(world, 2002u, &blob) != 0 ||
        blob.byte_count != (u32)(sizeof(payload_b) - 1u) ||
        memcmp(blob.bytes, payload_b, blob.byte_count) != 0) {
        d_world_destroy(world);
        return fail("store get mismatch");
    }

    if (!d_world_save_tlv(world, path)) {
        d_world_destroy(world);
        return fail("save failed");
    }
    d_world_destroy(world);

    loaded = d_world_load_tlv(path);
    if (!loaded) {
        remove(path);
        return fail("load failed");
    }
    if (dom_macro_capsule_store_count(loaded) != 2u) {
        d_world_destroy(loaded);
        remove(path);
        return fail("loaded count mismatch");
    }
    if (dom_macro_capsule_store_get_blob(loaded, 1001u, &blob) != 0 ||
        blob.byte_count != (u32)(sizeof(payload_a) - 1u) ||
        memcmp(blob.bytes, payload_a, blob.byte_count) != 0) {
        d_world_destroy(loaded);
        remove(path);
        return fail("loaded blob mismatch");
    }
    ok = 1;
    d_world_destroy(loaded);
    remove(path);
    return ok ? 0 : 1;
}

int main(void)
{
    if (test_store_roundtrip() != 0) {
        return 1;
    }
    printf("macro capsule store tests passed\n");
    return 0;
}
