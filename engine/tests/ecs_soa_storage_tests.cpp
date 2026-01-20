/*
ECS SoA storage backend tests (ECSX2).
*/
#include "ecs/soa_archetype_storage.h"

#include <stdio.h>
#include <string.h>

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

static dom_soa_field_def make_u64_field(dom_field_id field_id)
{
    dom_soa_field_def def;
    def.field_id = field_id;
    def.element_type = DOM_ECS_ELEM_U64;
    def.element_size = sizeof(u64);
    return def;
}

static dom_soa_component_def make_component(dom_component_id component_id,
                                            dom_soa_field_def* fields,
                                            u32 field_count)
{
    dom_soa_component_def def;
    def.component_id = component_id;
    def.fields = fields;
    def.field_count = field_count;
    return def;
}

static int test_stable_archetype_id(void)
{
    dom_component_id ids_a[3] = { 3u, 1u, 2u };
    dom_component_id ids_b[3] = { 1u, 2u, 3u };
    dom_archetype_id a;
    dom_archetype_id b;

    dom_soa_sort_component_ids(ids_a, 3u);
    dom_soa_sort_component_ids(ids_b, 3u);
    a = dom_soa_archetype_id_from_components(ids_a, 3u);
    b = dom_soa_archetype_id_from_components(ids_b, 3u);
    TEST_CHECK(dom_archetype_id_equal(a, b) == D_TRUE);
    return 0;
}

static int test_entity_ordering_insert_remove(void)
{
    dom_soa_archetype_storage backend;
    dom_soa_field_def fields[1];
    dom_soa_component_def components[1];
    dom_component_id component_id = 10u;
    dom_archetype_id arch_id;
    dom_ecs_write_op op;
    dom_ecs_write_buffer buffer;
    dom_ecs_commit_context ctx;
    dom_entity_range range;
    u64 values[3] = { 100u, 101u, 102u };

    fields[0] = make_u64_field(1u);
    components[0] = make_component(component_id, fields, 1u);
    TEST_CHECK(backend.add_archetype(components, 1u, 4u) == 0);
    arch_id = dom_soa_archetype_id_from_components(&component_id, 1u);
    backend.set_access_rule(arch_id, component_id, 1u, DOM_ECS_ACCESS_READWRITE);

    TEST_CHECK(backend.insert_entity(arch_id, 100u) == 0);
    TEST_CHECK(backend.insert_entity(arch_id, 101u) == 0);
    TEST_CHECK(backend.insert_entity(arch_id, 102u) == 0);

    range.archetype_id = arch_id;
    range.begin_index = 0u;
    range.end_index = 3u;
    op.commit_key.phase_id = 0u;
    op.commit_key.task_id = 1u;
    op.commit_key.sub_index = 0u;
    op.archetype_id = arch_id;
    op.range = range;
    op.component_id = component_id;
    op.field_id = 1u;
    op.element_type = DOM_ECS_ELEM_U64;
    op.element_size = sizeof(u64);
    op.access_mode = DOM_ECS_ACCESS_WRITE;
    op.reduction_op = DOM_REDUCE_NONE;
    op.data = values;
    op.stride = sizeof(u64);
    buffer.ops = &op;
    buffer.count = 1u;
    ctx.epoch_id = 0u;
    ctx.graph_id = 0u;
    ctx.allow_rollback = D_FALSE;
    ctx.status = 0;
    backend.apply_writes(buffer, ctx);
    TEST_CHECK(ctx.status == 0);

    TEST_CHECK(backend.remove_entity(arch_id, 101u) == 0);
    TEST_CHECK(backend.read_u64(arch_id, component_id, 1u, 0u) == 100u);
    TEST_CHECK(backend.read_u64(arch_id, component_id, 1u, 1u) == 102u);
    return 0;
}

static int test_view_determinism(void)
{
    dom_soa_archetype_storage backend;
    dom_soa_field_def fields[1];
    dom_soa_component_def components[1];
    dom_component_id component_id = 20u;
    dom_archetype_id arch_id;
    dom_component_view a;
    dom_component_view b;

    fields[0] = make_u64_field(1u);
    components[0] = make_component(component_id, fields, 1u);
    backend.add_archetype(components, 1u, 2u);
    arch_id = dom_soa_archetype_id_from_components(&component_id, 1u);
    backend.set_access_rule(arch_id, component_id, 1u, DOM_ECS_ACCESS_READWRITE);
    backend.insert_entity(arch_id, 1u);
    backend.insert_entity(arch_id, 2u);

    a = backend.get_view(arch_id, component_id, 1u);
    b = backend.get_view(arch_id, component_id, 1u);
    TEST_CHECK(dom_component_view_is_valid(&a) == D_TRUE);
    TEST_CHECK(dom_component_view_is_valid(&b) == D_TRUE);
    TEST_CHECK(a.count == b.count);
    TEST_CHECK(a.backend_token == b.backend_token);
    TEST_CHECK(a.stride == b.stride);
    return 0;
}

static int test_commit_order(void)
{
    dom_soa_archetype_storage backend;
    dom_soa_field_def fields[1];
    dom_soa_component_def components[1];
    dom_component_id component_id = 30u;
    dom_archetype_id arch_id;
    dom_ecs_write_op ops[2];
    dom_ecs_write_buffer buffer;
    dom_ecs_commit_context ctx;
    dom_entity_range range;
    u64 data_a[2] = { 1u, 1u };
    u64 data_b[2] = { 9u, 9u };

    fields[0] = make_u64_field(1u);
    components[0] = make_component(component_id, fields, 1u);
    backend.add_archetype(components, 1u, 2u);
    arch_id = dom_soa_archetype_id_from_components(&component_id, 1u);
    backend.set_access_rule(arch_id, component_id, 1u, DOM_ECS_ACCESS_READWRITE);
    backend.insert_entity(arch_id, 1u);
    backend.insert_entity(arch_id, 2u);

    range.archetype_id = arch_id;
    range.begin_index = 0u;
    range.end_index = 2u;

    ops[0].commit_key.phase_id = 0u;
    ops[0].commit_key.task_id = 2u;
    ops[0].commit_key.sub_index = 0u;
    ops[0].archetype_id = arch_id;
    ops[0].range = range;
    ops[0].component_id = component_id;
    ops[0].field_id = 1u;
    ops[0].element_type = DOM_ECS_ELEM_U64;
    ops[0].element_size = sizeof(u64);
    ops[0].access_mode = DOM_ECS_ACCESS_WRITE;
    ops[0].reduction_op = DOM_REDUCE_NONE;
    ops[0].data = data_b;
    ops[0].stride = sizeof(u64);

    ops[1].commit_key.phase_id = 0u;
    ops[1].commit_key.task_id = 1u;
    ops[1].commit_key.sub_index = 0u;
    ops[1].archetype_id = arch_id;
    ops[1].range = range;
    ops[1].component_id = component_id;
    ops[1].field_id = 1u;
    ops[1].element_type = DOM_ECS_ELEM_U64;
    ops[1].element_size = sizeof(u64);
    ops[1].access_mode = DOM_ECS_ACCESS_WRITE;
    ops[1].reduction_op = DOM_REDUCE_NONE;
    ops[1].data = data_a;
    ops[1].stride = sizeof(u64);

    buffer.ops = ops;
    buffer.count = 2u;
    ctx.epoch_id = 0u;
    ctx.graph_id = 0u;
    ctx.allow_rollback = D_FALSE;
    ctx.status = 0;
    backend.apply_writes(buffer, ctx);
    TEST_CHECK(ctx.status == 0);
    TEST_CHECK(backend.read_u64(arch_id, component_id, 1u, 0u) == 9u);
    return 0;
}

static int test_reduction_ops(void)
{
    dom_soa_archetype_storage backend;
    dom_soa_field_def fields[1];
    dom_soa_component_def components[1];
    dom_component_id component_id = 40u;
    dom_archetype_id arch_id;
    dom_ecs_write_op ops[2];
    dom_ecs_write_buffer buffer;
    dom_ecs_commit_context ctx;
    dom_entity_range range;
    u64 base[2] = { 5u, 5u };
    u64 reduce[2] = { 3u, 7u };
    u64 reduce_min[2] = { 4u, 20u };
    u64 reduce_max[2] = { 9u, 1u };

    fields[0] = make_u64_field(1u);
    components[0] = make_component(component_id, fields, 1u);
    backend.add_archetype(components, 1u, 2u);
    arch_id = dom_soa_archetype_id_from_components(&component_id, 1u);
    backend.set_access_rule(arch_id, component_id, 1u, DOM_ECS_ACCESS_READWRITE | DOM_ECS_ACCESS_REDUCE);
    backend.insert_entity(arch_id, 1u);
    backend.insert_entity(arch_id, 2u);

    range.archetype_id = arch_id;
    range.begin_index = 0u;
    range.end_index = 2u;

    ops[0].commit_key.phase_id = 0u;
    ops[0].commit_key.task_id = 1u;
    ops[0].commit_key.sub_index = 0u;
    ops[0].archetype_id = arch_id;
    ops[0].range = range;
    ops[0].component_id = component_id;
    ops[0].field_id = 1u;
    ops[0].element_type = DOM_ECS_ELEM_U64;
    ops[0].element_size = sizeof(u64);
    ops[0].access_mode = DOM_ECS_ACCESS_WRITE;
    ops[0].reduction_op = DOM_REDUCE_NONE;
    ops[0].data = base;
    ops[0].stride = sizeof(u64);

    ops[1].commit_key.phase_id = 0u;
    ops[1].commit_key.task_id = 2u;
    ops[1].commit_key.sub_index = 0u;
    ops[1].archetype_id = arch_id;
    ops[1].range = range;
    ops[1].component_id = component_id;
    ops[1].field_id = 1u;
    ops[1].element_type = DOM_ECS_ELEM_U64;
    ops[1].element_size = sizeof(u64);
    ops[1].access_mode = DOM_ECS_ACCESS_REDUCE;
    ops[1].reduction_op = DOM_REDUCE_INT_SUM;
    ops[1].data = reduce;
    ops[1].stride = sizeof(u64);

    buffer.ops = ops;
    buffer.count = 2u;
    ctx.epoch_id = 0u;
    ctx.graph_id = 0u;
    ctx.allow_rollback = D_FALSE;
    ctx.status = 0;
    backend.apply_writes(buffer, ctx);
    TEST_CHECK(ctx.status == 0);
    TEST_CHECK(backend.read_u64(arch_id, component_id, 1u, 0u) == 8u);
    TEST_CHECK(backend.read_u64(arch_id, component_id, 1u, 1u) == 12u);

    ops[0].commit_key.task_id = 3u;
    ops[0].access_mode = DOM_ECS_ACCESS_REDUCE;
    ops[0].reduction_op = DOM_REDUCE_INT_MIN;
    ops[0].data = reduce_min;
    buffer.ops = ops;
    buffer.count = 1u;
    backend.apply_writes(buffer, ctx);
    TEST_CHECK(ctx.status == 0);
    TEST_CHECK(backend.read_u64(arch_id, component_id, 1u, 0u) == 4u);
    TEST_CHECK(backend.read_u64(arch_id, component_id, 1u, 1u) == 12u);

    ops[0].commit_key.task_id = 4u;
    ops[0].reduction_op = DOM_REDUCE_INT_MAX;
    ops[0].data = reduce_max;
    backend.apply_writes(buffer, ctx);
    TEST_CHECK(ctx.status == 0);
    TEST_CHECK(backend.read_u64(arch_id, component_id, 1u, 0u) == 9u);
    TEST_CHECK(backend.read_u64(arch_id, component_id, 1u, 1u) == 12u);
    return 0;
}

static int test_access_enforcement(void)
{
    dom_soa_archetype_storage backend;
    dom_soa_field_def fields[1];
    dom_soa_component_def components[1];
    dom_component_id component_id = 50u;
    dom_archetype_id arch_id;
    dom_component_view view;
    dom_ecs_write_op op;
    dom_ecs_write_buffer buffer;
    dom_ecs_commit_context ctx;
    dom_entity_range range;
    u64 data[1] = { 1u };

    fields[0] = make_u64_field(1u);
    components[0] = make_component(component_id, fields, 1u);
    backend.add_archetype(components, 1u, 1u);
    arch_id = dom_soa_archetype_id_from_components(&component_id, 1u);
    backend.insert_entity(arch_id, 1u);

    view = backend.get_view(arch_id, component_id, 1u);
    TEST_CHECK(dom_component_view_is_valid(&view) == D_FALSE);

    range.archetype_id = arch_id;
    range.begin_index = 0u;
    range.end_index = 1u;
    op.commit_key.phase_id = 0u;
    op.commit_key.task_id = 1u;
    op.commit_key.sub_index = 0u;
    op.archetype_id = arch_id;
    op.range = range;
    op.component_id = component_id;
    op.field_id = 1u;
    op.element_type = DOM_ECS_ELEM_U64;
    op.element_size = sizeof(u64);
    op.access_mode = DOM_ECS_ACCESS_WRITE;
    op.reduction_op = DOM_REDUCE_NONE;
    op.data = data;
    op.stride = sizeof(u64);
    buffer.ops = &op;
    buffer.count = 1u;
    ctx.epoch_id = 0u;
    ctx.graph_id = 0u;
    ctx.allow_rollback = D_FALSE;
    ctx.status = 0;
    backend.apply_writes(buffer, ctx);
    TEST_CHECK(ctx.status != 0);
    return 0;
}

class DummyBackend : public IEcsStorageBackend {
public:
    DummyBackend() : count_(0u) {}
    void seed(u32 count) { count_ = count; }
    virtual dom_archetype_id get_archetype(dom_entity_id) const { return dom_archetype_id_make(1u); }
    virtual dom_entity_range query_archetype(dom_archetype_id archetype) const {
        dom_entity_range range;
        range.archetype_id = archetype;
        range.begin_index = 0u;
        range.end_index = count_;
        return range;
    }
    virtual dom_component_view get_view(dom_archetype_id, dom_component_id component, dom_field_id field) {
        dom_component_view view;
        view.component_id = component;
        view.field_id = field;
        view.element_type = DOM_ECS_ELEM_U64;
        view.element_size = sizeof(u64);
        view.stride = sizeof(u64);
        view.count = count_;
        view.access_mode = DOM_ECS_ACCESS_READ;
        view.view_flags = DOM_ECS_VIEW_VALID;
        view.reserved = 0u;
        view.backend_token = 0u;
        return view;
    }
    virtual void apply_writes(const dom_ecs_write_buffer&, dom_ecs_commit_context& ctx) {
        ctx.status = 0;
    }
private:
    u32 count_;
};

static int test_backend_equivalence_stub(void)
{
    dom_soa_archetype_storage backend;
    DummyBackend dummy;
    dom_soa_field_def fields[1];
    dom_soa_component_def components[1];
    dom_component_id component_id = 60u;
    dom_archetype_id arch_id;
    dom_component_view view_a;
    dom_component_view view_b;

    fields[0] = make_u64_field(1u);
    components[0] = make_component(component_id, fields, 1u);
    backend.add_archetype(components, 1u, 3u);
    arch_id = dom_soa_archetype_id_from_components(&component_id, 1u);
    backend.set_access_rule(arch_id, component_id, 1u, DOM_ECS_ACCESS_READ);
    backend.insert_entity(arch_id, 1u);
    backend.insert_entity(arch_id, 2u);
    backend.insert_entity(arch_id, 3u);
    dummy.seed(3u);

    view_a = backend.get_view(arch_id, component_id, 1u);
    view_b = dummy.get_view(arch_id, component_id, 1u);

    TEST_CHECK(dom_component_view_is_valid(&view_a) == D_TRUE);
    TEST_CHECK(dom_component_view_is_valid(&view_b) == D_TRUE);
    TEST_CHECK(view_a.count == view_b.count);
    TEST_CHECK(view_a.element_size == view_b.element_size);
    return 0;
}

int main(void)
{
    if (test_stable_archetype_id() != 0) return 1;
    if (test_entity_ordering_insert_remove() != 0) return 1;
    if (test_view_determinism() != 0) return 1;
    if (test_commit_order() != 0) return 1;
    if (test_reduction_ops() != 0) return 1;
    if (test_access_enforcement() != 0) return 1;
    if (test_backend_equivalence_stub() != 0) return 1;
    return 0;
}
