#include <stdio.h>
#include <string.h>

#include "content/d_content.h"
#include "content/d_content_tags.h"

#include "core/d_registry.h"
#include "core/d_tlv_schema.h"
#include "content/d_blueprint.h"

/* Registry capacities */
#define D_CONTENT_MAX_MATERIALS       4096u
#define D_CONTENT_MAX_ITEMS           8192u
#define D_CONTENT_MAX_CONTAINERS      2048u
#define D_CONTENT_MAX_PROCESSES       4096u
#define D_CONTENT_MAX_DEPOSITS        4096u
#define D_CONTENT_MAX_STRUCTURES      2048u
#define D_CONTENT_MAX_MODULES         4096u
#define D_CONTENT_MAX_VEHICLES        2048u
#define D_CONTENT_MAX_SPLINE_PROFILES 2048u
#define D_CONTENT_MAX_JOB_TEMPLATES   4096u
#define D_CONTENT_MAX_BUILDINGS       2048u

/* Registries and storage */
static d_registry g_material_registry;
static d_registry_entry g_material_entries[D_CONTENT_MAX_MATERIALS];
static d_proto_material g_material_storage[D_CONTENT_MAX_MATERIALS];

static d_registry g_item_registry;
static d_registry_entry g_item_entries[D_CONTENT_MAX_ITEMS];
static d_proto_item g_item_storage[D_CONTENT_MAX_ITEMS];

static d_registry g_container_registry;
static d_registry_entry g_container_entries[D_CONTENT_MAX_CONTAINERS];
static d_proto_container g_container_storage[D_CONTENT_MAX_CONTAINERS];

static d_registry g_process_registry;
static d_registry_entry g_process_entries[D_CONTENT_MAX_PROCESSES];
static d_proto_process g_process_storage[D_CONTENT_MAX_PROCESSES];

static d_registry g_deposit_registry;
static d_registry_entry g_deposit_entries[D_CONTENT_MAX_DEPOSITS];
static d_proto_deposit g_deposit_storage[D_CONTENT_MAX_DEPOSITS];

static d_registry g_structure_registry;
static d_registry_entry g_structure_entries[D_CONTENT_MAX_STRUCTURES];
static d_proto_structure g_structure_storage[D_CONTENT_MAX_STRUCTURES];

static d_registry g_module_registry;
static d_registry_entry g_module_entries[D_CONTENT_MAX_MODULES];
static d_proto_module g_module_storage[D_CONTENT_MAX_MODULES];

static d_registry g_vehicle_registry;
static d_registry_entry g_vehicle_entries[D_CONTENT_MAX_VEHICLES];
static d_proto_vehicle g_vehicle_storage[D_CONTENT_MAX_VEHICLES];

static d_registry g_spline_profile_registry;
static d_registry_entry g_spline_profile_entries[D_CONTENT_MAX_SPLINE_PROFILES];
static d_proto_spline_profile g_spline_profile_storage[D_CONTENT_MAX_SPLINE_PROFILES];

static d_registry g_job_template_registry;
static d_registry_entry g_job_template_entries[D_CONTENT_MAX_JOB_TEMPLATES];
static d_proto_job_template g_job_template_storage[D_CONTENT_MAX_JOB_TEMPLATES];

static d_registry g_building_registry;
static d_registry_entry g_building_entries[D_CONTENT_MAX_BUILDINGS];
static d_proto_building g_building_storage[D_CONTENT_MAX_BUILDINGS];

/* Forward declarations */
static d_content_result d_content_load_content_blob(const d_tlv_blob *blob);
static d_content_result d_content_load_materials_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_items_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_containers_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_processes_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_deposits_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_structures_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_modules_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_vehicles_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_spline_profiles_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_job_templates_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_buildings_from_tlv(const d_tlv_blob *blob);
static d_content_result d_content_load_blueprints_from_tlv(const d_tlv_blob *blob);

static int d_content_validate_basic(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
);

void d_content_init(void)
{
    d_registry_init(&g_material_registry,  g_material_entries,  D_CONTENT_MAX_MATERIALS,  1u);
    d_registry_init(&g_item_registry,      g_item_entries,      D_CONTENT_MAX_ITEMS,      1u);
    d_registry_init(&g_container_registry, g_container_entries, D_CONTENT_MAX_CONTAINERS, 1u);
    d_registry_init(&g_process_registry,   g_process_entries,   D_CONTENT_MAX_PROCESSES,  1u);
    d_registry_init(&g_deposit_registry,   g_deposit_entries,   D_CONTENT_MAX_DEPOSITS,   1u);
    d_registry_init(&g_structure_registry, g_structure_entries, D_CONTENT_MAX_STRUCTURES, 1u);
    d_registry_init(&g_module_registry,    g_module_entries,    D_CONTENT_MAX_MODULES,    1u);
    d_registry_init(&g_vehicle_registry,   g_vehicle_entries,   D_CONTENT_MAX_VEHICLES,   1u);
    d_registry_init(&g_spline_profile_registry, g_spline_profile_entries, D_CONTENT_MAX_SPLINE_PROFILES, 1u);
    d_registry_init(&g_job_template_registry,   g_job_template_entries,   D_CONTENT_MAX_JOB_TEMPLATES,   1u);
    d_registry_init(&g_building_registry,  g_building_entries,  D_CONTENT_MAX_BUILDINGS,  1u);

    d_blueprint_register_builtin_kinds();
}

void d_content_shutdown(void)
{
    memset(g_material_storage, 0, sizeof(g_material_storage));
    memset(g_item_storage, 0, sizeof(g_item_storage));
    memset(g_container_storage, 0, sizeof(g_container_storage));
    memset(g_process_storage, 0, sizeof(g_process_storage));
    memset(g_deposit_storage, 0, sizeof(g_deposit_storage));
    memset(g_structure_storage, 0, sizeof(g_structure_storage));
    memset(g_module_storage, 0, sizeof(g_module_storage));
    memset(g_vehicle_storage, 0, sizeof(g_vehicle_storage));
    memset(g_spline_profile_storage, 0, sizeof(g_spline_profile_storage));
    memset(g_job_template_storage, 0, sizeof(g_job_template_storage));
    memset(g_building_storage, 0, sizeof(g_building_storage));

    d_content_init();
}

static int d_content_register_schema(d_tlv_schema_id schema_id, u16 version)
{
    d_tlv_schema_desc desc;
    desc.schema_id = schema_id;
    desc.version = version;
    desc.validate_fn = d_content_validate_basic;
    return d_tlv_schema_register(&desc);
}

void d_content_register_schemas(void)
{
    /* Manifest schemas */
    (void)d_content_register_schema(D_TLV_SCHEMA_PACK_MANIFEST, 1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_MOD_MANIFEST,  1u);

    /* Proto schemas */
    (void)d_content_register_schema(D_TLV_SCHEMA_MATERIAL,       1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_ITEM,           1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_CONTAINER,      1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_PROCESS,        1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_DEPOSIT,        1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_STRUCTURE,      1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_MODULE,         1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_VEHICLE,        1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_SPLINE_PROFILE, 1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_JOB_TEMPLATE,   1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_BUILDING_PROTO, 1u);
    (void)d_content_register_schema(D_TLV_SCHEMA_BLUEPRINT,      1u);
}

static int d_content_validate_basic(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
)
{
    (void)schema_id;
    (void)version;
    (void)out_upgraded;
    if (!in) {
        return -1;
    }
    if (in->len == 0u || in->ptr == (unsigned char *)0) {
        return -1;
    }
    if (in->len < 8u) {
        /* Ensure at least one TLV header exists. */
        return -1;
    }
    /* TODO: Implement strict field validation and upgrade paths per schema. */
    return 0;
}

static d_content_result d_content_load_manifest_blob(
    const d_tlv_blob *blob,
    d_tlv_schema_id   schema_id
)
{
    int rc;
    d_tlv_blob upgraded;
    upgraded.ptr = (unsigned char *)0;
    upgraded.len = 0u;

    rc = d_tlv_schema_validate(schema_id, 1u, blob, &upgraded);
    if (rc != 0) {
        return D_CONTENT_ERR_SCHEMA;
    }
    /* TODO: handle upgraded blob lifetime if future upgrade logic is added. */
    return D_CONTENT_OK;
}

d_content_result d_content_load_pack(
    const d_proto_pack_manifest *man
)
{
    d_content_result rc;
    if (!man) {
        return D_CONTENT_ERR_SCHEMA;
    }

    rc = d_content_load_manifest_blob(&man->content_tlv, D_TLV_SCHEMA_PACK_MANIFEST);
    if (rc != D_CONTENT_OK) {
        return rc;
    }

    rc = d_content_load_content_blob(&man->content_tlv);
    if (rc != D_CONTENT_OK) {
        return rc;
    }

    return D_CONTENT_OK;
}

d_content_result d_content_load_mod(
    const d_proto_mod_manifest *man
)
{
    d_content_result rc;
    if (!man) {
        return D_CONTENT_ERR_SCHEMA;
    }

    rc = d_content_load_manifest_blob(&man->extra_tlv, D_TLV_SCHEMA_MOD_MANIFEST);
    if (rc != D_CONTENT_OK) {
        return rc;
    }

    /* Validate embedded pack blob using pack schema. */
    rc = d_content_load_manifest_blob(&man->base_pack_tlv, D_TLV_SCHEMA_PACK_MANIFEST);
    if (rc != D_CONTENT_OK) {
        return rc;
    }

    rc = d_content_load_content_blob(&man->base_pack_tlv);
    if (rc != D_CONTENT_OK) {
        return rc;
    }

    /* TODO: apply extra_tlv metadata (scripts, model registrations, etc.). */
    return D_CONTENT_OK;
}

static d_content_result d_content_load_content_blob(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob) {
        return D_CONTENT_ERR_SCHEMA;
    }
    if (!blob->ptr || blob->len == 0u) {
        return D_CONTENT_OK;
    }

    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        d_content_result rc = D_CONTENT_OK;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }

        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;

        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        switch (tag) {
            case D_CONTENT_TAG_MATERIALS:
                rc = d_content_load_materials_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_ITEMS:
                rc = d_content_load_items_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_CONTAINERS:
                rc = d_content_load_containers_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_PROCESSES:
                rc = d_content_load_processes_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_DEPOSITS:
                rc = d_content_load_deposits_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_STRUCTURES:
                rc = d_content_load_structures_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_MODULES:
                rc = d_content_load_modules_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_VEHICLES:
                rc = d_content_load_vehicles_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_SPLINE_PROFILES:
                rc = d_content_load_spline_profiles_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_JOB_TEMPLATES:
                rc = d_content_load_job_templates_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_BUILDINGS:
                rc = d_content_load_buildings_from_tlv(&payload);
                break;
            case D_CONTENT_TAG_BLUEPRINTS:
                rc = d_content_load_blueprints_from_tlv(&payload);
                break;
            default:
                /* Unknown section; ignore for forward compatibility. */
                break;
        }

        if (rc != D_CONTENT_OK) {
            return rc;
        }
    }

    return D_CONTENT_OK;
}

static d_content_result d_content_load_materials_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_material *mat;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag; /* tag reserved for future use */
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_MATERIAL, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_material_registry.count >= D_CONTENT_MAX_MATERIALS) {
            return D_CONTENT_ERR_REG;
        }
        mat = &g_material_storage[g_material_registry.count];
        memset(mat, 0, sizeof(*mat));
        mat->extra = payload;
        /* TODO: parse fields from payload TLV once schema is defined. */
        id = d_registry_add(&g_material_registry, mat);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        mat->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_items_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_item *it;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_ITEM, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_item_registry.count >= D_CONTENT_MAX_ITEMS) {
            return D_CONTENT_ERR_REG;
        }
        it = &g_item_storage[g_item_registry.count];
        memset(it, 0, sizeof(*it));
        it->extra = payload;
        /* TODO: parse item fields from payload TLV. */
        id = d_registry_add(&g_item_registry, it);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        it->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_containers_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_container *ct;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_CONTAINER, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_container_registry.count >= D_CONTENT_MAX_CONTAINERS) {
            return D_CONTENT_ERR_REG;
        }
        ct = &g_container_storage[g_container_registry.count];
        memset(ct, 0, sizeof(*ct));
        ct->extra = payload;
        /* TODO: parse container fields from payload TLV. */
        id = d_registry_add(&g_container_registry, ct);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        ct->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_processes_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_process *proc;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_PROCESS, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_process_registry.count >= D_CONTENT_MAX_PROCESSES) {
            return D_CONTENT_ERR_REG;
        }
        proc = &g_process_storage[g_process_registry.count];
        memset(proc, 0, sizeof(*proc));
        proc->extra = payload;
        /* TODO: parse process inputs/outputs from payload TLV. */
        id = d_registry_add(&g_process_registry, proc);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        proc->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_deposits_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_deposit *dep;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_DEPOSIT, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_deposit_registry.count >= D_CONTENT_MAX_DEPOSITS) {
            return D_CONTENT_ERR_REG;
        }
        dep = &g_deposit_storage[g_deposit_registry.count];
        memset(dep, 0, sizeof(*dep));
        dep->params = payload;
        /* TODO: parse deposit fields; payload currently captured in params. */
        id = d_registry_add(&g_deposit_registry, dep);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        dep->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_structures_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_structure *st;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_STRUCTURE, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_structure_registry.count >= D_CONTENT_MAX_STRUCTURES) {
            return D_CONTENT_ERR_REG;
        }
        st = &g_structure_storage[g_structure_registry.count];
        memset(st, 0, sizeof(*st));
        st->extra = payload;
        /* TODO: parse structure ports and process lists from payload TLV. */
        id = d_registry_add(&g_structure_registry, st);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        st->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_modules_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_module *mod;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_MODULE, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_module_registry.count >= D_CONTENT_MAX_MODULES) {
            return D_CONTENT_ERR_REG;
        }
        mod = &g_module_storage[g_module_registry.count];
        memset(mod, 0, sizeof(*mod));
        mod->params = payload;
        /* TODO: parse module fields from payload TLV. */
        id = d_registry_add(&g_module_registry, mod);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        mod->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_vehicles_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_vehicle *veh;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_VEHICLE, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_vehicle_registry.count >= D_CONTENT_MAX_VEHICLES) {
            return D_CONTENT_ERR_REG;
        }
        veh = &g_vehicle_storage[g_vehicle_registry.count];
        memset(veh, 0, sizeof(*veh));
        veh->extra = payload;
        /* TODO: parse vehicle modules/layouts from payload TLV. */
        id = d_registry_add(&g_vehicle_registry, veh);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        veh->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_spline_profiles_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_spline_profile *sp;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_SPLINE_PROFILE, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_spline_profile_registry.count >= D_CONTENT_MAX_SPLINE_PROFILES) {
            return D_CONTENT_ERR_REG;
        }
        sp = &g_spline_profile_storage[g_spline_profile_registry.count];
        memset(sp, 0, sizeof(*sp));
        sp->extra = payload;
        /* TODO: parse spline profile fields from payload TLV. */
        id = d_registry_add(&g_spline_profile_registry, sp);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        sp->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_job_templates_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_job_template *jt;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_JOB_TEMPLATE, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_job_template_registry.count >= D_CONTENT_MAX_JOB_TEMPLATES) {
            return D_CONTENT_ERR_REG;
        }
        jt = &g_job_template_storage[g_job_template_registry.count];
        memset(jt, 0, sizeof(*jt));
        jt->params = payload;
        /* TODO: parse job template fields from payload TLV. */
        id = d_registry_add(&g_job_template_registry, jt);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        jt->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_buildings_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        d_proto_building *bld;
        u32 id;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        (void)tag;
        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_BUILDING_PROTO, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        if (g_building_registry.count >= D_CONTENT_MAX_BUILDINGS) {
            return D_CONTENT_ERR_REG;
        }
        bld = &g_building_storage[g_building_registry.count];
        memset(bld, 0, sizeof(*bld));
        bld->extra = payload;
        /* TODO: parse building proto fields from payload TLV. */
        id = d_registry_add(&g_building_registry, bld);
        if (id == 0u) {
            return D_CONTENT_ERR_REG;
        }
        bld->id = id;
    }
    return D_CONTENT_OK;
}

static d_content_result d_content_load_blueprints_from_tlv(const d_tlv_blob *blob)
{
    u32 offset;
    if (!blob || blob->ptr == (unsigned char *)0) {
        return D_CONTENT_OK;
    }
    offset = 0u;
    while (offset < blob->len) {
        u32 remaining = blob->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        int vrc;
        (void)tag;

        if (remaining < 8u) {
            return D_CONTENT_ERR_SCHEMA;
        }
        memcpy(&tag, blob->ptr + offset, sizeof(u32));
        memcpy(&len, blob->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > blob->len - offset) {
            return D_CONTENT_ERR_SCHEMA;
        }
        payload.ptr = blob->ptr + offset;
        payload.len = len;
        offset += len;

        vrc = d_tlv_schema_validate(D_TLV_SCHEMA_BLUEPRINT, 1u, &payload, (d_tlv_blob *)0);
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }

        /* TODO: parse blueprint header, dispatch to kind validate/compile. */
        vrc = 0;
        if (vrc != 0) {
            return D_CONTENT_ERR_SCHEMA;
        }
    }
    return D_CONTENT_OK;
}

/* Registry getters */
const d_proto_material *d_content_get_material(d_material_id id)
{
    return (const d_proto_material *)d_registry_get(&g_material_registry, id);
}

const d_proto_item *d_content_get_item(d_item_id id)
{
    return (const d_proto_item *)d_registry_get(&g_item_registry, id);
}

const d_proto_container *d_content_get_container(d_container_proto_id id)
{
    return (const d_proto_container *)d_registry_get(&g_container_registry, id);
}

const d_proto_process *d_content_get_process(d_process_id id)
{
    return (const d_proto_process *)d_registry_get(&g_process_registry, id);
}

const d_proto_deposit *d_content_get_deposit(d_deposit_id id)
{
    return (const d_proto_deposit *)d_registry_get(&g_deposit_registry, id);
}

const d_proto_structure *d_content_get_structure(d_structure_id id)
{
    return (const d_proto_structure *)d_registry_get(&g_structure_registry, id);
}

const d_proto_module *d_content_get_module(d_module_proto_id id)
{
    return (const d_proto_module *)d_registry_get(&g_module_registry, id);
}

const d_proto_vehicle *d_content_get_vehicle(d_vehicle_proto_id id)
{
    return (const d_proto_vehicle *)d_registry_get(&g_vehicle_registry, id);
}

const d_proto_spline_profile *d_content_get_spline_profile(d_spline_profile_id id)
{
    return (const d_proto_spline_profile *)d_registry_get(&g_spline_profile_registry, id);
}

const d_proto_job_template *d_content_get_job_template(d_job_template_id id)
{
    return (const d_proto_job_template *)d_registry_get(&g_job_template_registry, id);
}

const d_proto_building *d_content_get_building(d_building_proto_id id)
{
    return (const d_proto_building *)d_registry_get(&g_building_registry, id);
}
