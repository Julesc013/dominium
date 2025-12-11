/* Resource/economic prototype definitions (C89). */
#ifndef D_RES_PROTO_H
#define D_RES_PROTO_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_material_id;
typedef u32 d_item_id;
typedef u32 d_process_id;
typedef u32 d_deposit_id;
typedef u32 d_container_proto_id;

/* Material prototype */
typedef struct d_proto_material {
    d_material_id id;
    const char   *name;

    u32           tags;          /* METALLIC, ORGANIC, FUEL_SOLID, FLUID, GAS, etc. */

    q16_16        density;       /* kg/m^3 in game units */
    q16_16        hardness;
    q16_16        melting_point;

    d_tlv_blob    extra;         /* future fields, hazard data, etc. */
} d_proto_material;

/* Item prototype */
typedef struct d_proto_item {
    d_item_id     id;
    const char   *name;

    d_material_id material_id;   /* 0 = virtual/non-material item */

    u32           tags;          /* BULK, COMPONENT, TOOL, FUEL_ITEM, etc. */
    u16           max_stack;

    q16_16        unit_mass;
    q16_16        unit_volume;

    d_tlv_blob    extra;         /* quality, rarity, icon refs, etc. */
} d_proto_item;

/* Container prototype (crates, pallets, jars, tanks) */
typedef struct d_proto_container {
    d_container_proto_id id;
    const char          *name;

    q16_16              internal_volume;     /* m^3 */
    q16_16              max_mass;

    u16                 slot_count;          /* 0 = bulk-only */

    u32                 allowed_material_tags;
    u32                 allowed_item_tags;

    u16                 packing_mode;        /* BULK_SINGLE_MATERIAL, DISCRETE_SLOTS, etc. */

    d_tlv_blob          extra;
} d_proto_container;

/* Process prototype (crafting, smelting, packing, assembly) */

#define D_RES_PROCESS_ITEM_MAX   8
#define D_RES_PROCESS_FLUID_MAX  4

typedef struct d_res_process_item {
    d_item_id id;
    u16       count;
} d_res_process_item;

typedef struct d_res_process_fluid {
    d_material_id id;   /* fluid or gas material */
    q16_16        amount;
} d_res_process_fluid;

typedef struct d_proto_process {
    d_process_id         id;
    const char          *name;
    d_res_process_item   item_in[D_RES_PROCESS_ITEM_MAX];
    d_res_process_item   item_out[D_RES_PROCESS_ITEM_MAX];
    d_res_process_fluid  fluid_in[D_RES_PROCESS_FLUID_MAX];
    d_res_process_fluid  fluid_out[D_RES_PROCESS_FLUID_MAX];

    q16_16               time_ticks;
    q16_16               power_required;

    u32                  tags;        /* SMELTING, CHEMISTRY, HAND_CRAFT, MACHINE_ONLY, etc. */

    d_tlv_blob           extra;
} d_proto_process;

/* Deposit prototype (ore body, reservoir, vegetation patch, etc.) */
typedef struct d_proto_deposit {
    d_deposit_id  id;
    const char   *name;

    d_material_id material_id;    /* ore, oil, gas, biomass, etc. */
    u16           model_family;   /* e.g. D_MODEL_FAMILY_RES */
    u16           model_id;       /* model within family (e.g. strata, reservoir) */

    u32           tags;           /* STRATA_SOLID, RESERVOIR_OIL, VEGETATION_SURFACE, etc. */

    d_tlv_blob    params;         /* model-specific parameters (grade, pressure, etc.) */

    d_tlv_blob    extra;
} d_proto_deposit;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_RES_PROTO_H */
