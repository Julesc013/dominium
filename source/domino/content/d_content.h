/* Content subsystem public interface (C89). */
#ifndef D_CONTENT_H
#define D_CONTENT_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Identifier typedefs for all prototype kinds. */
typedef u32 d_material_id;
typedef u32 d_item_id;
typedef u32 d_container_proto_id;
typedef u32 d_process_id;
typedef u32 d_deposit_proto_id;
typedef u32 d_structure_proto_id;
typedef u32 d_vehicle_proto_id;
typedef u32 d_spline_profile_id;
typedef u32 d_job_template_id;
typedef u32 d_building_proto_id;
typedef u32 d_blueprint_id;
typedef u32 d_pack_id;
typedef u32 d_mod_id;

/* Generic tag flags (bitmasks) shared across prototype types. */
typedef u32 d_content_tag;

#define D_TAG_MATERIAL_SOLID     (1u << 0)
#define D_TAG_MATERIAL_FLUID     (1u << 1)
#define D_TAG_MATERIAL_GAS       (1u << 2)
#define D_TAG_GENERIC_ORGANIC    (1u << 3)
#define D_TAG_GENERIC_SYNTHETIC  (1u << 4)
#define D_TAG_GENERIC_REFINED    (1u << 5)
#define D_TAG_GENERIC_METALLIC   (1u << 6)
#define D_TAG_ITEM_STACKABLE     (1u << 8)
#define D_TAG_ITEM_BULK          (1u << 9)
#define D_TAG_ITEM_RAW           (1u << 10)
#define D_TAG_CONTAINER_BULK     (1u << 12)
#define D_TAG_CONTAINER_SLOTS    (1u << 13)
#define D_TAG_PROCESS_CRAFT      (1u << 16)
#define D_TAG_PROCESS_TRANSFORM  (1u << 17)
#define D_TAG_PROCESS_EXTRACTION (1u << 18)
#define D_TAG_STRUCTURE_BUILDING (1u << 20)
#define D_TAG_STRUCTURE_TRANSPORT (1u << 21)
#define D_TAG_STRUCTURE_MACHINE  (1u << 22)
#define D_TAG_VEHICLE_SURFACE    (1u << 24)
#define D_TAG_VEHICLE_AIR        (1u << 25)
#define D_TAG_DEPOSIT_STRATA_SOLID (1u << 26)

typedef struct d_proto_material_s {
    d_material_id id;
    const char   *name;
    d_content_tag tags;

    /* Physical approximations; units not enforced here. */
    q16_16 density;
    q16_16 hardness;
    q16_16 melting_point;
} d_proto_material;

typedef struct d_proto_item_s {
    d_item_id     id;
    const char   *name;
    d_material_id material_id;
    d_content_tag tags;

    q16_16 unit_mass;    /* mass per item */
    q16_16 unit_volume;  /* volume per item */
} d_proto_item;

typedef struct d_proto_container_s {
    d_container_proto_id id;
    const char           *name;
    d_content_tag         tags;

    q16_16 max_volume;
    q16_16 max_mass;
    u16    slot_count;   /* 0 = bulk-only; >0 = slot-based */
} d_proto_container;

typedef struct d_proto_process_s {
    d_process_id  id;
    const char   *name;
    d_content_tag tags;

    /* TLV blob for generic I/O, rates, etc. Actual slots defined in data schema. */
    d_tlv_blob    params;
} d_proto_process;

typedef struct d_proto_deposit_s {
    d_deposit_proto_id id;
    const char        *name;

    d_material_id material_id;
    u16           model_id;     /* model proto id; interpretation left to data */
    d_content_tag tags;         /* STRATA_SOLID, RESERVOIR, etc. */

    d_tlv_blob   model_params;  /* per-model param blob */
} d_proto_deposit;

typedef struct d_proto_structure_s {
    d_structure_proto_id id;
    const char          *name;
    d_content_tag        tags;      /* BUILDING, MACHINE, TRANSPORT, etc. */

    /* Ports, IO, internal layout etc. encoded as TLV for extensibility. */
    d_tlv_blob   layout;
    d_tlv_blob   io;
    d_tlv_blob   processes;         /* which processes this structure runs */
} d_proto_structure;

typedef struct d_proto_vehicle_s {
    d_vehicle_proto_id id;
    const char        *name;
    d_content_tag      tags;
    d_tlv_blob         params;
} d_proto_vehicle;

typedef struct d_proto_spline_profile_s {
    d_spline_profile_id id;
    const char         *name;
    d_content_tag       tags;
    d_tlv_blob          params;
} d_proto_spline_profile;

typedef struct d_proto_job_template_s {
    d_job_template_id id;
    const char       *name;
    d_content_tag     tags;
    d_tlv_blob        params;
} d_proto_job_template;

typedef struct d_proto_building_s {
    d_building_proto_id id;
    const char         *name;
    d_content_tag       tags;
    d_tlv_blob          shell;
    d_tlv_blob          params;
} d_proto_building;

typedef struct d_proto_blueprint_s {
    d_blueprint_id  id;
    const char     *name;
    d_content_tag   tags;
    d_tlv_blob      contents;   /* describes one or more structures/vehicles/etc. */
} d_proto_blueprint;

typedef struct d_proto_pack_manifest_s {
    d_pack_id   id;
    u32         version;

    const char *name;
    const char *description;

    d_tlv_blob  content_tlv;
} d_proto_pack_manifest;

typedef struct d_proto_mod_manifest_s {
    d_mod_id    id;
    u32         version;

    const char *name;
    const char *description;

    /* Dependencies expressed as IDs/versions; TLV encoded for extensibility. */
    d_tlv_blob  deps_tlv;
    d_tlv_blob  content_tlv;
} d_proto_mod_manifest;

/* Initialize internal registries (materials, items, etc.). */
void d_content_init(void);

/* Clear all content registries (used when tearing down or reloading). */
void d_content_shutdown(void);

/* Reset registries to empty state. */
void d_content_reset(void);

/* Load a pack manifest and populate registries. Returns 0 on success. */
int d_content_load_pack(const d_proto_pack_manifest *m);

/* Load a mod manifest and populate registries. Returns 0 on success. */
int d_content_load_mod(const d_proto_mod_manifest *m);

/* Register all TLV schemas used by the content layer. Call once at startup. */
void d_content_register_schemas(void);

/* Validate loaded content graph; returns 0 on success. */
int d_content_validate_all(void);

/* Minimal registry getters */
const d_proto_material    *d_content_get_material(d_material_id id);
const d_proto_item        *d_content_get_item(d_item_id id);
const d_proto_container   *d_content_get_container(d_container_proto_id id);
const d_proto_process     *d_content_get_process(d_process_id id);
const d_proto_deposit     *d_content_get_deposit(d_deposit_proto_id id);
u32                        d_content_deposit_count(void);
const d_proto_deposit     *d_content_get_deposit_by_index(u32 index);
const d_proto_structure   *d_content_get_structure(d_structure_proto_id id);
const d_proto_vehicle     *d_content_get_vehicle(d_vehicle_proto_id id);
const d_proto_spline_profile *d_content_get_spline_profile(d_spline_profile_id id);
const d_proto_job_template *d_content_get_job_template(d_job_template_id id);
const d_proto_building    *d_content_get_building(d_building_proto_id id);
const d_proto_blueprint   *d_content_get_blueprint(d_blueprint_id id);
const d_proto_blueprint   *d_content_get_blueprint_by_name(const char *name);

u32 d_content_material_count(void);
const d_proto_material *d_content_get_material_by_index(u32 index);
u32 d_content_item_count(void);
const d_proto_item *d_content_get_item_by_index(u32 index);
u32 d_content_container_count(void);
const d_proto_container *d_content_get_container_by_index(u32 index);
u32 d_content_process_count(void);
const d_proto_process *d_content_get_process_by_index(u32 index);
u32 d_content_deposit_count(void);
const d_proto_deposit *d_content_get_deposit_by_index(u32 index);
u32 d_content_structure_count(void);
const d_proto_structure *d_content_get_structure_by_index(u32 index);
u32 d_content_vehicle_count(void);
const d_proto_vehicle *d_content_get_vehicle_by_index(u32 index);
u32 d_content_spline_profile_count(void);
const d_proto_spline_profile *d_content_get_spline_profile_by_index(u32 index);
u32 d_content_job_template_count(void);
const d_proto_job_template *d_content_get_job_template_by_index(u32 index);
u32 d_content_building_count(void);
const d_proto_building *d_content_get_building_by_index(u32 index);
u32 d_content_blueprint_count(void);
const d_proto_blueprint *d_content_get_blueprint_by_index(u32 index);

/* Debug helper to print counts and names. */
void d_content_debug_dump(void);

#ifdef __cplusplus
}
#endif

#endif /* D_CONTENT_H */
