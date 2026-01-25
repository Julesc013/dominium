/*
FILE: include/dominium/physical/parts_and_assemblies.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Defines parts, assemblies, and volume claim checks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Assembly stability and volume checks are deterministic.
*/
#ifndef DOMINIUM_PHYSICAL_PARTS_AND_ASSEMBLIES_H
#define DOMINIUM_PHYSICAL_PARTS_AND_ASSEMBLIES_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/dnumeric.h"
#include "dominium/physical/physical_audit.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_PART_IFACE_MECHANICAL = 1u << 0,
    DOM_PART_IFACE_ELECTRICAL = 1u << 1,
    DOM_PART_IFACE_FLUID = 1u << 2,
    DOM_PART_IFACE_THERMAL = 1u << 3,
    DOM_PART_IFACE_DATA = 1u << 4
};

enum {
    DOM_PART_FLAG_REQUIRES_SUPPORT = 1u << 0
};

typedef struct dom_physical_part_desc {
    u64 part_id;
    MassKg mass_kg_q16;
    VolM3 volume_m3_q16;
    u32 interface_mask;
    u32 failure_mode_mask;
    u32 flags;
} dom_physical_part_desc;

typedef struct dom_part_registry {
    dom_physical_part_desc* parts;
    u32 count;
    u32 capacity;
} dom_part_registry;

void dom_part_registry_init(dom_part_registry* reg,
                            dom_physical_part_desc* storage,
                            u32 capacity);
dom_physical_part_desc* dom_part_find(dom_part_registry* reg,
                                      u64 part_id);
int dom_part_register(dom_part_registry* reg,
                      const dom_physical_part_desc* desc);

typedef struct dom_assembly_part {
    u64 part_id;
    u32 flags;
    u32 interface_mask;
    MassKg mass_kg_q16;
} dom_assembly_part;

typedef struct dom_assembly_connection {
    u32 a;
    u32 b;
    u32 interface_mask;
} dom_assembly_connection;

typedef struct dom_assembly {
    u64 assembly_id;
    dom_assembly_part* parts;
    u32 part_count;
    u32 part_capacity;
    dom_assembly_connection* connections;
    u32 connection_count;
    u32 connection_capacity;
    u32 grounded_mask;
} dom_assembly;

void dom_assembly_init(dom_assembly* assembly,
                       u64 assembly_id,
                       dom_assembly_part* parts,
                       u32 part_capacity,
                       dom_assembly_connection* connections,
                       u32 connection_capacity);
int dom_assembly_add_part(dom_assembly* assembly,
                          const dom_physical_part_desc* part_desc,
                          u32* out_index);
int dom_assembly_connect(dom_assembly* assembly,
                         u32 a,
                         u32 b,
                         u32 interface_mask);
int dom_assembly_set_grounded(dom_assembly* assembly,
                              u32 part_index,
                              int grounded);
int dom_assembly_check_support(const dom_assembly* assembly);

typedef struct dom_volume_claim {
    u64 claim_id;
    u64 owner_id;
    i32 min_x;
    i32 min_y;
    i32 max_x;
    i32 max_y;
    u32 flags;
} dom_volume_claim;

typedef struct dom_volume_claim_registry {
    dom_volume_claim* claims;
    u32 count;
    u32 capacity;
} dom_volume_claim_registry;

void dom_volume_claim_registry_init(dom_volume_claim_registry* reg,
                                    dom_volume_claim* storage,
                                    u32 capacity);
int dom_volume_claim_register(dom_volume_claim_registry* reg,
                              const dom_volume_claim* claim,
                              dom_physical_audit_log* audit,
                              dom_act_time_t now_act);
int dom_volume_claim_release(dom_volume_claim_registry* reg,
                             u64 claim_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_PARTS_AND_ASSEMBLIES_H */
