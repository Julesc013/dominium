/* Content subsystem public interface (C89). */
#ifndef D_CONTENT_H
#define D_CONTENT_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "core/d_tlv_schema.h"
#include "core/d_registry.h"

#include "res/d_res_proto.h"
#include "struct/d_struct_proto.h"
#include "vehicle/d_vehicle_proto.h"
#include "trans/d_trans_proto.h"
#include "job/d_job_proto.h"
#include "build/d_build_proto.h"
#include "content/d_blueprint.h"

#ifdef __cplusplus
extern "C" {
#endif

/* TLV schema IDs for content layer. */
enum {
    D_TLV_SCHEMA_PACK_MANIFEST     = 0x0100,
    D_TLV_SCHEMA_MOD_MANIFEST      = 0x0101,
    D_TLV_SCHEMA_MATERIAL          = 0x0200,
    D_TLV_SCHEMA_ITEM              = 0x0201,
    D_TLV_SCHEMA_CONTAINER         = 0x0202,
    D_TLV_SCHEMA_PROCESS           = 0x0203,
    D_TLV_SCHEMA_DEPOSIT           = 0x0204,
    D_TLV_SCHEMA_STRUCTURE         = 0x0205,
    D_TLV_SCHEMA_MODULE            = 0x0206,
    D_TLV_SCHEMA_VEHICLE           = 0x0207,
    D_TLV_SCHEMA_SPLINE_PROFILE    = 0x0208,
    D_TLV_SCHEMA_JOB_TEMPLATE      = 0x0209,
    D_TLV_SCHEMA_BUILDING_PROTO    = 0x020A,
    D_TLV_SCHEMA_BLUEPRINT         = 0x020B
};

typedef struct d_content_dep {
    const char *id;          /* pack or mod id string */
    u32         min_version; /* inclusive; 0 means "no minimum" */
    u32         max_version; /* inclusive; 0 means "no maximum" */
} d_content_dep;

typedef struct d_proto_pack_manifest {
    const char *pack_id;
    u32         pack_version;

    const char *title;
    const char *author;

    u32         flags;       /* OFFICIAL, DLC, MOD_PACK, etc. */

    d_content_dep deps[16];  /* conservative fixed limit for now */
    u32           dep_count;

    /* Root TLV containing all content data for this pack. */
    d_tlv_blob    content_tlv;
} d_proto_pack_manifest;

typedef struct d_proto_mod_manifest {
    const char *mod_id;
    u32         mod_version;

    const char *title;
    const char *author;

    u32         flags;       /* CLIENT_ONLY, SERVER_ONLY, SCRIPTED, etc. */

    d_content_dep deps[16];
    u32           dep_count;

    /* Either embedded pack or explicit reference to a pack. For now, use TLV. */
    d_tlv_blob    base_pack_tlv;
    /* Extra metadata (scripts, model registrations, etc.) */
    d_tlv_blob    extra_tlv;
} d_proto_mod_manifest;

/* Result code enum for content loading operations. */
typedef enum d_content_result_e {
    D_CONTENT_OK = 0,
    D_CONTENT_ERR_SCHEMA = -1,
    D_CONTENT_ERR_DEP    = -2,
    D_CONTENT_ERR_REG    = -3,
    D_CONTENT_ERR_IO     = -4,
    D_CONTENT_ERR_UNKNOWN = -100
} d_content_result;

/*
 * Content subsystem top-level API:
 *
 * These APIs operate on TLV blobs and internal registries. File I/O is done
 * by a higher layer (launcher/setup/game), which provides already-loaded TLVs.
 */

/* Initialize internal registries (materials, items, etc.). */
void d_content_init(void);

/* Clear all content registries (used when tearing down or reloading). */
void d_content_shutdown(void);

/* Load a pack manifest and populate registries. */
d_content_result d_content_load_pack(
    const d_proto_pack_manifest *man
);

/* Load a mod manifest and populate registries (including embedded pack). */
d_content_result d_content_load_mod(
    const d_proto_mod_manifest *man
);

/* Register all TLV schemas used by the content layer. Call once at startup. */
void d_content_register_schemas(void);

/* Minimal registry getters */
const d_proto_material *d_content_get_material(d_material_id id);
const d_proto_item     *d_content_get_item(d_item_id id);
const d_proto_container *d_content_get_container(d_container_proto_id id);
const d_proto_process  *d_content_get_process(d_process_id id);
const d_proto_deposit  *d_content_get_deposit(d_deposit_id id);
const d_proto_structure *d_content_get_structure(d_structure_id id);
const d_proto_module   *d_content_get_module(d_module_proto_id id);
const d_proto_vehicle  *d_content_get_vehicle(d_vehicle_proto_id id);
const d_proto_spline_profile *d_content_get_spline_profile(d_spline_profile_id id);
const d_proto_job_template *d_content_get_job_template(d_job_template_id id);
const d_proto_building *d_content_get_building(d_building_proto_id id);

#ifdef __cplusplus
}
#endif

#endif /* D_CONTENT_H */
