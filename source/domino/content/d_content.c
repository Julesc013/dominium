#include <stdio.h>
#include <string.h>

#include "content/d_content.h"
#include "content/d_content_schema.h"

#include "core/d_registry.h"
#include "core/d_tlv_schema.h"

/* Registry capacities */
#define D_CONTENT_MAX_MATERIALS       4096u
#define D_CONTENT_MAX_ITEMS           8192u
#define D_CONTENT_MAX_CONTAINERS      2048u
#define D_CONTENT_MAX_PROCESSES       4096u
#define D_CONTENT_MAX_PROCESS_IO_TERMS 65536u
#define D_CONTENT_MAX_DEPOSITS        4096u
#define D_CONTENT_MAX_STRUCTURES      2048u
#define D_CONTENT_MAX_VEHICLES        2048u
#define D_CONTENT_MAX_SPLINE_PROFILES 2048u
#define D_CONTENT_MAX_JOB_TEMPLATES   4096u
#define D_CONTENT_MAX_BUILDINGS       2048u
#define D_CONTENT_MAX_BLUEPRINTS      4096u

static const char *D_CONTENT_EMPTY_STRING = "";

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
static d_process_io_term g_process_io_terms[D_CONTENT_MAX_PROCESS_IO_TERMS];
static u32 g_process_io_term_count = 0u;

static d_registry g_deposit_registry;
static d_registry_entry g_deposit_entries[D_CONTENT_MAX_DEPOSITS];
static d_proto_deposit g_deposit_storage[D_CONTENT_MAX_DEPOSITS];

static d_registry g_structure_registry;
static d_registry_entry g_structure_entries[D_CONTENT_MAX_STRUCTURES];
static d_proto_structure g_structure_storage[D_CONTENT_MAX_STRUCTURES];

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

static d_registry g_blueprint_registry;
static d_registry_entry g_blueprint_entries[D_CONTENT_MAX_BLUEPRINTS];
static d_proto_blueprint g_blueprint_storage[D_CONTENT_MAX_BLUEPRINTS];

/* Forward declarations */
static int d_content_load_content_blob(const d_tlv_blob *blob);
static int d_content_register_material(const d_proto_material *src);
static int d_content_register_item(const d_proto_item *src);
static int d_content_register_container(const d_proto_container *src);
static int d_content_register_process(const d_proto_process *src);
static int d_content_register_deposit(const d_proto_deposit *src);
static int d_content_register_structure(const d_proto_structure *src);
static int d_content_register_vehicle(const d_proto_vehicle *src);
static int d_content_register_spline(const d_proto_spline_profile *src);
static int d_content_register_job_template(const d_proto_job_template *src);
static int d_content_register_building(const d_proto_building *src);
static int d_content_register_blueprint(const d_proto_blueprint *src);
static int d_content_read_tlv(const d_tlv_blob *blob, u32 *offset, u32 *tag, d_tlv_blob *payload);

static void d_content_clear_storage(void)
{
    memset(g_material_entries, 0, sizeof(g_material_entries));
    memset(g_material_storage, 0, sizeof(g_material_storage));

    memset(g_item_entries, 0, sizeof(g_item_entries));
    memset(g_item_storage, 0, sizeof(g_item_storage));

    memset(g_container_entries, 0, sizeof(g_container_entries));
    memset(g_container_storage, 0, sizeof(g_container_storage));

    memset(g_process_entries, 0, sizeof(g_process_entries));
    memset(g_process_storage, 0, sizeof(g_process_storage));
    memset(g_process_io_terms, 0, sizeof(g_process_io_terms));
    g_process_io_term_count = 0u;

    memset(g_deposit_entries, 0, sizeof(g_deposit_entries));
    memset(g_deposit_storage, 0, sizeof(g_deposit_storage));

    memset(g_structure_entries, 0, sizeof(g_structure_entries));
    memset(g_structure_storage, 0, sizeof(g_structure_storage));

    memset(g_vehicle_entries, 0, sizeof(g_vehicle_entries));
    memset(g_vehicle_storage, 0, sizeof(g_vehicle_storage));

    memset(g_spline_profile_entries, 0, sizeof(g_spline_profile_entries));
    memset(g_spline_profile_storage, 0, sizeof(g_spline_profile_storage));

    memset(g_job_template_entries, 0, sizeof(g_job_template_entries));
    memset(g_job_template_storage, 0, sizeof(g_job_template_storage));

    memset(g_building_entries, 0, sizeof(g_building_entries));
    memset(g_building_storage, 0, sizeof(g_building_storage));

    memset(g_blueprint_entries, 0, sizeof(g_blueprint_entries));
    memset(g_blueprint_storage, 0, sizeof(g_blueprint_storage));
}

static void d_content_init_registries(void)
{
    d_registry_init(&g_material_registry,  g_material_entries,  D_CONTENT_MAX_MATERIALS,  1u);
    d_registry_init(&g_item_registry,      g_item_entries,      D_CONTENT_MAX_ITEMS,      1u);
    d_registry_init(&g_container_registry, g_container_entries, D_CONTENT_MAX_CONTAINERS, 1u);
    d_registry_init(&g_process_registry,   g_process_entries,   D_CONTENT_MAX_PROCESSES,  1u);
    d_registry_init(&g_deposit_registry,   g_deposit_entries,   D_CONTENT_MAX_DEPOSITS,   1u);
    d_registry_init(&g_structure_registry, g_structure_entries, D_CONTENT_MAX_STRUCTURES, 1u);
    d_registry_init(&g_vehicle_registry,   g_vehicle_entries,   D_CONTENT_MAX_VEHICLES,   1u);
    d_registry_init(&g_spline_profile_registry, g_spline_profile_entries, D_CONTENT_MAX_SPLINE_PROFILES, 1u);
    d_registry_init(&g_job_template_registry,   g_job_template_entries,   D_CONTENT_MAX_JOB_TEMPLATES,   1u);
    d_registry_init(&g_building_registry,  g_building_entries,  D_CONTENT_MAX_BUILDINGS,  1u);
    d_registry_init(&g_blueprint_registry, g_blueprint_entries, D_CONTENT_MAX_BLUEPRINTS, 1u);
}

void d_content_init(void)
{
    d_content_clear_storage();
    d_content_init_registries();
}

void d_content_shutdown(void)
{
    d_content_clear_storage();
    d_content_init_registries();
}

void d_content_reset(void)
{
    d_content_shutdown();
}

void d_content_register_schemas(void)
{
    (void)d_content_schema_register_all();
}

static const char *d_content_safe_name(const char *name)
{
    if (!name) {
        return D_CONTENT_EMPTY_STRING;
    }
    return name;
}

static int d_content_register_material(const d_proto_material *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_material_registry.count;
    if (slot >= D_CONTENT_MAX_MATERIALS) {
        return -1;
    }
    g_material_storage[slot] = *src;
    g_material_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_material_registry, src->id, &g_material_storage[slot]) == 0u) {
        memset(&g_material_storage[slot], 0, sizeof(g_material_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_item(const d_proto_item *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_item_registry.count;
    if (slot >= D_CONTENT_MAX_ITEMS) {
        return -1;
    }
    g_item_storage[slot] = *src;
    g_item_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_item_registry, src->id, &g_item_storage[slot]) == 0u) {
        memset(&g_item_storage[slot], 0, sizeof(g_item_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_container(const d_proto_container *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_container_registry.count;
    if (slot >= D_CONTENT_MAX_CONTAINERS) {
        return -1;
    }
    g_container_storage[slot] = *src;
    g_container_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_container_registry, src->id, &g_container_storage[slot]) == 0u) {
        memset(&g_container_storage[slot], 0, sizeof(g_container_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_process(const d_proto_process *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_process_registry.count;
    if (slot >= D_CONTENT_MAX_PROCESSES) {
        return -1;
    }
    g_process_storage[slot] = *src;
    g_process_storage[slot].name = d_content_safe_name(src->name);
    if (src->io_count > 0u && src->io_terms) {
        u32 needed = (u32)src->io_count;
        u32 base = g_process_io_term_count;
        if (base > D_CONTENT_MAX_PROCESS_IO_TERMS || needed > (D_CONTENT_MAX_PROCESS_IO_TERMS - base)) {
            memset(&g_process_storage[slot], 0, sizeof(g_process_storage[slot]));
            return -1;
        }
        memcpy(&g_process_io_terms[base], src->io_terms, sizeof(d_process_io_term) * needed);
        g_process_storage[slot].io_terms = &g_process_io_terms[base];
        g_process_io_term_count = base + needed;
    } else {
        g_process_storage[slot].io_count = 0u;
        g_process_storage[slot].io_terms = (d_process_io_term *)0;
    }
    if (d_registry_add_with_id(&g_process_registry, src->id, &g_process_storage[slot]) == 0u) {
        memset(&g_process_storage[slot], 0, sizeof(g_process_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_deposit(const d_proto_deposit *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_deposit_registry.count;
    if (slot >= D_CONTENT_MAX_DEPOSITS) {
        return -1;
    }
    g_deposit_storage[slot] = *src;
    g_deposit_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_deposit_registry, src->id, &g_deposit_storage[slot]) == 0u) {
        memset(&g_deposit_storage[slot], 0, sizeof(g_deposit_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_structure(const d_proto_structure *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_structure_registry.count;
    if (slot >= D_CONTENT_MAX_STRUCTURES) {
        return -1;
    }
    g_structure_storage[slot] = *src;
    g_structure_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_structure_registry, src->id, &g_structure_storage[slot]) == 0u) {
        memset(&g_structure_storage[slot], 0, sizeof(g_structure_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_vehicle(const d_proto_vehicle *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_vehicle_registry.count;
    if (slot >= D_CONTENT_MAX_VEHICLES) {
        return -1;
    }
    g_vehicle_storage[slot] = *src;
    g_vehicle_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_vehicle_registry, src->id, &g_vehicle_storage[slot]) == 0u) {
        memset(&g_vehicle_storage[slot], 0, sizeof(g_vehicle_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_spline(const d_proto_spline_profile *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_spline_profile_registry.count;
    if (slot >= D_CONTENT_MAX_SPLINE_PROFILES) {
        return -1;
    }
    g_spline_profile_storage[slot] = *src;
    g_spline_profile_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_spline_profile_registry, src->id, &g_spline_profile_storage[slot]) == 0u) {
        memset(&g_spline_profile_storage[slot], 0, sizeof(g_spline_profile_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_job_template(const d_proto_job_template *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_job_template_registry.count;
    if (slot >= D_CONTENT_MAX_JOB_TEMPLATES) {
        return -1;
    }
    g_job_template_storage[slot] = *src;
    g_job_template_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_job_template_registry, src->id, &g_job_template_storage[slot]) == 0u) {
        memset(&g_job_template_storage[slot], 0, sizeof(g_job_template_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_building(const d_proto_building *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_building_registry.count;
    if (slot >= D_CONTENT_MAX_BUILDINGS) {
        return -1;
    }
    g_building_storage[slot] = *src;
    g_building_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_building_registry, src->id, &g_building_storage[slot]) == 0u) {
        memset(&g_building_storage[slot], 0, sizeof(g_building_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_register_blueprint(const d_proto_blueprint *src)
{
    u32 slot;
    if (!src) {
        return -1;
    }
    slot = g_blueprint_registry.count;
    if (slot >= D_CONTENT_MAX_BLUEPRINTS) {
        return -1;
    }
    g_blueprint_storage[slot] = *src;
    g_blueprint_storage[slot].name = d_content_safe_name(src->name);
    if (d_registry_add_with_id(&g_blueprint_registry, src->id, &g_blueprint_storage[slot]) == 0u) {
        memset(&g_blueprint_storage[slot], 0, sizeof(g_blueprint_storage[slot]));
        return -1;
    }
    return 0;
}

static int d_content_read_tlv(const d_tlv_blob *blob,
                              u32 *offset,
                              u32 *tag,
                              d_tlv_blob *payload)
{
    u32 remaining;
    u32 len;
    if (!blob || !offset || !tag || !payload) {
        return -1;
    }
    if (*offset >= blob->len) {
        return 1; /* end-of-blob */
    }
    remaining = blob->len - *offset;
    if (remaining < 8u) {
        return -1;
    }
    memcpy(tag, blob->ptr + *offset, sizeof(u32));
    memcpy(&len, blob->ptr + *offset + 4u, sizeof(u32));
    *offset += 8u;
    if (len > blob->len - *offset) {
        return -1;
    }
    payload->ptr = blob->ptr + *offset;
    payload->len = len;
    *offset += len;
    return 0;
}

static int d_content_load_content_blob(const d_tlv_blob *blob)
{
    u32 offset = 0u;
    u32 schema_id;
    d_tlv_blob payload;

    if (!blob) {
        return -1;
    }
    if (!blob->ptr || blob->len == 0u) {
        return 0;
    }

    while (1) {
        int rc = d_content_read_tlv(blob, &offset, &schema_id, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (schema_id) {
        case D_TLV_SCHEMA_MATERIAL_V1: {
            d_proto_material mat;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_material_v1(&payload, &mat) != 0) return -1;
            if (d_content_register_material(&mat) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_ITEM_V1: {
            d_proto_item it;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_item_v1(&payload, &it) != 0) return -1;
            if (d_content_register_item(&it) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_CONTAINER_V1: {
            d_proto_container ct;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_container_v1(&payload, &ct) != 0) return -1;
            if (d_content_register_container(&ct) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_PROCESS_V1: {
            d_proto_process proc;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_process_v1(&payload, &proc) != 0) return -1;
            if (d_content_register_process(&proc) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_DEPOSIT_V1: {
            d_proto_deposit dep;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_deposit_v1(&payload, &dep) != 0) return -1;
            if (d_content_register_deposit(&dep) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_STRUCTURE_V1: {
            d_proto_structure st;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_structure_v1(&payload, &st) != 0) return -1;
            if (d_content_register_structure(&st) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_VEHICLE_V1: {
            d_proto_vehicle veh;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_vehicle_v1(&payload, &veh) != 0) return -1;
            if (d_content_register_vehicle(&veh) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_SPLINE_V1: {
            d_proto_spline_profile sp;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_spline_v1(&payload, &sp) != 0) return -1;
            if (d_content_register_spline(&sp) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_JOB_TEMPLATE_V1: {
            d_proto_job_template jt;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_job_template_v1(&payload, &jt) != 0) return -1;
            if (d_content_register_job_template(&jt) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_BUILDING_V1: {
            d_proto_building bld;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_building_v1(&payload, &bld) != 0) return -1;
            if (d_content_register_building(&bld) != 0) return -1;
            break;
        }
        case D_TLV_SCHEMA_BLUEPRINT_V1: {
            d_proto_blueprint bp;
            if (d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &payload, (d_tlv_blob *)0) != 0) return -1;
            if (d_content_schema_parse_blueprint_v1(&payload, &bp) != 0) return -1;
            if (d_content_register_blueprint(&bp) != 0) return -1;
            break;
        }
        default:
            /* Unknown schema id; skip for forward compatibility. */
            break;
        }
    }
    return 0;
}

int d_content_load_pack(const d_proto_pack_manifest *m)
{
    d_proto_pack_manifest parsed;
    d_tlv_blob content_blob;

    if (!m) {
        return -1;
    }

    content_blob = m->content_tlv;
    if (m->content_tlv.ptr && m->content_tlv.len >= 8u) {
        if (d_content_schema_parse_pack_v1(&m->content_tlv, &parsed) == 0) {
            if (parsed.content_tlv.ptr || parsed.content_tlv.len != 0u) {
                content_blob = parsed.content_tlv;
            }
        }
    }

    if (d_content_load_content_blob(&content_blob) != 0) {
        return -1;
    }
    return 0;
}

int d_content_load_mod(const d_proto_mod_manifest *m)
{
    d_proto_mod_manifest parsed;
    d_tlv_blob content_blob;

    if (!m) {
        return -1;
    }

    content_blob = m->content_tlv;
    if (m->content_tlv.ptr && m->content_tlv.len >= 8u) {
        if (d_content_schema_parse_mod_v1(&m->content_tlv, &parsed) == 0) {
            if (parsed.content_tlv.ptr || parsed.content_tlv.len != 0u) {
                content_blob = parsed.content_tlv;
            }
        }
    }

    if (d_content_load_content_blob(&content_blob) != 0) {
        return -1;
    }
    return 0;
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

const d_proto_deposit *d_content_get_deposit(d_deposit_proto_id id)
{
    return (const d_proto_deposit *)d_registry_get(&g_deposit_registry, id);
}

u32 d_content_deposit_count(void)
{
    return g_deposit_registry.count;
}

const d_proto_deposit *d_content_get_deposit_by_index(u32 index)
{
    if (index >= g_deposit_registry.count) {
        return (const d_proto_deposit *)0;
    }
    return (const d_proto_deposit *)g_deposit_registry.entries[index].ptr;
}

const d_proto_structure *d_content_get_structure(d_structure_proto_id id)
{
    return (const d_proto_structure *)d_registry_get(&g_structure_registry, id);
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

const d_proto_blueprint *d_content_get_blueprint(d_blueprint_id id)
{
    return (const d_proto_blueprint *)d_registry_get(&g_blueprint_registry, id);
}

const d_proto_blueprint *d_content_get_blueprint_by_name(const char *name)
{
    u32 i;
    if (!name || !name[0]) {
        return (const d_proto_blueprint *)0;
    }
    for (i = 0u; i < g_blueprint_registry.count; ++i) {
        const d_proto_blueprint *bp = (const d_proto_blueprint *)g_blueprint_registry.entries[i].ptr;
        if (bp && bp->name && strcmp(bp->name, name) == 0) {
            return bp;
        }
    }
    return (const d_proto_blueprint *)0;
}

u32 d_content_material_count(void) { return g_material_registry.count; }
const d_proto_material *d_content_get_material_by_index(u32 index) {
    if (index >= g_material_registry.count) return (const d_proto_material *)0;
    return (const d_proto_material *)g_material_registry.entries[index].ptr;
}

u32 d_content_item_count(void) { return g_item_registry.count; }
const d_proto_item *d_content_get_item_by_index(u32 index) {
    if (index >= g_item_registry.count) return (const d_proto_item *)0;
    return (const d_proto_item *)g_item_registry.entries[index].ptr;
}

u32 d_content_container_count(void) { return g_container_registry.count; }
const d_proto_container *d_content_get_container_by_index(u32 index) {
    if (index >= g_container_registry.count) return (const d_proto_container *)0;
    return (const d_proto_container *)g_container_registry.entries[index].ptr;
}

u32 d_content_process_count(void) { return g_process_registry.count; }
const d_proto_process *d_content_get_process_by_index(u32 index) {
    if (index >= g_process_registry.count) return (const d_proto_process *)0;
    return (const d_proto_process *)g_process_registry.entries[index].ptr;
}

u32 d_content_structure_count(void) { return g_structure_registry.count; }
const d_proto_structure *d_content_get_structure_by_index(u32 index) {
    if (index >= g_structure_registry.count) return (const d_proto_structure *)0;
    return (const d_proto_structure *)g_structure_registry.entries[index].ptr;
}

u32 d_content_vehicle_count(void) { return g_vehicle_registry.count; }
const d_proto_vehicle *d_content_get_vehicle_by_index(u32 index) {
    if (index >= g_vehicle_registry.count) return (const d_proto_vehicle *)0;
    return (const d_proto_vehicle *)g_vehicle_registry.entries[index].ptr;
}

u32 d_content_spline_profile_count(void) { return g_spline_profile_registry.count; }
const d_proto_spline_profile *d_content_get_spline_profile_by_index(u32 index) {
    if (index >= g_spline_profile_registry.count) return (const d_proto_spline_profile *)0;
    return (const d_proto_spline_profile *)g_spline_profile_registry.entries[index].ptr;
}

u32 d_content_job_template_count(void) { return g_job_template_registry.count; }
const d_proto_job_template *d_content_get_job_template_by_index(u32 index) {
    if (index >= g_job_template_registry.count) return (const d_proto_job_template *)0;
    return (const d_proto_job_template *)g_job_template_registry.entries[index].ptr;
}

u32 d_content_building_count(void) { return g_building_registry.count; }
const d_proto_building *d_content_get_building_by_index(u32 index) {
    if (index >= g_building_registry.count) return (const d_proto_building *)0;
    return (const d_proto_building *)g_building_registry.entries[index].ptr;
}

u32 d_content_blueprint_count(void) { return g_blueprint_registry.count; }
const d_proto_blueprint *d_content_get_blueprint_by_index(u32 index) {
    if (index >= g_blueprint_registry.count) return (const d_proto_blueprint *)0;
    return (const d_proto_blueprint *)g_blueprint_registry.entries[index].ptr;
}

void d_content_debug_dump(void)
{
    u32 i;
    printf("Content registries:\n");
    printf("  materials: %u\n", (unsigned int)g_material_registry.count);
    for (i = 0u; i < g_material_registry.count; ++i) {
        const d_proto_material *m = (const d_proto_material *)g_material_registry.entries[i].ptr;
        printf("    [%u] %s\n", (unsigned int)g_material_registry.entries[i].id,
               m && m->name ? m->name : "(null)");
    }
    printf("  items: %u\n", (unsigned int)g_item_registry.count);
    for (i = 0u; i < g_item_registry.count; ++i) {
        const d_proto_item *it = (const d_proto_item *)g_item_registry.entries[i].ptr;
        printf("    [%u] %s\n", (unsigned int)g_item_registry.entries[i].id,
               it && it->name ? it->name : "(null)");
    }
    printf("  containers: %u\n", (unsigned int)g_container_registry.count);
    printf("  processes: %u\n", (unsigned int)g_process_registry.count);
    printf("  deposits: %u\n", (unsigned int)g_deposit_registry.count);
    printf("  structures: %u\n", (unsigned int)g_structure_registry.count);
    printf("  vehicles: %u\n", (unsigned int)g_vehicle_registry.count);
    printf("  splines: %u\n", (unsigned int)g_spline_profile_registry.count);
    printf("  job templates: %u\n", (unsigned int)g_job_template_registry.count);
    printf("  buildings: %u\n", (unsigned int)g_building_registry.count);
    printf("  blueprints: %u\n", (unsigned int)g_blueprint_registry.count);
}
