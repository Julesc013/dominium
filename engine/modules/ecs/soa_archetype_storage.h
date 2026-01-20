/*
FILE: engine/modules/ecs/soa_archetype_storage.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: Deterministic SoA archetype storage backend (reference).
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: Stable ordering and commit semantics only.
*/
#ifndef DOMINO_ECS_SOA_ARCHETYPE_STORAGE_H
#define DOMINO_ECS_SOA_ARCHETYPE_STORAGE_H

#include "domino/ecs/ecs_storage_iface.h"
#include "soa_archetype_layout.h"

typedef struct dom_soa_access_rule {
    dom_archetype_id archetype_id;
    dom_component_id component_id;
    dom_field_id     field_id;
    u32              access_mode;
} dom_soa_access_rule;

typedef struct dom_soa_column {
    dom_component_id component_id;
    dom_field_id     field_id;
    u32              element_type;
    u32              element_size;
    u32              stride;
    u32              capacity;
    u32              size;
    unsigned char*   data;
} dom_soa_column;

typedef struct dom_soa_archetype {
    dom_archetype_id   archetype_id;
    dom_component_id*  component_set;
    u32                component_count;
    dom_soa_column*    columns;
    u32                column_count;
    dom_entity_id*     entities;
    u32                entity_count;
    u32                entity_capacity;
    dom_soa_access_rule* access_rules;
    u32                access_count;
    u32                access_capacity;
} dom_soa_archetype;

class dom_soa_archetype_storage : public IEcsStorageBackend {
public:
    dom_soa_archetype_storage();
    ~dom_soa_archetype_storage();

    int add_archetype(const dom_soa_component_def* components,
                      u32 component_count,
                      u32 initial_capacity);
    int reserve_entities(dom_archetype_id archetype, u32 capacity);
    int insert_entity(dom_archetype_id archetype, dom_entity_id entity);
    int remove_entity(dom_archetype_id archetype, dom_entity_id entity);
    int set_access_rule(dom_archetype_id archetype,
                        dom_component_id component_id,
                        dom_field_id field_id,
                        u32 access_mode);

    u64 read_u64(dom_archetype_id archetype,
                 dom_component_id component_id,
                 dom_field_id field_id,
                 u32 index) const;

    virtual dom_archetype_id get_archetype(dom_entity_id entity) const;
    virtual dom_entity_range query_archetype(dom_archetype_id archetype) const;
    virtual dom_component_view get_view(dom_archetype_id archetype,
                                        dom_component_id component,
                                        dom_field_id field);
    virtual void apply_writes(const dom_ecs_write_buffer& writes,
                              dom_ecs_commit_context& ctx);

private:
    dom_soa_archetype* find_archetype(dom_archetype_id archetype);
    const dom_soa_archetype* find_archetype(dom_archetype_id archetype) const;
    dom_soa_column* find_column(dom_soa_archetype* arch,
                                dom_component_id component_id,
                                dom_field_id field_id);
    const dom_soa_column* find_column(const dom_soa_archetype* arch,
                                      dom_component_id component_id,
                                      dom_field_id field_id) const;
    dom_soa_access_rule* find_access_rule(dom_soa_archetype* arch,
                                          dom_component_id component_id,
                                          dom_field_id field_id);
    const dom_soa_access_rule* find_access_rule(const dom_soa_archetype* arch,
                                                dom_component_id component_id,
                                                dom_field_id field_id) const;
    int ensure_capacity(dom_soa_archetype* arch, u32 capacity);
    void zero_new_rows(dom_soa_archetype* arch, u32 from_index, u32 to_index);
    int validate_write(const dom_ecs_write_op& op) const;
    void apply_write(const dom_ecs_write_op& op);
    void apply_reduce(const dom_ecs_write_op& op);

    dom_soa_archetype* archetypes_;
    u32                archetype_count_;
    u32                archetype_capacity_;
    u32*               sort_indices_;
    u32                sort_capacity_;
};

#endif /* DOMINO_ECS_SOA_ARCHETYPE_STORAGE_H */
