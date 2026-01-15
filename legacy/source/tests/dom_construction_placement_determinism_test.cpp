/*
FILE: source/tests/dom_construction_placement_determinism_test.cpp
MODULE: Repository
PURPOSE: Ensures construction placement yields deterministic registry state.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

#include "dominium/core_tlv.h"
#include "runtime/dom_construction_registry.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
}

static void append_u32(std::vector<unsigned char> &out, u32 v) {
    out.push_back((unsigned char)(v & 0xffu));
    out.push_back((unsigned char)((v >> 8u) & 0xffu));
    out.push_back((unsigned char)((v >> 16u) & 0xffu));
    out.push_back((unsigned char)((v >> 24u) & 0xffu));
}

static void append_u64(std::vector<unsigned char> &out, u64 v) {
    append_u32(out, (u32)(v & 0xffffffffu));
    append_u32(out, (u32)((v >> 32u) & 0xffffffffu));
}

static void append_i32(std::vector<unsigned char> &out, i32 v) {
    append_u32(out, (u32)v);
}

static void append_i64(std::vector<unsigned char> &out, i64 v) {
    append_u64(out, (u64)v);
}

static u64 registry_hash(const dom_construction_registry *registry) {
    std::vector<unsigned char> bytes;
    u32 count = 0u;
    int rc = dom_construction_list(registry, 0, 0u, &count);
    assert(rc == DOM_CONSTRUCTION_OK);
    append_u32(bytes, count);
    if (count > 0u) {
        std::vector<dom_construction_instance> list;
        list.resize(count);
        rc = dom_construction_list(registry, &list[0], count, &count);
        assert(rc == DOM_CONSTRUCTION_OK);
        if (list.size() != count) {
            list.resize(count);
        }
        for (u32 i = 0u; i < count; ++i) {
            const dom_construction_instance &inst = list[i];
            append_u64(bytes, inst.instance_id);
            append_u32(bytes, inst.type_id);
            append_u32(bytes, inst.orientation);
            append_u64(bytes, inst.body_id);
            append_i32(bytes, inst.chunk_key.step_turns_q16);
            append_i32(bytes, inst.chunk_key.lat_index);
            append_i32(bytes, inst.chunk_key.lon_index);
            append_i64(bytes, (i64)inst.local_pos_m[0]);
            append_i64(bytes, (i64)inst.local_pos_m[1]);
            append_i64(bytes, (i64)inst.local_pos_m[2]);
            append_i32(bytes, inst.cell_x);
            append_i32(bytes, inst.cell_y);
        }
    }
    return bytes.empty() ? 0ull : dom::core_tlv::tlv_fnv1a64(&bytes[0], bytes.size());
}

static void fill_instance(dom_construction_instance &inst,
                          dom_construction_instance_id id,
                          dom_body_id body_id,
                          i32 lat_index,
                          i32 lon_index,
                          i32 cell_x,
                          i32 cell_y,
                          q48_16 east,
                          q48_16 north,
                          q48_16 up) {
    std::memset(&inst, 0, sizeof(inst));
    inst.instance_id = id;
    inst.type_id = DOM_CONSTRUCTION_TYPE_HABITAT;
    inst.body_id = body_id;
    inst.chunk_key.body_id = body_id;
    inst.chunk_key.step_turns_q16 = 0x0100;
    inst.chunk_key.lat_index = lat_index;
    inst.chunk_key.lon_index = lon_index;
    inst.local_pos_m[0] = east;
    inst.local_pos_m[1] = north;
    inst.local_pos_m[2] = up;
    inst.orientation = 0u;
    inst.cell_x = cell_x;
    inst.cell_y = cell_y;
}

int main(void) {
    dom_construction_registry *reg_a = dom_construction_registry_create();
    dom_construction_registry *reg_b = dom_construction_registry_create();
    dom_body_id earth_id = 0ull;
    dom_construction_instance insts[3];
    u64 hash_a = 0ull;
    u64 hash_b = 0ull;
    int rc;

    assert(reg_a != 0);
    assert(reg_b != 0);
    rc = dom_id_hash64("earth", 5u, &earth_id);
    assert(rc == DOM_SPACETIME_OK);

    fill_instance(insts[0], 1ull, earth_id, 0, 0, 0, 0,
                  d_q48_16_from_int(0), d_q48_16_from_int(0), d_q48_16_from_int(0));
    fill_instance(insts[1], 2ull, earth_id, 0, 1, 1, 0,
                  d_q48_16_from_int(1), d_q48_16_from_int(0), d_q48_16_from_int(0));
    fill_instance(insts[2], 3ull, earth_id, 1, 0, 0, 1,
                  d_q48_16_from_int(0), d_q48_16_from_int(1), d_q48_16_from_int(0));

    rc = dom_construction_register_instance(reg_a, &insts[0], 0);
    assert(rc == DOM_CONSTRUCTION_OK);
    rc = dom_construction_register_instance(reg_a, &insts[1], 0);
    assert(rc == DOM_CONSTRUCTION_OK);
    rc = dom_construction_register_instance(reg_a, &insts[2], 0);
    assert(rc == DOM_CONSTRUCTION_OK);

    rc = dom_construction_register_instance(reg_b, &insts[0], 0);
    assert(rc == DOM_CONSTRUCTION_OK);
    {
        u32 tmp = 0u;
        rc = dom_construction_list(reg_b, 0, 0u, &tmp);
        assert(rc == DOM_CONSTRUCTION_OK);
    }
    rc = dom_construction_register_instance(reg_b, &insts[1], 0);
    assert(rc == DOM_CONSTRUCTION_OK);
    rc = dom_construction_register_instance(reg_b, &insts[2], 0);
    assert(rc == DOM_CONSTRUCTION_OK);

    hash_a = registry_hash(reg_a);
    hash_b = registry_hash(reg_b);
    assert(hash_a == hash_b);

    dom_construction_registry_destroy(reg_b);
    dom_construction_registry_destroy(reg_a);

    std::printf("dom_construction_placement_determinism_test: OK\n");
    return 0;
}
