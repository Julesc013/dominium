/* Deterministic serialization schema registry (C89).
 *
 * This module treats serialization identifiers (chunk type IDs, chunk versions,
 * TLV tag IDs) as ABI. It provides a stable schema id for compatibility checks.
 */

#include "domino/io/schema_registry.h"

#include <stdlib.h>
#include <string.h>

#include "domino/io/container.h"

#include "content/d_content_schema.h"
#include "core/d_serialize_tags.h"

#define DOM_FNV1A64_OFFSET 14695981039346656037ULL
#define DOM_FNV1A64_PRIME  1099511628211ULL

static u64 dom_fnv1a64_bytes(u64 h, const unsigned char* data, u32 len) {
    u32 i;
    if (!data || len == 0u) {
        return h;
    }
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= DOM_FNV1A64_PRIME;
    }
    return h;
}

static u64 dom_fnv1a64_u16_le(u64 h, u16 v) {
    unsigned char buf[2];
    dtlv_le_write_u16(buf, v);
    return dom_fnv1a64_bytes(h, buf, 2u);
}

static u64 dom_fnv1a64_u32_le(u64 h, u32 v) {
    unsigned char buf[4];
    dtlv_le_write_u32(buf, v);
    return dom_fnv1a64_bytes(h, buf, 4u);
}

static u64 dom_fnv1a64_u64_le(u64 h, u64 v) {
    unsigned char buf[8];
    dtlv_le_write_u64(buf, v);
    return dom_fnv1a64_bytes(h, buf, 8u);
}

static void dom_insertion_sort_u32(u32* a, u32 count) {
    u32 i;
    if (!a || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        u32 key = a[i];
        u32 j = i;
        while (j > 0u && a[j - 1u] > key) {
            a[j] = a[j - 1u];
            --j;
        }
        a[j] = key;
    }
}

/*-----------------------
 * Compiled-in registry
 *-----------------------*/

static const u32 g_instance_config_tags[] = {
    DOM_TAG_INSTANCE_ID,
    DOM_TAG_WORLD_SEED,
    DOM_TAG_WORLD_SIZE_M,
    DOM_TAG_VERTICAL_MIN_M,
    DOM_TAG_VERTICAL_MAX_M,
    DOM_TAG_SUITE_VERSION,
    DOM_TAG_CORE_VERSION,
    DOM_TAG_PACK_ENTRY,
    DOM_TAG_MOD_ENTRY,
    DOM_TAG_LAST_PRODUCT,
    DOM_TAG_LAST_PRODUCT_VERSION
};

static const u32 g_save_instance_tags[] = {
    TAG_SUBSYS_DWORLD,
    TAG_SUBSYS_DRES,
    TAG_SUBSYS_DENV,
    TAG_SUBSYS_DBULD,
    TAG_SUBSYS_DTRANS,
    TAG_SUBSYS_DSTRUCT,
    TAG_SUBSYS_DVEH,
    TAG_SUBSYS_DJOB,
    TAG_SUBSYS_DNET,
    TAG_SUBSYS_DREPLAY,
    TAG_SUBSYS_DHYDRO,
    TAG_SUBSYS_DLITHO,
    TAG_SUBSYS_DORG,
    TAG_SUBSYS_DRESEARCH,
    TAG_SUBSYS_DECON,
    TAG_SUBSYS_DPOLICY
};

static const u32 g_replay_tags[] = {
    DOM_TAG_REPLAY_FRAME
};

static const u32 g_content_stream_tags[] = {
    D_TLV_SCHEMA_MATERIAL_V1,
    D_TLV_SCHEMA_ITEM_V1,
    D_TLV_SCHEMA_CONTAINER_V1,
    D_TLV_SCHEMA_PROCESS_V1,
    D_TLV_SCHEMA_DEPOSIT_V1,
    D_TLV_SCHEMA_STRUCTURE_V1,
    D_TLV_SCHEMA_VEHICLE_V1,
    D_TLV_SCHEMA_SPLINE_V1,
    D_TLV_SCHEMA_JOB_TEMPLATE_V1,
    D_TLV_SCHEMA_BUILDING_V1,
    D_TLV_SCHEMA_BLUEPRINT_V1,
    D_TLV_SCHEMA_RESEARCH_V1,
    D_TLV_SCHEMA_RESEARCH_POINT_SOURCE_V1,
    D_TLV_SCHEMA_POLICY_RULE_V1,
    D_TLV_SCHEMA_PACK_V1,
    D_TLV_SCHEMA_MOD_V1
};

static const u32 g_handshake_tags[] = {
    DOM_TAG_HANDSHAKE_ENGINE_BUILD_ID,
    DOM_TAG_HANDSHAKE_ENGINE_GIT_HASH,
    DOM_TAG_HANDSHAKE_SIM_SCHEMA_ID,
    DOM_TAG_HANDSHAKE_SIM_SCHEMA_VERSION,
    DOM_TAG_HANDSHAKE_DET_GRADE,
    DOM_TAG_HANDSHAKE_LOCKSTEP_STRICT,
    DOM_TAG_HANDSHAKE_CONTENT_HASH
};

static const dom_chunk_schema_desc g_schema_registry[] = {
    { DOM_CHUNK_INSTANCE_CONFIG_V1, 1u, DOM_SCHEMA_DOMAIN_CONFIG,
      g_instance_config_tags, (u32)(sizeof(g_instance_config_tags) / sizeof(g_instance_config_tags[0])) },

    { DOM_CHUNK_SAVE_INSTANCE_V1, 1u, DOM_SCHEMA_DOMAIN_SIM,
      g_save_instance_tags, (u32)(sizeof(g_save_instance_tags) / sizeof(g_save_instance_tags[0])) },

    { DOM_CHUNK_REPLAY_V1, 1u, DOM_SCHEMA_DOMAIN_SIM,
      g_replay_tags, (u32)(sizeof(g_replay_tags) / sizeof(g_replay_tags[0])) },

    { DOM_CHUNK_CONTENT_STREAM_V1, 1u, DOM_SCHEMA_DOMAIN_CONTENT,
      g_content_stream_tags, (u32)(sizeof(g_content_stream_tags) / sizeof(g_content_stream_tags[0])) },

    { DOM_CHUNK_NET_HANDSHAKE_V1, 1u, DOM_SCHEMA_DOMAIN_NET,
      g_handshake_tags, (u32)(sizeof(g_handshake_tags) / sizeof(g_handshake_tags[0])) }
};

const dom_chunk_schema_desc* dom_schema_registry(u32* out_count) {
    if (out_count) {
        *out_count = (u32)(sizeof(g_schema_registry) / sizeof(g_schema_registry[0]));
    }
    return g_schema_registry;
}

/*-----------------------
 * Deterministic schema id
 *-----------------------*/

static int dom_schema_desc_less(const dom_chunk_schema_desc* a, const dom_chunk_schema_desc* b) {
    if (a->chunk_type_id < b->chunk_type_id) return 1;
    if (a->chunk_type_id > b->chunk_type_id) return 0;
    if (a->chunk_version < b->chunk_version) return 1;
    if (a->chunk_version > b->chunk_version) return 0;
    return 0;
}

static void dom_insertion_sort_desc_ptrs(const dom_chunk_schema_desc** a, u32 count) {
    u32 i;
    if (!a || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        const dom_chunk_schema_desc* key = a[i];
        u32 j = i;
        while (j > 0u && dom_schema_desc_less(key, a[j - 1u])) {
            a[j] = a[j - 1u];
            --j;
        }
        a[j] = key;
    }
}

u64 dom_schema_id_for_domain(u32 domain_mask) {
    const dom_chunk_schema_desc* reg;
    u32 reg_count;
    const dom_chunk_schema_desc** selected;
    u32 sel_count;
    u32 i;
    u64 h;

    reg = dom_schema_registry(&reg_count);
    if (!reg || reg_count == 0u) {
        return 0u;
    }

    selected = (const dom_chunk_schema_desc**)malloc(sizeof(dom_chunk_schema_desc*) * (size_t)reg_count);
    if (!selected) {
        return 0u;
    }

    sel_count = 0u;
    for (i = 0u; i < reg_count; ++i) {
        if ((reg[i].domain_mask & domain_mask) == 0u) {
            continue;
        }
        selected[sel_count++] = &reg[i];
    }

    if (sel_count == 0u) {
        free(selected);
        return 0u;
    }

    dom_insertion_sort_desc_ptrs(selected, sel_count);

    h = (u64)DOM_FNV1A64_OFFSET;
    for (i = 0u; i < sel_count; ++i) {
        const dom_chunk_schema_desc* d = selected[i];
        u32* tags;
        u32 j;

        h = dom_fnv1a64_u32_le(h, d->chunk_type_id);
        h = dom_fnv1a64_u16_le(h, d->chunk_version);
        h = dom_fnv1a64_u32_le(h, d->tlv_tag_count);

        if (d->tlv_tag_count == 0u) {
            continue;
        }
        if (!d->tlv_tags) {
            free(selected);
            return 0u;
        }

        tags = (u32*)malloc(sizeof(u32) * (size_t)d->tlv_tag_count);
        if (!tags) {
            free(selected);
            return 0u;
        }
        memcpy(tags, d->tlv_tags, sizeof(u32) * (size_t)d->tlv_tag_count);
        dom_insertion_sort_u32(tags, d->tlv_tag_count);

        for (j = 0u; j < d->tlv_tag_count; ++j) {
            h = dom_fnv1a64_u32_le(h, tags[j]);
        }
        free(tags);
    }

    free(selected);
    return h;
}

u64 dom_sim_schema_id(void) {
    return dom_schema_id_for_domain(DOM_SCHEMA_DOMAIN_SIM);
}

