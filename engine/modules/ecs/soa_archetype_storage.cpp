/*
FILE: engine/modules/ecs/soa_archetype_storage.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: Deterministic SoA archetype storage backend.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: Stable ordering and deterministic commits only.
*/
#include "ecs/soa_archetype_storage.h"

#include <string.h>

static u64 dom_soa_hash_init(void)
{
    return 1469598103934665603ULL;
}

static u64 dom_soa_hash_u64(u64 hash, u64 v)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((v >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

extern "C" {

void dom_soa_sort_component_ids(dom_component_id* ids, u32 count)
{
    u32 i;
    if (!ids || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_component_id key = ids[i];
        u32 j = i;
        while (j > 0u && ids[j - 1u] > key) {
            ids[j] = ids[j - 1u];
            --j;
        }
        ids[j] = key;
    }
}

void dom_soa_sort_field_defs(dom_soa_field_def* fields, u32 count)
{
    u32 i;
    if (!fields || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_soa_field_def key = fields[i];
        u32 j = i;
        while (j > 0u && fields[j - 1u].field_id > key.field_id) {
            fields[j] = fields[j - 1u];
            --j;
        }
        fields[j] = key;
    }
}

d_bool dom_soa_component_set_is_sorted(const dom_component_id* ids, u32 count)
{
    u32 i;
    if (!ids) {
        return D_FALSE;
    }
    for (i = 1u; i < count; ++i) {
        if (ids[i - 1u] > ids[i]) {
            return D_FALSE;
        }
    }
    return D_TRUE;
}

dom_archetype_id dom_soa_archetype_id_from_components(const dom_component_id* ids, u32 count)
{
    u32 i;
    u64 hash = dom_soa_hash_init();
    if (!ids || count == 0u) {
        return dom_archetype_id_make(0u);
    }
    for (i = 0u; i < count; ++i) {
        hash = dom_soa_hash_u64(hash, (u64)ids[i]);
    }
    return dom_archetype_id_make(hash);
}

} /* extern "C" */

dom_soa_archetype_storage::dom_soa_archetype_storage()
    : archetypes_(0),
      archetype_count_(0u),
      archetype_capacity_(0u),
      sort_indices_(0),
      sort_capacity_(0u)
{
}

dom_soa_archetype_storage::~dom_soa_archetype_storage()
{
    u32 i;
    if (archetypes_) {
        for (i = 0u; i < archetype_count_; ++i) {
            dom_soa_archetype* arch = &archetypes_[i];
            u32 c;
            for (c = 0u; c < arch->column_count; ++c) {
                delete[] arch->columns[c].data;
            }
            delete[] arch->columns;
            delete[] arch->component_set;
            delete[] arch->entities;
            delete[] arch->access_rules;
        }
        delete[] archetypes_;
    }
    delete[] sort_indices_;
}

int dom_soa_archetype_storage::add_archetype(const dom_soa_component_def* components,
                                             u32 component_count,
                                             u32 initial_capacity)
{
    u32 i;
    u32 total_fields = 0u;
    dom_soa_component_def* sorted_components = 0;
    dom_soa_archetype* arch = 0;
    dom_soa_column* columns = 0;
    if (!components || component_count == 0u) {
        return -1;
    }

    sorted_components = new dom_soa_component_def[component_count];
    for (i = 0u; i < component_count; ++i) {
        sorted_components[i] = components[i];
        total_fields += components[i].field_count;
    }
    for (i = 1u; i < component_count; ++i) {
        dom_soa_component_def key = sorted_components[i];
        u32 j = i;
        while (j > 0u && sorted_components[j - 1u].component_id > key.component_id) {
            sorted_components[j] = sorted_components[j - 1u];
            --j;
        }
        sorted_components[j] = key;
    }

    if (!archetypes_) {
        archetype_capacity_ = 4u;
        archetypes_ = new dom_soa_archetype[archetype_capacity_];
        memset(archetypes_, 0, sizeof(dom_soa_archetype) * archetype_capacity_);
    } else if (archetype_count_ >= archetype_capacity_) {
        u32 new_capacity = archetype_capacity_ * 2u;
        dom_soa_archetype* next = new dom_soa_archetype[new_capacity];
        memset(next, 0, sizeof(dom_soa_archetype) * new_capacity);
        memcpy(next, archetypes_, sizeof(dom_soa_archetype) * archetype_count_);
        delete[] archetypes_;
        archetypes_ = next;
        archetype_capacity_ = new_capacity;
    }

    arch = &archetypes_[archetype_count_++];
    memset(arch, 0, sizeof(dom_soa_archetype));
    arch->component_set = new dom_component_id[component_count];
    for (i = 0u; i < component_count; ++i) {
        arch->component_set[i] = sorted_components[i].component_id;
    }
    arch->component_count = component_count;
    arch->archetype_id = dom_soa_archetype_id_from_components(arch->component_set, component_count);
    arch->entities = 0;
    arch->entity_count = 0u;
    arch->entity_capacity = 0u;
    arch->columns = 0;
    arch->column_count = total_fields;

    if (total_fields > 0u) {
        columns = new dom_soa_column[total_fields];
        memset(columns, 0, sizeof(dom_soa_column) * total_fields);
    }
    arch->columns = columns;

    {
        u32 col_index = 0u;
        for (i = 0u; i < component_count; ++i) {
            dom_soa_field_def* sorted_fields = 0;
            u32 f;
            if (sorted_components[i].field_count > 0u) {
                sorted_fields = new dom_soa_field_def[sorted_components[i].field_count];
                for (f = 0u; f < sorted_components[i].field_count; ++f) {
                    sorted_fields[f] = sorted_components[i].fields[f];
                }
                dom_soa_sort_field_defs(sorted_fields, sorted_components[i].field_count);
            }
            for (f = 0u; f < sorted_components[i].field_count; ++f) {
                dom_soa_column* col = &columns[col_index++];
                col->component_id = sorted_components[i].component_id;
                col->field_id = sorted_fields[f].field_id;
                col->element_type = sorted_fields[f].element_type;
                col->element_size = sorted_fields[f].element_size;
                col->stride = sorted_fields[f].element_size;
                col->capacity = 0u;
                col->size = 0u;
                col->data = 0;
            }
            delete[] sorted_fields;
        }
    }

    delete[] sorted_components;
    return reserve_entities(arch->archetype_id, initial_capacity);
}

int dom_soa_archetype_storage::reserve_entities(dom_archetype_id archetype, u32 capacity)
{
    dom_soa_archetype* arch = find_archetype(archetype);
    if (!arch) {
        return -1;
    }
    return ensure_capacity(arch, capacity);
}

int dom_soa_archetype_storage::insert_entity(dom_archetype_id archetype, dom_entity_id entity)
{
    u32 i;
    dom_soa_archetype* arch = find_archetype(archetype);
    if (!arch) {
        return -1;
    }
    for (i = 0u; i < arch->entity_count; ++i) {
        if (arch->entities[i] == entity) {
            return -2;
        }
    }
    if (ensure_capacity(arch, arch->entity_count + 1u) != 0) {
        return -3;
    }
    arch->entities[arch->entity_count] = entity;
    zero_new_rows(arch, arch->entity_count, arch->entity_count + 1u);
    arch->entity_count += 1u;
    return 0;
}

int dom_soa_archetype_storage::remove_entity(dom_archetype_id archetype, dom_entity_id entity)
{
    u32 i;
    dom_soa_archetype* arch = find_archetype(archetype);
    if (!arch) {
        return -1;
    }
    for (i = 0u; i < arch->entity_count; ++i) {
        if (arch->entities[i] == entity) {
            u32 remaining = arch->entity_count - i - 1u;
            if (remaining > 0u) {
                memmove(&arch->entities[i], &arch->entities[i + 1u],
                        sizeof(dom_entity_id) * remaining);
            }
            if (arch->entity_count > 0u) {
                u32 c;
                for (c = 0u; c < arch->column_count; ++c) {
                    dom_soa_column* col = &arch->columns[c];
                    size_t row_bytes = (size_t)col->stride;
                    unsigned char* base = col->data;
                    if (remaining > 0u) {
                        memmove(base + (size_t)i * row_bytes,
                                base + (size_t)(i + 1u) * row_bytes,
                                row_bytes * remaining);
                    }
                    col->size = arch->entity_count - 1u;
                }
            }
            arch->entity_count -= 1u;
            return 0;
        }
    }
    return -2;
}

int dom_soa_archetype_storage::set_access_rule(dom_archetype_id archetype,
                                               dom_component_id component_id,
                                               dom_field_id field_id,
                                               u32 access_mode)
{
    dom_soa_archetype* arch = find_archetype(archetype);
    dom_soa_access_rule* rule = 0;
    if (!arch) {
        return -1;
    }
    rule = find_access_rule(arch, component_id, field_id);
    if (!rule) {
        if (arch->access_count >= arch->access_capacity) {
            u32 new_capacity = (arch->access_capacity == 0u) ? 4u : arch->access_capacity * 2u;
            dom_soa_access_rule* next = new dom_soa_access_rule[new_capacity];
            if (arch->access_rules) {
                memcpy(next, arch->access_rules, sizeof(dom_soa_access_rule) * arch->access_count);
                delete[] arch->access_rules;
            }
            arch->access_rules = next;
            arch->access_capacity = new_capacity;
        }
        rule = &arch->access_rules[arch->access_count++];
        rule->archetype_id = archetype;
        rule->component_id = component_id;
        rule->field_id = field_id;
    }
    rule->access_mode = access_mode;
    return 0;
}

u64 dom_soa_archetype_storage::read_u64(dom_archetype_id archetype,
                                        dom_component_id component_id,
                                        dom_field_id field_id,
                                        u32 index) const
{
    const dom_soa_archetype* arch = find_archetype(archetype);
    const dom_soa_column* col = 0;
    u64 value = 0u;
    if (!arch) {
        return 0u;
    }
    col = find_column(arch, component_id, field_id);
    if (!col || index >= arch->entity_count || col->element_size != sizeof(u64)) {
        return 0u;
    }
    memcpy(&value, col->data + (size_t)index * col->stride, sizeof(u64));
    return value;
}

dom_archetype_id dom_soa_archetype_storage::get_archetype(dom_entity_id entity) const
{
    u32 i;
    for (i = 0u; i < archetype_count_; ++i) {
        u32 j;
        const dom_soa_archetype* arch = &archetypes_[i];
        for (j = 0u; j < arch->entity_count; ++j) {
            if (arch->entities[j] == entity) {
                return arch->archetype_id;
            }
        }
    }
    return dom_archetype_id_make(0u);
}

dom_entity_range dom_soa_archetype_storage::query_archetype(dom_archetype_id archetype) const
{
    dom_entity_range range;
    const dom_soa_archetype* arch = find_archetype(archetype);
    range.archetype_id = archetype;
    range.begin_index = 0u;
    range.end_index = arch ? arch->entity_count : 0u;
    return range;
}

dom_component_view dom_soa_archetype_storage::get_view(dom_archetype_id archetype,
                                                       dom_component_id component,
                                                       dom_field_id field)
{
    dom_component_view view;
    dom_soa_archetype* arch = find_archetype(archetype);
    const dom_soa_access_rule* rule = 0;
    dom_soa_column* col = 0;
    if (!arch) {
        return dom_component_view_invalid();
    }
    rule = find_access_rule(arch, component, field);
    if (!rule) {
        return dom_component_view_invalid();
    }
    col = find_column(arch, component, field);
    if (!col) {
        return dom_component_view_invalid();
    }
    view.component_id = component;
    view.field_id = field;
    view.element_type = col->element_type;
    view.element_size = col->element_size;
    view.stride = col->stride;
    view.count = arch->entity_count;
    view.access_mode = rule->access_mode;
    view.view_flags = DOM_ECS_VIEW_VALID;
    view.reserved = 0u;
    view.backend_token = (u64)(col - arch->columns);
    return view;
}

void dom_soa_archetype_storage::apply_writes(const dom_ecs_write_buffer& writes,
                                             dom_ecs_commit_context& ctx)
{
    u32 i;
    if (!writes.ops || writes.count == 0u) {
        ctx.status = 0;
        return;
    }
    if (writes.count > sort_capacity_) {
        delete[] sort_indices_;
        sort_capacity_ = writes.count;
        sort_indices_ = new u32[sort_capacity_];
    }
    for (i = 0u; i < writes.count; ++i) {
        if (!validate_write(writes.ops[i])) {
            ctx.status = -1;
            return;
        }
        sort_indices_[i] = i;
    }
    for (i = 1u; i < writes.count; ++i) {
        u32 key = sort_indices_[i];
        u32 j = i;
        while (j > 0u &&
               dom_commit_key_compare(&writes.ops[sort_indices_[j - 1u]].commit_key,
                                      &writes.ops[key].commit_key) > 0) {
            sort_indices_[j] = sort_indices_[j - 1u];
            --j;
        }
        sort_indices_[j] = key;
    }
    for (i = 0u; i < writes.count; ++i) {
        const dom_ecs_write_op& op = writes.ops[sort_indices_[i]];
        if (op.reduction_op != DOM_REDUCE_NONE) {
            apply_reduce(op);
        } else {
            apply_write(op);
        }
    }
    ctx.status = 0;
}

dom_soa_archetype* dom_soa_archetype_storage::find_archetype(dom_archetype_id archetype)
{
    u32 i;
    for (i = 0u; i < archetype_count_; ++i) {
        if (dom_archetype_id_equal(archetypes_[i].archetype_id, archetype)) {
            return &archetypes_[i];
        }
    }
    return 0;
}

const dom_soa_archetype* dom_soa_archetype_storage::find_archetype(dom_archetype_id archetype) const
{
    u32 i;
    for (i = 0u; i < archetype_count_; ++i) {
        if (dom_archetype_id_equal(archetypes_[i].archetype_id, archetype)) {
            return &archetypes_[i];
        }
    }
    return 0;
}

dom_soa_column* dom_soa_archetype_storage::find_column(dom_soa_archetype* arch,
                                                       dom_component_id component_id,
                                                       dom_field_id field_id)
{
    u32 i;
    if (!arch) {
        return 0;
    }
    for (i = 0u; i < arch->column_count; ++i) {
        if (arch->columns[i].component_id == component_id &&
            arch->columns[i].field_id == field_id) {
            return &arch->columns[i];
        }
    }
    return 0;
}

const dom_soa_column* dom_soa_archetype_storage::find_column(const dom_soa_archetype* arch,
                                                             dom_component_id component_id,
                                                             dom_field_id field_id) const
{
    u32 i;
    if (!arch) {
        return 0;
    }
    for (i = 0u; i < arch->column_count; ++i) {
        if (arch->columns[i].component_id == component_id &&
            arch->columns[i].field_id == field_id) {
            return &arch->columns[i];
        }
    }
    return 0;
}

dom_soa_access_rule* dom_soa_archetype_storage::find_access_rule(dom_soa_archetype* arch,
                                                                 dom_component_id component_id,
                                                                 dom_field_id field_id)
{
    u32 i;
    if (!arch || !arch->access_rules) {
        return 0;
    }
    for (i = 0u; i < arch->access_count; ++i) {
        if (arch->access_rules[i].component_id == component_id &&
            arch->access_rules[i].field_id == field_id) {
            return &arch->access_rules[i];
        }
    }
    return 0;
}

const dom_soa_access_rule* dom_soa_archetype_storage::find_access_rule(const dom_soa_archetype* arch,
                                                                       dom_component_id component_id,
                                                                       dom_field_id field_id) const
{
    u32 i;
    if (!arch || !arch->access_rules) {
        return 0;
    }
    for (i = 0u; i < arch->access_count; ++i) {
        if (arch->access_rules[i].component_id == component_id &&
            arch->access_rules[i].field_id == field_id) {
            return &arch->access_rules[i];
        }
    }
    return 0;
}

int dom_soa_archetype_storage::ensure_capacity(dom_soa_archetype* arch, u32 capacity)
{
    u32 i;
    if (!arch) {
        return -1;
    }
    if (capacity <= arch->entity_capacity) {
        return 0;
    }
    {
        u32 new_capacity = arch->entity_capacity ? arch->entity_capacity : 1u;
        while (new_capacity < capacity) {
            new_capacity *= 2u;
        }
        dom_entity_id* next_entities = new dom_entity_id[new_capacity];
        if (arch->entities && arch->entity_count > 0u) {
            memcpy(next_entities, arch->entities, sizeof(dom_entity_id) * arch->entity_count);
        }
        delete[] arch->entities;
        arch->entities = next_entities;
        arch->entity_capacity = new_capacity;
        for (i = 0u; i < arch->column_count; ++i) {
            dom_soa_column* col = &arch->columns[i];
            unsigned char* next = new unsigned char[(size_t)new_capacity * col->stride];
            if (col->data && col->size > 0u) {
                memcpy(next, col->data, (size_t)col->size * col->stride);
            }
            delete[] col->data;
            col->data = next;
            col->capacity = new_capacity;
        }
    }
    return 0;
}

void dom_soa_archetype_storage::zero_new_rows(dom_soa_archetype* arch, u32 from_index, u32 to_index)
{
    u32 i;
    if (!arch) {
        return;
    }
    for (i = 0u; i < arch->column_count; ++i) {
        dom_soa_column* col = &arch->columns[i];
        if (!col->data || col->stride == 0u) {
            continue;
        }
        if (to_index > from_index) {
            size_t offset = (size_t)from_index * col->stride;
            size_t bytes = (size_t)(to_index - from_index) * col->stride;
            memset(col->data + offset, 0, bytes);
        }
        col->size = arch->entity_count + (to_index - from_index);
    }
}

int dom_soa_archetype_storage::validate_write(const dom_ecs_write_op& op) const
{
    const dom_soa_archetype* arch = find_archetype(op.archetype_id);
    const dom_soa_column* col;
    const dom_soa_access_rule* rule;
    u32 count;
    if (!arch) {
        return 0;
    }
    col = find_column(arch, op.component_id, op.field_id);
    if (!col) {
        return 0;
    }
    rule = find_access_rule(arch, op.component_id, op.field_id);
    if (!rule) {
        return 0;
    }
    if ((op.access_mode & rule->access_mode) != op.access_mode) {
        return 0;
    }
    if (!dom_entity_range_is_valid(&op.range)) {
        return 0;
    }
    count = dom_entity_range_count(&op.range);
    if (op.range.begin_index + count > arch->entity_count) {
        return 0;
    }
    if (op.element_type != col->element_type) {
        return 0;
    }
    if (op.element_size != col->element_size || op.stride < col->element_size) {
        return 0;
    }
    if (!op.data) {
        return 0;
    }
    if (op.reduction_op == DOM_REDUCE_NONE &&
        (op.access_mode & DOM_ECS_ACCESS_WRITE) == 0u) {
        return 0;
    }
    if (op.reduction_op != DOM_REDUCE_NONE &&
        (op.access_mode & DOM_ECS_ACCESS_REDUCE) == 0u) {
        return 0;
    }
    if (op.reduction_op != DOM_REDUCE_NONE) {
        if (op.reduction_op != DOM_REDUCE_INT_SUM &&
            op.reduction_op != DOM_REDUCE_INT_MIN &&
            op.reduction_op != DOM_REDUCE_INT_MAX) {
            return 0;
        }
        if (col->element_type != DOM_ECS_ELEM_U64 &&
            col->element_type != DOM_ECS_ELEM_U32 &&
            col->element_type != DOM_ECS_ELEM_I64 &&
            col->element_type != DOM_ECS_ELEM_I32) {
            return 0;
        }
    }
    return 1;
}

void dom_soa_archetype_storage::apply_write(const dom_ecs_write_op& op)
{
    dom_soa_archetype* arch = find_archetype(op.archetype_id);
    dom_soa_column* col = 0;
    u32 count;
    u32 i;
    if (!arch) {
        return;
    }
    col = find_column(arch, op.component_id, op.field_id);
    if (!col || !op.data) {
        return;
    }
    count = dom_entity_range_count(&op.range);
    for (i = 0u; i < count; ++i) {
        size_t src_offset = (size_t)i * op.stride;
        size_t dst_offset = (size_t)(op.range.begin_index + i) * col->stride;
        memcpy(col->data + dst_offset, (const unsigned char*)op.data + src_offset, col->element_size);
    }
}

void dom_soa_archetype_storage::apply_reduce(const dom_ecs_write_op& op)
{
    dom_soa_archetype* arch = find_archetype(op.archetype_id);
    dom_soa_column* col = 0;
    u32 count;
    u32 i;
    if (!arch) {
        return;
    }
    col = find_column(arch, op.component_id, op.field_id);
    if (!col || !op.data) {
        return;
    }
    count = dom_entity_range_count(&op.range);
    for (i = 0u; i < count; ++i) {
        size_t src_offset = (size_t)i * op.stride;
        size_t dst_offset = (size_t)(op.range.begin_index + i) * col->stride;
        if (col->element_type == DOM_ECS_ELEM_U64) {
            u64 cur;
            u64 incoming;
            memcpy(&cur, col->data + dst_offset, sizeof(u64));
            memcpy(&incoming, (const unsigned char*)op.data + src_offset, sizeof(u64));
            if (op.reduction_op == DOM_REDUCE_INT_SUM) {
                cur += incoming;
            } else if (op.reduction_op == DOM_REDUCE_INT_MIN) {
                cur = (incoming < cur) ? incoming : cur;
            } else if (op.reduction_op == DOM_REDUCE_INT_MAX) {
                cur = (incoming > cur) ? incoming : cur;
            }
            memcpy(col->data + dst_offset, &cur, sizeof(u64));
        } else if (col->element_type == DOM_ECS_ELEM_U32) {
            u32 cur32;
            u32 incoming32;
            memcpy(&cur32, col->data + dst_offset, sizeof(u32));
            memcpy(&incoming32, (const unsigned char*)op.data + src_offset, sizeof(u32));
            if (op.reduction_op == DOM_REDUCE_INT_SUM) {
                cur32 += incoming32;
            } else if (op.reduction_op == DOM_REDUCE_INT_MIN) {
                cur32 = (incoming32 < cur32) ? incoming32 : cur32;
            } else if (op.reduction_op == DOM_REDUCE_INT_MAX) {
                cur32 = (incoming32 > cur32) ? incoming32 : cur32;
            }
            memcpy(col->data + dst_offset, &cur32, sizeof(u32));
        } else if (col->element_type == DOM_ECS_ELEM_I64) {
            i64 cur64;
            i64 incoming64;
            memcpy(&cur64, col->data + dst_offset, sizeof(i64));
            memcpy(&incoming64, (const unsigned char*)op.data + src_offset, sizeof(i64));
            if (op.reduction_op == DOM_REDUCE_INT_SUM) {
                cur64 += incoming64;
            } else if (op.reduction_op == DOM_REDUCE_INT_MIN) {
                cur64 = (incoming64 < cur64) ? incoming64 : cur64;
            } else if (op.reduction_op == DOM_REDUCE_INT_MAX) {
                cur64 = (incoming64 > cur64) ? incoming64 : cur64;
            }
            memcpy(col->data + dst_offset, &cur64, sizeof(i64));
        } else if (col->element_type == DOM_ECS_ELEM_I32) {
            i32 cur32;
            i32 incoming32;
            memcpy(&cur32, col->data + dst_offset, sizeof(i32));
            memcpy(&incoming32, (const unsigned char*)op.data + src_offset, sizeof(i32));
            if (op.reduction_op == DOM_REDUCE_INT_SUM) {
                cur32 += incoming32;
            } else if (op.reduction_op == DOM_REDUCE_INT_MIN) {
                cur32 = (incoming32 < cur32) ? incoming32 : cur32;
            } else if (op.reduction_op == DOM_REDUCE_INT_MAX) {
                cur32 = (incoming32 > cur32) ? incoming32 : cur32;
            }
            memcpy(col->data + dst_offset, &cur32, sizeof(i32));
        }
    }
}
