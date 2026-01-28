/*
FILE: game/rules/fab/fab_interpreters.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / fab
RESPONSIBILITY: Implements minimal fabrication (FAB) interpreters and adapters.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: FAB evaluation is deterministic for identical inputs.
*/
#include "dominium/fab/fab_interpreters.h"

#include <ctype.h>
#include <string.h>
#include <stdlib.h>

static int fab_is_empty(const char* s)
{
    if (!s) {
        return 1;
    }
    while (*s) {
        if (*s != ' ' && *s != '\t' && *s != '\n' && *s != '\r') {
            return 0;
        }
        ++s;
    }
    return 1;
}

static int fab_str_icmp(const char* a, const char* b)
{
    int ca;
    int cb;
    if (!a && !b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    while (*a && *b) {
        ca = (unsigned char)*a;
        cb = (unsigned char)*b;
        ca = tolower(ca);
        cb = tolower(cb);
        if (ca != cb) {
            return (ca < cb) ? -1 : 1;
        }
        ++a;
        ++b;
    }
    if (*a == *b) return 0;
    return (*a < *b) ? -1 : 1;
}

static int fab_str_eq(const char* a, const char* b)
{
    return fab_str_icmp(a, b) == 0;
}

static const char* fab_id_tail(const char* s)
{
    const char* last = s;
    const char* p;
    if (!s) {
        return s;
    }
    for (p = s; *p; ++p) {
        if (*p == '.') {
            last = p + 1;
        }
    }
    return last;
}

static u32 fab_hash32(const char* s)
{
    u32 h = 2166136261u;
    const unsigned char* p = (const unsigned char*)s;
    if (!s) {
        return 0u;
    }
    while (*p) {
        h ^= (u32)(*p++);
        h *= 16777619u;
    }
    return h;
}

static int fab_checked_add_q48(q48_16 a, q48_16 b, q48_16* out)
{
    q48_16 sum = a + b;
    if (!out) {
        return -1;
    }
    if (b > 0 && sum < a) {
        return -2;
    }
    if (b < 0 && sum > a) {
        return -2;
    }
    *out = sum;
    return 0;
}

static u32 fab_parse_directionality(const char* tag)
{
    const char* tail = fab_id_tail(tag);
    if (fab_str_eq(tail, "input") || fab_str_eq(tail, "in")) {
        return DOM_FAB_DIR_INPUT;
    }
    if (fab_str_eq(tail, "output") || fab_str_eq(tail, "out")) {
        return DOM_FAB_DIR_OUTPUT;
    }
    if (fab_str_eq(tail, "bidirectional") || fab_str_eq(tail, "io") || fab_str_eq(tail, "both")) {
        return DOM_FAB_DIR_BIDIRECTIONAL;
    }
    return DOM_FAB_DIR_UNKNOWN;
}

static u32 fab_parse_interface_type(const char* tag)
{
    const char* tail = fab_id_tail(tag);
    if (fab_str_eq(tail, "mechanical")) return DOM_FAB_IFACE_MECHANICAL;
    if (fab_str_eq(tail, "electrical")) return DOM_FAB_IFACE_ELECTRICAL;
    if (fab_str_eq(tail, "fluid")) return DOM_FAB_IFACE_FLUID;
    if (fab_str_eq(tail, "data")) return DOM_FAB_IFACE_DATA;
    if (fab_str_eq(tail, "thermal")) return DOM_FAB_IFACE_THERMAL;
    return DOM_FAB_IFACE_UNKNOWN;
}

/*------------------------------------------------------------
 * Material registry
 *------------------------------------------------------------*/

void dom_fab_material_registry_init(dom_fab_material_registry* reg,
                                    dom_fab_material* storage,
                                    u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->materials = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_fab_material) * (size_t)capacity);
    }
}

static u32 fab_material_find_index(const dom_fab_material_registry* reg,
                                   const char* material_id,
                                   int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->materials || !material_id) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        int cmp = fab_str_icmp(reg->materials[i].material_id, material_id);
        if (cmp == 0) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (cmp > 0) {
            break;
        }
    }
    return i;
}

int dom_fab_material_register(dom_fab_material_registry* reg,
                              const dom_fab_material* material)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->materials || !material || fab_is_empty(material->material_id)) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = fab_material_find_index(reg, material->material_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->materials[i] = reg->materials[i - 1u];
    }
    reg->materials[idx] = *material;
    reg->count += 1u;
    return 0;
}

const dom_fab_material* dom_fab_material_find(const dom_fab_material_registry* reg,
                                              const char* material_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->materials || !material_id) {
        return 0;
    }
    idx = fab_material_find_index(reg, material_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->materials[idx];
}

const dom_fab_trait* dom_fab_material_trait_find(const dom_fab_material* material,
                                                 const char* trait_id)
{
    u32 i;
    if (!material || !material->traits || !trait_id) {
        return 0;
    }
    for (i = 0u; i < material->trait_count; ++i) {
        if (fab_str_eq(material->traits[i].trait_id, trait_id)) {
            return &material->traits[i];
        }
    }
    return 0;
}

int dom_fab_material_trait_interpolate(const dom_fab_material* a,
                                       const dom_fab_material* b,
                                       const char* trait_id,
                                       q16_16 t_q16,
                                       dom_fab_trait* out_trait)
{
    const dom_fab_trait* ta;
    const dom_fab_trait* tb;
    q48_16 t_q48;
    q48_16 diff;
    q48_16 delta;
    if (!a || !b || !trait_id || !out_trait) {
        return -1;
    }
    ta = dom_fab_material_trait_find(a, trait_id);
    tb = dom_fab_material_trait_find(b, trait_id);
    if (!ta || !tb) {
        return -2;
    }
    if (!fab_str_eq(ta->unit_id, tb->unit_id)) {
        return -3;
    }
    out_trait->trait_id = trait_id;
    out_trait->unit_id = ta->unit_id;
    out_trait->aggregation = ta->aggregation ? ta->aggregation : tb->aggregation;
    out_trait->interpolation = ta->interpolation ? ta->interpolation : tb->interpolation;

    if (out_trait->interpolation == DOM_FAB_INTERP_LINEAR) {
        t_q48 = (q48_16)t_q16;
        diff = tb->value_q48 - ta->value_q48;
        delta = d_q48_16_mul(diff, t_q48);
        out_trait->value_q48 = d_q48_16_add(ta->value_q48, delta);
        return 0;
    }

    /* Step interpolation (default) */
    if (t_q16 < (q16_16)(1 << 15)) {
        out_trait->value_q48 = ta->value_q48;
    } else {
        out_trait->value_q48 = tb->value_q48;
    }
    return 0;
}

/*------------------------------------------------------------
 * Interface registry + compatibility
 *------------------------------------------------------------*/

void dom_fab_interface_registry_init(dom_fab_interface_registry* reg,
                                     dom_fab_interface_desc* storage,
                                     u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->interfaces = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_fab_interface_desc) * (size_t)capacity);
    }
}

static u32 fab_interface_find_index(const dom_fab_interface_registry* reg,
                                    const char* interface_id,
                                    int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->interfaces || !interface_id) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        int cmp = fab_str_icmp(reg->interfaces[i].interface_id, interface_id);
        if (cmp == 0) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (cmp > 0) {
            break;
        }
    }
    return i;
}

int dom_fab_interface_register(dom_fab_interface_registry* reg,
                               const dom_fab_interface_desc* desc)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->interfaces || !desc || fab_is_empty(desc->interface_id)) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = fab_interface_find_index(reg, desc->interface_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->interfaces[i] = reg->interfaces[i - 1u];
    }
    reg->interfaces[idx] = *desc;
    reg->count += 1u;
    return 0;
}

const dom_fab_interface_desc* dom_fab_interface_find(const dom_fab_interface_registry* reg,
                                                     const char* interface_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->interfaces || !interface_id) {
        return 0;
    }
    idx = fab_interface_find_index(reg, interface_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->interfaces[idx];
}

int dom_fab_interface_check_compat(const dom_fab_interface_desc* a,
                                   const dom_fab_interface_desc* b,
                                   dom_fab_interface_compat_result* out_result)
{
    u32 dir_a;
    u32 dir_b;
    u32 type_a;
    u32 type_b;
    if (out_result) {
        out_result->compat = DOM_FAB_COMPAT_REFUSE;
        out_result->refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
    }
    if (!a || !b || !out_result) {
        return -1;
    }
    type_a = fab_parse_interface_type(a->interface_type);
    type_b = fab_parse_interface_type(b->interface_type);
    if (type_a == DOM_FAB_IFACE_UNKNOWN || type_b == DOM_FAB_IFACE_UNKNOWN || type_a != type_b) {
        out_result->compat = DOM_FAB_COMPAT_REFUSE;
        out_result->refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
        return 0;
    }
    dir_a = fab_parse_directionality(a->directionality);
    dir_b = fab_parse_directionality(b->directionality);
    if (dir_a == DOM_FAB_DIR_UNKNOWN || dir_b == DOM_FAB_DIR_UNKNOWN) {
        out_result->compat = DOM_FAB_COMPAT_REFUSE;
        out_result->refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
        return 0;
    }
    if (dir_a == DOM_FAB_DIR_INPUT && dir_b == DOM_FAB_DIR_INPUT) {
        out_result->compat = DOM_FAB_COMPAT_REFUSE;
        out_result->refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
        return 0;
    }
    if (dir_a == DOM_FAB_DIR_OUTPUT && dir_b == DOM_FAB_DIR_OUTPUT) {
        out_result->compat = DOM_FAB_COMPAT_REFUSE;
        out_result->refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
        return 0;
    }
    if (!fab_str_eq(a->capacity.unit_id, b->capacity.unit_id) ||
        a->capacity.scale != b->capacity.scale) {
        out_result->compat = DOM_FAB_COMPAT_REFUSE;
        out_result->refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
        return 0;
    }
    if (a->capacity.value_q48 != b->capacity.value_q48) {
        if (a->allow_degraded || b->allow_degraded) {
            out_result->compat = DOM_FAB_COMPAT_DEGRADED;
            out_result->refusal_code = DOM_FAB_REFUSE_NONE;
            return 0;
        }
        out_result->compat = DOM_FAB_COMPAT_REFUSE;
        out_result->refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
        return 0;
    }
    out_result->compat = DOM_FAB_COMPAT_OK;
    out_result->refusal_code = DOM_FAB_REFUSE_NONE;
    return 0;
}

/*------------------------------------------------------------
 * Part registry
 *------------------------------------------------------------*/

void dom_fab_part_registry_init(dom_fab_part_registry* reg,
                                dom_fab_part_desc* storage,
                                u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->parts = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_fab_part_desc) * (size_t)capacity);
    }
}

static u32 fab_part_find_index(const dom_fab_part_registry* reg,
                               const char* part_id,
                               int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->parts || !part_id) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        int cmp = fab_str_icmp(reg->parts[i].part_id, part_id);
        if (cmp == 0) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (cmp > 0) {
            break;
        }
    }
    return i;
}

int dom_fab_part_register(dom_fab_part_registry* reg,
                          const dom_fab_part_desc* part)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->parts || !part || fab_is_empty(part->part_id)) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = fab_part_find_index(reg, part->part_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->parts[i] = reg->parts[i - 1u];
    }
    reg->parts[idx] = *part;
    reg->count += 1u;
    return 0;
}

const dom_fab_part_desc* dom_fab_part_find(const dom_fab_part_registry* reg,
                                           const char* part_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->parts || !part_id) {
        return 0;
    }
    idx = fab_part_find_index(reg, part_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->parts[idx];
}

/*------------------------------------------------------------
 * Assembly registry and helpers
 *------------------------------------------------------------*/

void dom_fab_assembly_registry_init(dom_fab_assembly_registry* reg,
                                    dom_fab_assembly_desc* storage,
                                    u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->assemblies = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_fab_assembly_desc) * (size_t)capacity);
    }
}

static u32 fab_assembly_find_index(const dom_fab_assembly_registry* reg,
                                   const char* assembly_id,
                                   int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->assemblies || !assembly_id) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        int cmp = fab_str_icmp(reg->assemblies[i].assembly_id, assembly_id);
        if (cmp == 0) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (cmp > 0) {
            break;
        }
    }
    return i;
}

int dom_fab_assembly_register(dom_fab_assembly_registry* reg,
                              const dom_fab_assembly_desc* assembly)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->assemblies || !assembly || fab_is_empty(assembly->assembly_id)) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = fab_assembly_find_index(reg, assembly->assembly_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->assemblies[i] = reg->assemblies[i - 1u];
    }
    reg->assemblies[idx] = *assembly;
    reg->count += 1u;
    return 0;
}

const dom_fab_assembly_desc* dom_fab_assembly_find(const dom_fab_assembly_registry* reg,
                                                   const char* assembly_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->assemblies || !assembly_id) {
        return 0;
    }
    idx = fab_assembly_find_index(reg, assembly_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->assemblies[idx];
}

static int fab_node_index(const dom_fab_assembly_desc* assembly,
                          const char* node_id)
{
    u32 i;
    if (!assembly || !assembly->nodes || !node_id) {
        return -1;
    }
    for (i = 0u; i < assembly->node_count; ++i) {
        if (fab_str_eq(assembly->nodes[i].node_id, node_id)) {
            return (int)i;
        }
    }
    return -1;
}

static int fab_part_has_interface(const dom_fab_part_desc* part,
                                  const char* interface_id)
{
    u32 i;
    if (!part || !part->interface_ids || !interface_id) {
        return 0;
    }
    for (i = 0u; i < part->interface_count; ++i) {
        if (fab_str_eq(part->interface_ids[i], interface_id)) {
            return 1;
        }
    }
    return 0;
}

static int fab_cycle_dfs(const dom_fab_assembly_desc* assembly,
                         int node_index,
                         u32* state)
{
    u32 i;
    const char* node_id;
    if (!assembly || !state || node_index < 0) {
        return 0;
    }
    if (state[node_index] == 1u) {
        return 1;
    }
    if (state[node_index] == 2u) {
        return 0;
    }
    state[node_index] = 1u;
    node_id = assembly->nodes[node_index].node_id;
    for (i = 0u; i < assembly->edge_count; ++i) {
        const dom_fab_assembly_edge* edge = &assembly->edges[i];
        if (!edge->from_node_id || !edge->to_node_id) {
            continue;
        }
        if (!fab_str_eq(edge->from_node_id, node_id)) {
            continue;
        }
        {
            int next_index = fab_node_index(assembly, edge->to_node_id);
            if (next_index >= 0 && fab_cycle_dfs(assembly, next_index, state)) {
                return 1;
            }
        }
    }
    state[node_index] = 2u;
    return 0;
}

int dom_fab_assembly_validate(const dom_fab_assembly_desc* assembly,
                              const dom_fab_part_registry* parts,
                              const dom_fab_interface_registry* interfaces,
                              const dom_fab_assembly_registry* assemblies,
                              u32* out_refusal_code)
{
    u32 i;
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
    }
    if (!assembly) {
        return -1;
    }
    if (!assembly->nodes || assembly->node_count == 0u) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
        }
        return -2;
    }
    for (i = 0u; i < assembly->node_count; ++i) {
        const dom_fab_assembly_node* node = &assembly->nodes[i];
        if (fab_is_empty(node->node_id) || fab_is_empty(node->ref_id)) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
            }
            return -3;
        }
        if (node->node_type == DOM_FAB_NODE_PART) {
            if (!dom_fab_part_find(parts, node->ref_id)) {
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
                }
                return -4;
            }
        } else if (node->node_type == DOM_FAB_NODE_SUBASSEMBLY) {
            if (!dom_fab_assembly_find(assemblies, node->ref_id)) {
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
                }
                return -5;
            }
        } else {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
            }
            return -6;
        }
    }
    for (i = 0u; i < assembly->edge_count; ++i) {
        const dom_fab_assembly_edge* edge = &assembly->edges[i];
        int a_idx;
        int b_idx;
        if (fab_is_empty(edge->edge_id) ||
            fab_is_empty(edge->from_node_id) ||
            fab_is_empty(edge->to_node_id)) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
            }
            return -7;
        }
        a_idx = fab_node_index(assembly, edge->from_node_id);
        b_idx = fab_node_index(assembly, edge->to_node_id);
        if (a_idx < 0 || b_idx < 0) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
            }
            return -8;
        }
        if (fab_is_empty(edge->interface_id)) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
            }
            return -9;
        }
        if (!dom_fab_interface_find(interfaces, edge->interface_id)) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
            }
            return -10;
        }
        {
            const dom_fab_assembly_node* node_a = &assembly->nodes[a_idx];
            const dom_fab_assembly_node* node_b = &assembly->nodes[b_idx];
            if (node_a->node_type == DOM_FAB_NODE_PART) {
                const dom_fab_part_desc* part = dom_fab_part_find(parts, node_a->ref_id);
                if (!part || !fab_part_has_interface(part, edge->interface_id)) {
                    if (out_refusal_code) {
                        *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
                    }
                    return -11;
                }
            }
            if (node_b->node_type == DOM_FAB_NODE_PART) {
                const dom_fab_part_desc* part = dom_fab_part_find(parts, node_b->ref_id);
                if (!part || !fab_part_has_interface(part, edge->interface_id)) {
                    if (out_refusal_code) {
                        *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
                    }
                    return -12;
                }
            }
        }
    }
    if ((assembly->flags & DOM_FAB_ASSEMBLY_ALLOW_CYCLES) == 0u) {
        u32* state = (u32*)malloc(sizeof(u32) * (size_t)assembly->node_count);
        if (!state) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
            }
            return -13;
        }
        memset(state, 0, sizeof(u32) * (size_t)assembly->node_count);
        for (i = 0u; i < assembly->node_count; ++i) {
            if (fab_cycle_dfs(assembly, (int)i, state)) {
                free(state);
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
                }
                return -14;
            }
        }
        free(state);
    }
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_NONE;
    }
    return 0;
}

static int fab_add_unique_id(const char* id,
                             const char** out_ids,
                             u32* io_count,
                             u32 capacity)
{
    u32 i;
    if (!id || !out_ids || !io_count) {
        return -1;
    }
    for (i = 0u; i < *io_count; ++i) {
        if (fab_str_eq(out_ids[i], id)) {
            return 0;
        }
    }
    if (*io_count >= capacity) {
        return -2;
    }
    out_ids[*io_count] = id;
    *io_count += 1u;
    return 0;
}

static int fab_add_metric(const dom_fab_metric* metric,
                          dom_fab_metric* out_metrics,
                          u32* io_count,
                          u32 capacity,
                          u32* counts)
{
    u32 i;
    if (!metric || !out_metrics || !io_count || !counts) {
        return -1;
    }
    for (i = 0u; i < *io_count; ++i) {
        if (fab_str_eq(out_metrics[i].metric_id, metric->metric_id)) {
            u32 agg = out_metrics[i].aggregation ? out_metrics[i].aggregation : DOM_FAB_AGG_SUM;
            q48_16 next = 0;
            switch (agg) {
            case DOM_FAB_AGG_MIN:
                if (metric->value.value_q48 < out_metrics[i].value.value_q48) {
                    out_metrics[i].value = metric->value;
                }
                break;
            case DOM_FAB_AGG_MAX:
                if (metric->value.value_q48 > out_metrics[i].value.value_q48) {
                    out_metrics[i].value = metric->value;
                }
                break;
            case DOM_FAB_AGG_AVG:
                if (fab_checked_add_q48(out_metrics[i].value.value_q48,
                                        metric->value.value_q48, &next) != 0) {
                    return -2;
                }
                out_metrics[i].value.value_q48 = next;
                counts[i] += 1u;
                break;
            case DOM_FAB_AGG_SUM:
            default:
                if (fab_checked_add_q48(out_metrics[i].value.value_q48,
                                        metric->value.value_q48, &next) != 0) {
                    return -2;
                }
                out_metrics[i].value.value_q48 = next;
                break;
            }
            return 0;
        }
    }
    if (*io_count >= capacity) {
        return -3;
    }
    out_metrics[*io_count] = *metric;
    counts[*io_count] = 1u;
    *io_count += 1u;
    return 0;
}

static void fab_finalize_metric_avgs(dom_fab_metric* metrics,
                                     u32 count,
                                     const u32* counts)
{
    u32 i;
    if (!metrics || !counts) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        if (metrics[i].aggregation == DOM_FAB_AGG_AVG && counts[i] > 0u) {
            metrics[i].value.value_q48 = metrics[i].value.value_q48 / (q48_16)counts[i];
        }
    }
}

static int fab_aggregate_recursive(const dom_fab_assembly_desc* assembly,
                                   const dom_fab_part_registry* parts,
                                   const dom_fab_interface_registry* interfaces,
                                   const dom_fab_assembly_registry* assemblies,
                                   dom_fab_assembly_aggregate* out_agg,
                                   u32* throughput_counts,
                                   u32* maintenance_counts,
                                   u32* out_refusal_code)
{
    u32 i;
    if (!assembly || !out_agg) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
        }
        return -1;
    }
    if (assembly->hosted_process_ids && assembly->hosted_process_count > 0u) {
        for (i = 0u; i < assembly->hosted_process_count; ++i) {
            if (fab_add_unique_id(assembly->hosted_process_ids[i],
                                  out_agg->hosted_process_ids,
                                  &out_agg->hosted_process_count,
                                  out_agg->hosted_process_capacity) != 0) {
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                }
                return -10;
            }
        }
    }
    if (assembly->throughput_limits && assembly->throughput_count > 0u && throughput_counts) {
        for (i = 0u; i < assembly->throughput_count; ++i) {
            if (fab_add_metric(&assembly->throughput_limits[i],
                               out_agg->throughput_limits,
                               &out_agg->throughput_count,
                               out_agg->throughput_capacity,
                               throughput_counts) != 0) {
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                }
                return -11;
            }
        }
    }
    if (assembly->maintenance && assembly->maintenance_count > 0u && maintenance_counts) {
        for (i = 0u; i < assembly->maintenance_count; ++i) {
            if (fab_add_metric(&assembly->maintenance[i],
                               out_agg->maintenance,
                               &out_agg->maintenance_count,
                               out_agg->maintenance_capacity,
                               maintenance_counts) != 0) {
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                }
                return -12;
            }
        }
    }
    for (i = 0u; i < assembly->node_count; ++i) {
        const dom_fab_assembly_node* node = &assembly->nodes[i];
        if (node->node_type == DOM_FAB_NODE_PART) {
            const dom_fab_part_desc* part = dom_fab_part_find(parts, node->ref_id);
            q48_16 next = 0;
            if (!part) {
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
                }
                return -2;
            }
            if (fab_checked_add_q48(out_agg->total_mass_q48, part->mass.value_q48, &next) != 0) {
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                }
                return -3;
            }
            out_agg->total_mass_q48 = next;
            if (fab_checked_add_q48(out_agg->total_volume_q48, part->volume.value_q48, &next) != 0) {
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                }
                return -4;
            }
            out_agg->total_volume_q48 = next;
            if (part->interface_ids && part->interface_count > 0u) {
                u32 j;
                for (j = 0u; j < part->interface_count; ++j) {
                    const dom_fab_interface_desc* iface = dom_fab_interface_find(interfaces, part->interface_ids[j]);
                    u32 type;
                    if (!iface) {
                        if (out_refusal_code) {
                            *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
                        }
                        return -5;
                    }
                    type = fab_parse_interface_type(iface->interface_type);
                    switch (type) {
                    case DOM_FAB_IFACE_MECHANICAL:
                        (void)fab_checked_add_q48(out_agg->capacities.mechanical_q48,
                                                  iface->capacity.value_q48,
                                                  &out_agg->capacities.mechanical_q48);
                        break;
                    case DOM_FAB_IFACE_ELECTRICAL:
                        (void)fab_checked_add_q48(out_agg->capacities.electrical_q48,
                                                  iface->capacity.value_q48,
                                                  &out_agg->capacities.electrical_q48);
                        break;
                    case DOM_FAB_IFACE_FLUID:
                        (void)fab_checked_add_q48(out_agg->capacities.fluid_q48,
                                                  iface->capacity.value_q48,
                                                  &out_agg->capacities.fluid_q48);
                        break;
                    case DOM_FAB_IFACE_DATA:
                        (void)fab_checked_add_q48(out_agg->capacities.data_q48,
                                                  iface->capacity.value_q48,
                                                  &out_agg->capacities.data_q48);
                        break;
                    case DOM_FAB_IFACE_THERMAL:
                        (void)fab_checked_add_q48(out_agg->capacities.thermal_q48,
                                                  iface->capacity.value_q48,
                                                  &out_agg->capacities.thermal_q48);
                        break;
                    default:
                        break;
                    }
                }
            }
        } else if (node->node_type == DOM_FAB_NODE_SUBASSEMBLY) {
            const dom_fab_assembly_desc* sub = dom_fab_assembly_find(assemblies, node->ref_id);
            if (!sub) {
                if (out_refusal_code) {
                    *out_refusal_code = DOM_FAB_REFUSE_INTEGRITY_VIOLATION;
                }
                return -6;
            }
            if (fab_aggregate_recursive(sub, parts, interfaces, assemblies,
                                        out_agg, throughput_counts, maintenance_counts,
                                        out_refusal_code) != 0) {
                return -7;
            }
        }
    }
    return 0;
}

int dom_fab_assembly_aggregate_compute(const dom_fab_assembly_desc* assembly,
                                       const dom_fab_part_registry* parts,
                                       const dom_fab_interface_registry* interfaces,
                                       const dom_fab_assembly_registry* assemblies,
                                       dom_fab_assembly_aggregate* out_agg,
                                       u32* out_refusal_code)
{
    u32* throughput_counts = 0;
    u32* maintenance_counts = 0;
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
    }
    if (!assembly || !out_agg) {
        return -1;
    }
    {
        const char** hosted_ids = out_agg->hosted_process_ids;
        u32 hosted_cap = out_agg->hosted_process_capacity;
        dom_fab_metric* throughput = out_agg->throughput_limits;
        u32 throughput_cap = out_agg->throughput_capacity;
        dom_fab_metric* maintenance = out_agg->maintenance;
        u32 maintenance_cap = out_agg->maintenance_capacity;

        memset(out_agg, 0, sizeof(*out_agg));
        out_agg->hosted_process_ids = hosted_ids;
        out_agg->hosted_process_capacity = hosted_cap;
        out_agg->throughput_limits = throughput;
        out_agg->throughput_capacity = throughput_cap;
        out_agg->maintenance = maintenance;
        out_agg->maintenance_capacity = maintenance_cap;
    }
    if (out_agg->hosted_process_ids && out_agg->hosted_process_capacity > 0u) {
        memset(out_agg->hosted_process_ids, 0,
               sizeof(const char*) * (size_t)out_agg->hosted_process_capacity);
    }
    if (out_agg->throughput_limits && out_agg->throughput_capacity > 0u) {
        memset(out_agg->throughput_limits, 0,
               sizeof(dom_fab_metric) * (size_t)out_agg->throughput_capacity);
    }
    if (out_agg->maintenance && out_agg->maintenance_capacity > 0u) {
        memset(out_agg->maintenance, 0,
               sizeof(dom_fab_metric) * (size_t)out_agg->maintenance_capacity);
    }
    if (out_agg->throughput_capacity > 0u) {
        throughput_counts = (u32*)malloc(sizeof(u32) * (size_t)out_agg->throughput_capacity);
    }
    if (out_agg->maintenance_capacity > 0u) {
        maintenance_counts = (u32*)malloc(sizeof(u32) * (size_t)out_agg->maintenance_capacity);
    }
    if (throughput_counts) {
        memset(throughput_counts, 0, sizeof(u32) * (size_t)out_agg->throughput_capacity);
    }
    if (maintenance_counts) {
        memset(maintenance_counts, 0, sizeof(u32) * (size_t)out_agg->maintenance_capacity);
    }

    if (fab_aggregate_recursive(assembly, parts, interfaces, assemblies,
                                out_agg, throughput_counts, maintenance_counts,
                                out_refusal_code) != 0) {
        if (throughput_counts) free(throughput_counts);
        if (maintenance_counts) free(maintenance_counts);
        return -5;
    }

    if (throughput_counts) {
        fab_finalize_metric_avgs(out_agg->throughput_limits, out_agg->throughput_count, throughput_counts);
        free(throughput_counts);
    }
    if (maintenance_counts) {
        fab_finalize_metric_avgs(out_agg->maintenance, out_agg->maintenance_count, maintenance_counts);
        free(maintenance_counts);
    }

    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_NONE;
    }
    return 0;
}

/*------------------------------------------------------------
 * Process registry and execution
 *------------------------------------------------------------*/

void dom_fab_process_registry_init(dom_fab_process_registry* reg,
                                   dom_fab_process_family* storage,
                                   u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->families = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_fab_process_family) * (size_t)capacity);
    }
}

static u32 fab_process_find_index(const dom_fab_process_registry* reg,
                                  const char* process_family_id,
                                  int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->families || !process_family_id) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        int cmp = fab_str_icmp(reg->families[i].process_family_id, process_family_id);
        if (cmp == 0) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (cmp > 0) {
            break;
        }
    }
    return i;
}

int dom_fab_process_register(dom_fab_process_registry* reg,
                             const dom_fab_process_family* family)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->families || !family || fab_is_empty(family->process_family_id)) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = fab_process_find_index(reg, family->process_family_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->families[i] = reg->families[i - 1u];
    }
    reg->families[idx] = *family;
    reg->count += 1u;
    return 0;
}

const dom_fab_process_family* dom_fab_process_find(const dom_fab_process_registry* reg,
                                                   const char* process_family_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->families || !process_family_id) {
        return 0;
    }
    idx = fab_process_find_index(reg, process_family_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->families[idx];
}

int dom_fab_constraints_eval(const dom_fab_constraint* constraints,
                             u32 constraint_count,
                             const dom_fab_constraint_context* ctx,
                             u32* out_refusal_code)
{
    u32 i;
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
    }
    if (!constraints || constraint_count == 0u) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_FAB_REFUSE_NONE;
        }
        return 0;
    }
    if (!ctx || !ctx->values || ctx->value_count == 0u) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
        }
        return -1;
    }
    for (i = 0u; i < constraint_count; ++i) {
        const dom_fab_constraint* c = &constraints[i];
        u32 j;
        int found = 0;
        for (j = 0u; j < ctx->value_count; ++j) {
            if (fab_str_eq(ctx->values[j].param_id, c->key)) {
                q48_16 v = ctx->values[j].value_q48;
                found = 1;
                if (v < c->min_q48 || v > c->max_q48) {
                    if (out_refusal_code) {
                        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                    }
                    return -2;
                }
                break;
            }
        }
        if (!found) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
            }
            return -3;
        }
    }
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_NONE;
    }
    return 0;
}

static int fab_id_in_list(const char* id, const char** list, u32 count)
{
    u32 i;
    if (!id || !list) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (fab_str_eq(list[i], id)) {
            return 1;
        }
    }
    return 0;
}

static int fab_params_find(const dom_fab_param_value* params,
                           u32 count,
                           const char* param_id,
                           const dom_fab_param_value** out_param)
{
    u32 i;
    if (out_param) {
        *out_param = 0;
    }
    if (!params || !param_id) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (fab_str_eq(params[i].param_id, param_id)) {
            if (out_param) {
                *out_param = &params[i];
            }
            return 1;
        }
    }
    return 0;
}

static u32 fab_select_outcome(const dom_fab_process_family* family,
                              u32 seed)
{
    d_rng_state rng;
    u32 total = 0u;
    u32 i;
    if (!family || !family->yield_distribution || family->yield_count == 0u) {
        return 0u;
    }
    for (i = 0u; i < family->yield_count; ++i) {
        total += family->yield_distribution[i].weight;
    }
    if (total == 0u) {
        return 0u;
    }
    d_rng_seed(&rng, seed);
    {
        u32 roll = d_rng_next_u32(&rng) % total;
        u32 acc = 0u;
        for (i = 0u; i < family->yield_count; ++i) {
            acc += family->yield_distribution[i].weight;
            if (roll < acc) {
                return family->yield_distribution[i].outcome_id;
            }
        }
    }
    return 0u;
}

static void fab_sort_io_indices(const dom_fab_process_io* io,
                                u32 count,
                                u32* indices)
{
    u32 i;
    if (!io || !indices) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        indices[i] = i;
    }
    for (i = 1u; i < count; ++i) {
        u32 key = indices[i];
        u32 j = i;
        while (j > 0u && io[indices[j - 1u]].io_id > io[key].io_id) {
            indices[j] = indices[j - 1u];
            --j;
        }
        indices[j] = key;
    }
}

int dom_fab_process_execute(const dom_fab_process_family* family,
                            const dom_fab_process_context* ctx,
                            dom_fab_process_result* out_result)
{
    u32 i;
    if (out_result) {
        memset(out_result, 0, sizeof(*out_result));
        out_result->ok = 0;
        out_result->refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
        out_result->failure_mode_id = 0u;
        out_result->outcome_id = 0u;
        out_result->cost_units = 0u;
    }
    if (!family || !out_result) {
        return -1;
    }
    if (family->required_instruments && family->instrument_count > 0u) {
        for (i = 0u; i < family->instrument_count; ++i) {
            if (!fab_id_in_list(family->required_instruments[i],
                                ctx ? ctx->instrument_ids : 0,
                                ctx ? ctx->instrument_count : 0u)) {
                out_result->refusal_code = DOM_FAB_REFUSE_CAPABILITY_MISSING;
                return -2;
            }
        }
    }
    if (family->required_standards && family->standard_count > 0u) {
        for (i = 0u; i < family->standard_count; ++i) {
            if (!fab_id_in_list(family->required_standards[i],
                                ctx ? ctx->standard_ids : 0,
                                ctx ? ctx->standard_count : 0u)) {
                out_result->refusal_code = DOM_FAB_REFUSE_CAPABILITY_MISSING;
                return -3;
            }
        }
    }
    if (family->parameter_space && family->parameter_count > 0u) {
        for (i = 0u; i < family->parameter_count; ++i) {
            const dom_fab_param_range* range = &family->parameter_space[i];
            const dom_fab_param_value* param = 0;
            if (!fab_params_find(ctx ? ctx->parameters : 0,
                                 ctx ? ctx->parameter_count : 0u,
                                 range->param_id,
                                 &param)) {
                out_result->refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                return -4;
            }
            if (!fab_str_eq(param->unit_id, range->unit_id)) {
                out_result->refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                return -5;
            }
            if (param->value_q48 < range->min_q48 || param->value_q48 > range->max_q48) {
                out_result->refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                return -6;
            }
        }
    }
    if (family->constraints && family->constraint_count > 0u) {
        dom_fab_constraint_context cctx;
        u32 refusal = DOM_FAB_REFUSE_NONE;
        cctx.values = ctx ? ctx->parameters : 0;
        cctx.value_count = ctx ? ctx->parameter_count : 0u;
        if (dom_fab_constraints_eval(family->constraints, family->constraint_count, &cctx, &refusal) != 0) {
            out_result->refusal_code = refusal ? refusal : DOM_FAB_REFUSE_INVALID_INTENT;
            return -7;
        }
    }

    {
        u32 seed = (ctx ? ctx->rng_seed : 0u) ^ fab_hash32(family->process_family_id);
        u32 outcome_id = fab_select_outcome(family, seed);
        out_result->outcome_id = outcome_id;
        if (outcome_id != 0u) {
            out_result->ok = 0;
            out_result->failure_mode_id = outcome_id;
            out_result->refusal_code = DOM_FAB_REFUSE_NONE;
            return 0;
        }
    }
    out_result->ok = 1;
    out_result->refusal_code = DOM_FAB_REFUSE_NONE;
    return 0;
}

int dom_fab_process_family_to_desc(const dom_fab_process_family* family,
                                   dom_process_desc* out_desc,
                                   dom_process_io_desc* io_storage,
                                   u32 io_storage_cap)
{
    u32 total_io;
    u32 i;
    u32 offset = 0u;
    u32* input_idx = 0;
    u32* output_idx = 0;
    u32* waste_idx = 0;
    if (!family || !out_desc || !io_storage) {
        return -1;
    }
    total_io = family->input_count + family->output_count + family->waste_count;
    if (io_storage_cap < total_io) {
        return -2;
    }
    memset(out_desc, 0, sizeof(*out_desc));
    out_desc->id = (dom_process_id)fab_hash32(family->process_family_id);
    out_desc->process_class = DOM_PROCESS_TRANSFORMATIVE;
    out_desc->input_count = family->input_count;
    out_desc->output_count = family->output_count;
    out_desc->waste_count = family->waste_count;
    if (family->input_count > 0u) {
        input_idx = (u32*)malloc(sizeof(u32) * (size_t)family->input_count);
        fab_sort_io_indices(family->inputs, family->input_count, input_idx);
    }
    if (family->output_count > 0u) {
        output_idx = (u32*)malloc(sizeof(u32) * (size_t)family->output_count);
        fab_sort_io_indices(family->outputs, family->output_count, output_idx);
    }
    if (family->waste_count > 0u) {
        waste_idx = (u32*)malloc(sizeof(u32) * (size_t)family->waste_count);
        fab_sort_io_indices(family->waste, family->waste_count, waste_idx);
    }

    out_desc->inputs = (family->input_count > 0u) ? &io_storage[offset] : 0;
    for (i = 0u; i < family->input_count; ++i) {
        const dom_fab_process_io* io = &family->inputs[input_idx ? input_idx[i] : i];
        io_storage[offset].io_id = io->io_id;
        io_storage[offset].unit_id = fab_hash32(io->quantity.unit_id);
        io_storage[offset].quantity_q16 = (u32)io->quantity.value_q48;
        io_storage[offset].flags = 0u;
        io_storage[offset].kind = DOM_PROCESS_IO_INPUT;
        offset += 1u;
    }
    out_desc->outputs = (family->output_count > 0u) ? &io_storage[offset] : 0;
    for (i = 0u; i < family->output_count; ++i) {
        const dom_fab_process_io* io = &family->outputs[output_idx ? output_idx[i] : i];
        io_storage[offset].io_id = io->io_id;
        io_storage[offset].unit_id = fab_hash32(io->quantity.unit_id);
        io_storage[offset].quantity_q16 = (u32)io->quantity.value_q48;
        io_storage[offset].flags = 0u;
        io_storage[offset].kind = DOM_PROCESS_IO_OUTPUT;
        offset += 1u;
    }
    out_desc->waste = (family->waste_count > 0u) ? &io_storage[offset] : 0;
    for (i = 0u; i < family->waste_count; ++i) {
        const dom_fab_process_io* io = &family->waste[waste_idx ? waste_idx[i] : i];
        io_storage[offset].io_id = io->io_id;
        io_storage[offset].unit_id = fab_hash32(io->quantity.unit_id);
        io_storage[offset].quantity_q16 = (u32)io->quantity.value_q48;
        io_storage[offset].flags = 0u;
        io_storage[offset].kind = DOM_PROCESS_IO_WASTE;
        offset += 1u;
    }
    if (input_idx) free(input_idx);
    if (output_idx) free(output_idx);
    if (waste_idx) free(waste_idx);
    return 0;
}

/*------------------------------------------------------------
 * Quality and failure hooks
 *------------------------------------------------------------*/

int dom_fab_quality_evaluate(const dom_fab_quality_desc* quality,
                             const dom_fab_quality_measurement* measurements,
                             u32 measurement_count,
                             u32* out_refusal_code)
{
    u32 i;
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
    }
    if (!quality) {
        return -1;
    }
    for (i = 0u; i < quality->rule_count; ++i) {
        const dom_fab_quality_rule* rule = &quality->rules[i];
        u32 j;
        int found = 0;
        for (j = 0u; j < measurement_count; ++j) {
            if (fab_str_eq(measurements[j].metric_id, rule->metric_id)) {
                found = 1;
                if (!fab_str_eq(measurements[j].unit_id, rule->unit_id)) {
                    if (out_refusal_code) {
                        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                    }
                    return -2;
                }
                if (measurements[j].value_q48 < rule->min_q48 ||
                    measurements[j].value_q48 > rule->max_q48) {
                    if (out_refusal_code) {
                        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                    }
                    return -3;
                }
                break;
            }
        }
        if (!found) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
            }
            return -4;
        }
    }
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_NONE;
    }
    return 0;
}

int dom_fab_failure_apply(const dom_fab_failure_model* model,
                          dom_fab_material* material,
                          u32* out_refusal_code)
{
    u32 i;
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
    }
    if (!model || !material || !material->traits) {
        return -1;
    }
    for (i = 0u; i < model->rule_count; ++i) {
        const dom_fab_failure_rule* rule = &model->rules[i];
        u32 j;
        int found = 0;
        for (j = 0u; j < material->trait_count; ++j) {
            if (fab_str_eq(material->traits[j].trait_id, rule->trait_id)) {
                found = 1;
                if (rule->mode == DOM_FAB_FAILURE_ADD) {
                    q48_16 next = 0;
                    if (fab_checked_add_q48(material->traits[j].value_q48,
                                            rule->value_q48, &next) != 0) {
                        if (out_refusal_code) {
                            *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
                        }
                        return -2;
                    }
                    material->traits[j].value_q48 = next;
                } else if (rule->mode == DOM_FAB_FAILURE_MULTIPLY) {
                    material->traits[j].value_q48 =
                        d_q48_16_mul(material->traits[j].value_q48, rule->value_q48);
                }
                break;
            }
        }
        if (!found) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
            }
            return -3;
        }
    }
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_NONE;
    }
    return 0;
}

/*------------------------------------------------------------
 * Placement / volume claims
 *------------------------------------------------------------*/

int dom_fab_volume_claim_register(dom_volume_claim_registry* reg,
                                  const dom_fab_volume_claim_desc* claim,
                                  dom_physical_audit_log* audit,
                                  dom_act_time_t now_act,
                                  u32* out_refusal_code)
{
    dom_volume_claim c;
    int rc;
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
    }
    if (!reg || !claim) {
        return -1;
    }
    memset(&c, 0, sizeof(c));
    c.claim_id = claim->claim_id;
    c.owner_id = claim->owner_id;
    c.min_x = claim->min_x;
    c.min_y = claim->min_y;
    c.max_x = claim->max_x;
    c.max_y = claim->max_y;
    rc = dom_volume_claim_register(reg, &c, audit, now_act);
    if (rc == 0) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_FAB_REFUSE_NONE;
        }
        return 0;
    }
    if (rc == -3) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_FAB_REFUSE_DOMAIN_FORBIDDEN;
        }
        return -2;
    }
    if (out_refusal_code) {
        *out_refusal_code = DOM_FAB_REFUSE_INVALID_INTENT;
    }
    return -3;
}
