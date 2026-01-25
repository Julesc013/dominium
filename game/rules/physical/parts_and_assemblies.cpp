/*
FILE: game/rules/physical/parts_and_assemblies.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Implements parts, assemblies, and volume claim checks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Assembly stability and volume checks are deterministic.
*/
#include "dominium/physical/parts_and_assemblies.h"

#include <string.h>

void dom_part_registry_init(dom_part_registry* reg,
                            dom_physical_part_desc* storage,
                            u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->parts = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_physical_part_desc) * (size_t)capacity);
    }
}

static u32 dom_part_find_index(const dom_part_registry* reg,
                               u64 part_id,
                               int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->parts) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->parts[i].part_id == part_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->parts[i].part_id > part_id) {
            break;
        }
    }
    return i;
}

dom_physical_part_desc* dom_part_find(dom_part_registry* reg,
                                      u64 part_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->parts) {
        return 0;
    }
    idx = dom_part_find_index(reg, part_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->parts[idx];
}

int dom_part_register(dom_part_registry* reg,
                      const dom_physical_part_desc* desc)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->parts || !desc || desc->part_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = dom_part_find_index(reg, desc->part_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->parts[i] = reg->parts[i - 1u];
    }
    reg->parts[idx] = *desc;
    reg->count += 1u;
    return 0;
}

void dom_assembly_init(dom_assembly* assembly,
                       u64 assembly_id,
                       dom_assembly_part* parts,
                       u32 part_capacity,
                       dom_assembly_connection* connections,
                       u32 connection_capacity)
{
    if (!assembly) {
        return;
    }
    assembly->assembly_id = assembly_id;
    assembly->parts = parts;
    assembly->part_count = 0u;
    assembly->part_capacity = part_capacity;
    assembly->connections = connections;
    assembly->connection_count = 0u;
    assembly->connection_capacity = connection_capacity;
    assembly->grounded_mask = 0u;
    if (parts && part_capacity > 0u) {
        memset(parts, 0, sizeof(dom_assembly_part) * (size_t)part_capacity);
    }
    if (connections && connection_capacity > 0u) {
        memset(connections, 0, sizeof(dom_assembly_connection) * (size_t)connection_capacity);
    }
}

int dom_assembly_add_part(dom_assembly* assembly,
                          const dom_physical_part_desc* part_desc,
                          u32* out_index)
{
    dom_assembly_part* part;
    if (!assembly || !part_desc) {
        return -1;
    }
    if (assembly->part_count >= assembly->part_capacity) {
        return -2;
    }
    part = &assembly->parts[assembly->part_count];
    memset(part, 0, sizeof(*part));
    part->part_id = part_desc->part_id;
    part->flags = part_desc->flags;
    part->interface_mask = part_desc->interface_mask;
    part->mass_kg_q16 = part_desc->mass_kg_q16;
    if (out_index) {
        *out_index = assembly->part_count;
    }
    assembly->part_count += 1u;
    return 0;
}

int dom_assembly_connect(dom_assembly* assembly,
                         u32 a,
                         u32 b,
                         u32 interface_mask)
{
    dom_assembly_connection* conn;
    if (!assembly || !assembly->connections) {
        return -1;
    }
    if (a >= assembly->part_count || b >= assembly->part_count) {
        return -2;
    }
    if (assembly->connection_count >= assembly->connection_capacity) {
        return -3;
    }
    conn = &assembly->connections[assembly->connection_count++];
    conn->a = a;
    conn->b = b;
    conn->interface_mask = interface_mask;
    return 0;
}

int dom_assembly_set_grounded(dom_assembly* assembly,
                              u32 part_index,
                              int grounded)
{
    if (!assembly || part_index >= assembly->part_count) {
        return -1;
    }
    if (part_index >= 32u) {
        return -2;
    }
    if (grounded) {
        assembly->grounded_mask |= (1u << part_index);
    } else {
        assembly->grounded_mask &= ~(1u << part_index);
    }
    return 0;
}

int dom_assembly_check_support(const dom_assembly* assembly)
{
    u32 supported_mask = 0u;
    u32 i;
    u32 changed;
    if (!assembly || assembly->part_count == 0u) {
        return 0;
    }
    supported_mask = assembly->grounded_mask;
    if (supported_mask == 0u) {
        return 0;
    }
    do {
        changed = 0u;
        for (i = 0u; i < assembly->connection_count; ++i) {
            const dom_assembly_connection* conn = &assembly->connections[i];
            u32 a_bit = (conn->a < 32u) ? (1u << conn->a) : 0u;
            u32 b_bit = (conn->b < 32u) ? (1u << conn->b) : 0u;
            if ((supported_mask & a_bit) != 0u && (supported_mask & b_bit) == 0u) {
                supported_mask |= b_bit;
                changed = 1u;
            } else if ((supported_mask & b_bit) != 0u && (supported_mask & a_bit) == 0u) {
                supported_mask |= a_bit;
                changed = 1u;
            }
        }
    } while (changed != 0u);
    for (i = 0u; i < assembly->part_count && i < 32u; ++i) {
        if ((assembly->parts[i].flags & DOM_PART_FLAG_REQUIRES_SUPPORT) != 0u) {
            if ((supported_mask & (1u << i)) == 0u) {
                return 0;
            }
        }
    }
    return 1;
}

void dom_volume_claim_registry_init(dom_volume_claim_registry* reg,
                                    dom_volume_claim* storage,
                                    u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->claims = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_volume_claim) * (size_t)capacity);
    }
}

static int dom_volume_claims_overlap(const dom_volume_claim* a,
                                     const dom_volume_claim* b)
{
    if (!a || !b) {
        return 0;
    }
    if (a->max_x <= b->min_x || b->max_x <= a->min_x) {
        return 0;
    }
    if (a->max_y <= b->min_y || b->max_y <= a->min_y) {
        return 0;
    }
    return 1;
}

int dom_volume_claim_register(dom_volume_claim_registry* reg,
                              const dom_volume_claim* claim,
                              dom_physical_audit_log* audit,
                              dom_act_time_t now_act)
{
    u32 i;
    if (!reg || !reg->claims || !claim) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (dom_volume_claims_overlap(&reg->claims[i], claim)) {
            if (audit) {
                dom_physical_audit_set_context(audit, now_act, 0u);
                dom_physical_audit_record(audit,
                                          claim->owner_id,
                                          DOM_PHYS_EVENT_VOLUME_CONFLICT,
                                          claim->claim_id,
                                          reg->claims[i].claim_id,
                                          0);
            }
            return -3;
        }
    }
    reg->claims[reg->count++] = *claim;
    if (audit) {
        dom_physical_audit_set_context(audit, now_act, 0u);
        dom_physical_audit_record(audit,
                                  claim->owner_id,
                                  DOM_PHYS_EVENT_STRUCTURE_BUILD,
                                  claim->claim_id,
                                  0u,
                                  0);
    }
    return 0;
}

int dom_volume_claim_release(dom_volume_claim_registry* reg,
                             u64 claim_id)
{
    u32 i;
    if (!reg || !reg->claims) {
        return -1;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->claims[i].claim_id == claim_id) {
            u32 j;
            for (j = i + 1u; j < reg->count; ++j) {
                reg->claims[j - 1u] = reg->claims[j];
            }
            reg->count -= 1u;
            return 0;
        }
    }
    return -2;
}
