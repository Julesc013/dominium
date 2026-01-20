/*
ECS storage interface tests (ECSX1).
*/
#include "domino/ecs/ecs_storage_iface.h"
#include "domino/ecs/ecs_entity_range.h"
#include "domino/ecs/ecs_component_view.h"

#include <string.h>
#include <stdio.h>

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

typedef struct test_archetype {
    dom_archetype_id archetype_id;
    u32              count;
} test_archetype;

typedef struct test_field_store {
    dom_archetype_id archetype_id;
    dom_component_id component_id;
    dom_field_id     field_id;
    u64              values[8];
    u32              count;
} test_field_store;

typedef struct test_access_rule {
    dom_archetype_id archetype_id;
    dom_component_id component_id;
    dom_field_id     field_id;
} test_access_rule;

class DummyBackend : public IEcsStorageBackend {
public:
    DummyBackend()
        : archetype_count_(0u),
          field_count_(0u),
          access_count_(0u)
    {
        memset(archetypes_, 0, sizeof(archetypes_));
        memset(fields_, 0, sizeof(fields_));
        memset(access_, 0, sizeof(access_));
    }

    void add_archetype(u64 id_value, u32 count)
    {
        if (archetype_count_ >= kMaxArchetypes) {
            return;
        }
        archetypes_[archetype_count_].archetype_id = dom_archetype_id_make(id_value);
        archetypes_[archetype_count_].count = count;
        archetype_count_ += 1u;
    }

    void add_field(u64 archetype_value, dom_component_id component_id, dom_field_id field_id, u64 base_value)
    {
        u32 i;
        if (field_count_ >= kMaxFields) {
            return;
        }
        fields_[field_count_].archetype_id = dom_archetype_id_make(archetype_value);
        fields_[field_count_].component_id = component_id;
        fields_[field_count_].field_id = field_id;
        fields_[field_count_].count = 0u;
        for (i = 0u; i < archetype_count_; ++i) {
            if (dom_archetype_id_equal(archetypes_[i].archetype_id,
                                       fields_[field_count_].archetype_id)) {
                fields_[field_count_].count = archetypes_[i].count;
                break;
            }
        }
        for (i = 0u; i < fields_[field_count_].count && i < 8u; ++i) {
            fields_[field_count_].values[i] = base_value + (u64)i;
        }
        field_count_ += 1u;
    }

    void allow_access(u64 archetype_value, dom_component_id component_id, dom_field_id field_id)
    {
        if (access_count_ >= kMaxAccess) {
            return;
        }
        access_[access_count_].archetype_id = dom_archetype_id_make(archetype_value);
        access_[access_count_].component_id = component_id;
        access_[access_count_].field_id = field_id;
        access_count_ += 1u;
    }

    u64 read_value(u64 archetype_value, dom_component_id component_id, dom_field_id field_id, u32 index) const
    {
        const test_field_store* store = find_field(dom_archetype_id_make(archetype_value), component_id, field_id);
        if (!store || index >= store->count) {
            return 0u;
        }
        return store->values[index];
    }

    virtual dom_archetype_id get_archetype(dom_entity_id entity) const
    {
        u32 i;
        for (i = 0u; i < archetype_count_; ++i) {
            if (entity < archetypes_[i].count) {
                return archetypes_[i].archetype_id;
            }
        }
        return dom_archetype_id_make(0u);
    }

    virtual dom_entity_range query_archetype(dom_archetype_id archetype) const
    {
        u32 i;
        dom_entity_range range;
        range.archetype_id = archetype;
        range.begin_index = 0u;
        range.end_index = 0u;
        for (i = 0u; i < archetype_count_; ++i) {
            if (dom_archetype_id_equal(archetypes_[i].archetype_id, archetype)) {
                range.end_index = archetypes_[i].count;
                break;
            }
        }
        return range;
    }

    virtual dom_component_view get_view(dom_archetype_id archetype,
                                        dom_component_id component,
                                        dom_field_id field)
    {
        dom_component_view view;
        const test_field_store* store = find_field(archetype, component, field);
        if (!store || !is_access_allowed(archetype, component, field)) {
            return dom_component_view_invalid();
        }
        view.component_id = component;
        view.field_id = field;
        view.element_type = DOM_ECS_ELEM_U64;
        view.element_size = sizeof(u64);
        view.stride = sizeof(u64);
        view.count = store->count;
        view.access_mode = DOM_ECS_ACCESS_READWRITE;
        view.view_flags = DOM_ECS_VIEW_VALID;
        view.reserved = 0u;
        view.backend_token = store_index(store);
        return view;
    }

    virtual void apply_writes(const dom_ecs_write_buffer& writes,
                              dom_ecs_commit_context& ctx)
    {
        u32 i;
        u32 sorted[16];
        if (!writes.ops || writes.count == 0u) {
            ctx.status = 0;
            return;
        }
        if (writes.count > 16u) {
            ctx.status = -1;
            return;
        }
        for (i = 0u; i < writes.count; ++i) {
            if (!validate_write(writes.ops[i])) {
                ctx.status = -2;
                return;
            }
            sorted[i] = i;
        }
        for (i = 1u; i < writes.count; ++i) {
            u32 key = sorted[i];
            u32 j = i;
            while (j > 0u &&
                   dom_commit_key_compare(&writes.ops[sorted[j - 1u]].commit_key,
                                          &writes.ops[key].commit_key) > 0) {
                sorted[j] = sorted[j - 1u];
                --j;
            }
            sorted[j] = key;
        }
        for (i = 0u; i < writes.count; ++i) {
            apply_write(writes.ops[sorted[i]]);
        }
        ctx.status = 0;
    }

private:
    static const u32 kMaxArchetypes = 4u;
    static const u32 kMaxFields = 8u;
    static const u32 kMaxAccess = 16u;

    const test_field_store* find_field(dom_archetype_id archetype,
                                       dom_component_id component_id,
                                       dom_field_id field_id) const
    {
        u32 i;
        for (i = 0u; i < field_count_; ++i) {
            if (dom_archetype_id_equal(fields_[i].archetype_id, archetype) &&
                fields_[i].component_id == component_id &&
                fields_[i].field_id == field_id) {
                return &fields_[i];
            }
        }
        return (const test_field_store*)0;
    }

    test_field_store* find_field_mut(dom_archetype_id archetype,
                                     dom_component_id component_id,
                                     dom_field_id field_id)
    {
        u32 i;
        for (i = 0u; i < field_count_; ++i) {
            if (dom_archetype_id_equal(fields_[i].archetype_id, archetype) &&
                fields_[i].component_id == component_id &&
                fields_[i].field_id == field_id) {
                return &fields_[i];
            }
        }
        return (test_field_store*)0;
    }

    d_bool is_access_allowed(dom_archetype_id archetype,
                             dom_component_id component_id,
                             dom_field_id field_id) const
    {
        u32 i;
        for (i = 0u; i < access_count_; ++i) {
            if (dom_archetype_id_equal(access_[i].archetype_id, archetype) &&
                access_[i].component_id == component_id &&
                access_[i].field_id == field_id) {
                return D_TRUE;
            }
        }
        return D_FALSE;
    }

    u64 store_index(const test_field_store* store) const
    {
        if (!store) {
            return 0u;
        }
        return (u64)(store - fields_);
    }

    d_bool validate_write(const dom_ecs_write_op& op) const
    {
        const test_field_store* store = find_field(op.archetype_id, op.component_id, op.field_id);
        u32 count = dom_entity_range_count(&op.range);
        if (!store) {
            return D_FALSE;
        }
        if (!dom_entity_range_is_valid(&op.range)) {
            return D_FALSE;
        }
        if (op.range.begin_index + count > store->count) {
            return D_FALSE;
        }
        if (op.element_type != DOM_ECS_ELEM_U64 || op.element_size != sizeof(u64)) {
            return D_FALSE;
        }
        if ((op.access_mode & DOM_ECS_ACCESS_WRITE) == 0u) {
            return D_FALSE;
        }
        if (op.reduction_op != DOM_REDUCE_NONE) {
            return D_FALSE;
        }
        return D_TRUE;
    }

    void apply_write(const dom_ecs_write_op& op)
    {
        u32 i;
        test_field_store* store = find_field_mut(op.archetype_id, op.component_id, op.field_id);
        u32 count = dom_entity_range_count(&op.range);
        const unsigned char* bytes = (const unsigned char*)op.data;
        if (!store || !bytes) {
            return;
        }
        for (i = 0u; i < count; ++i) {
            u32 offset = i * op.stride;
            u64 value;
            memcpy(&value, bytes + offset, sizeof(u64));
            store->values[op.range.begin_index + i] = value;
        }
    }

    test_archetype archetypes_[kMaxArchetypes];
    test_field_store fields_[kMaxFields];
    test_access_rule access_[kMaxAccess];
    u32 archetype_count_;
    u32 field_count_;
    u32 access_count_;
};

static int test_stable_iteration(void)
{
    DummyBackend backend;
    dom_entity_range a;
    dom_entity_range b;
    backend.add_archetype(1u, 4u);
    a = backend.query_archetype(dom_archetype_id_make(1u));
    b = backend.query_archetype(dom_archetype_id_make(1u));
    TEST_CHECK(dom_archetype_id_equal(a.archetype_id, b.archetype_id) == D_TRUE);
    TEST_CHECK(a.begin_index == b.begin_index);
    TEST_CHECK(a.end_index == b.end_index);
    return 0;
}

static int test_view_correctness(void)
{
    DummyBackend backend;
    dom_component_view view;
    backend.add_archetype(2u, 3u);
    backend.add_field(2u, 10u, 1u, 100u);
    backend.allow_access(2u, 10u, 1u);
    view = backend.get_view(dom_archetype_id_make(2u), 10u, 1u);
    TEST_CHECK(dom_component_view_is_valid(&view) == D_TRUE);
    TEST_CHECK(view.count == 3u);
    TEST_CHECK(view.component_id == 10u);
    TEST_CHECK(view.field_id == 1u);
    return 0;
}

static int test_access_enforcement(void)
{
    DummyBackend backend;
    dom_component_view view;
    backend.add_archetype(3u, 2u);
    backend.add_field(3u, 20u, 1u, 200u);
    backend.allow_access(3u, 20u, 1u);
    view = backend.get_view(dom_archetype_id_make(3u), 21u, 1u);
    TEST_CHECK(dom_component_view_is_valid(&view) == D_FALSE);
    return 0;
}

static int test_deterministic_commit(void)
{
    DummyBackend backend;
    dom_ecs_write_op ops[2];
    dom_ecs_write_buffer buffer;
    dom_ecs_commit_context ctx;
    dom_entity_range range;
    u64 data_a[2] = { 100u, 100u };
    u64 data_b[2] = { 200u, 200u };

    backend.add_archetype(4u, 2u);
    backend.add_field(4u, 30u, 1u, 0u);
    backend.allow_access(4u, 30u, 1u);

    range.archetype_id = dom_archetype_id_make(4u);
    range.begin_index = 0u;
    range.end_index = 2u;

    ops[0].commit_key.phase_id = 0u;
    ops[0].commit_key.task_id = 2u;
    ops[0].commit_key.sub_index = 0u;
    ops[0].archetype_id = dom_archetype_id_make(4u);
    ops[0].range = range;
    ops[0].component_id = 30u;
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
    ops[1].archetype_id = dom_archetype_id_make(4u);
    ops[1].range = range;
    ops[1].component_id = 30u;
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
    TEST_CHECK(backend.read_value(4u, 30u, 1u, 0u) == 200u);
    TEST_CHECK(backend.read_value(4u, 30u, 1u, 1u) == 200u);
    return 0;
}

static int test_backend_swap(void)
{
    DummyBackend a;
    DummyBackend b;
    dom_component_view view_a;
    dom_component_view view_b;

    a.add_archetype(5u, 3u);
    a.add_field(5u, 40u, 1u, 10u);
    a.allow_access(5u, 40u, 1u);

    b.add_archetype(5u, 3u);
    b.add_field(5u, 40u, 1u, 10u);
    b.allow_access(5u, 40u, 1u);

    view_a = a.get_view(dom_archetype_id_make(5u), 40u, 1u);
    view_b = b.get_view(dom_archetype_id_make(5u), 40u, 1u);

    TEST_CHECK(dom_component_view_is_valid(&view_a) == D_TRUE);
    TEST_CHECK(dom_component_view_is_valid(&view_b) == D_TRUE);
    TEST_CHECK(view_a.count == view_b.count);
    TEST_CHECK(a.read_value(5u, 40u, 1u, 2u) == b.read_value(5u, 40u, 1u, 2u));
    return 0;
}

int main(void)
{
    if (test_stable_iteration() != 0) return 1;
    if (test_view_correctness() != 0) return 1;
    if (test_access_enforcement() != 0) return 1;
    if (test_deterministic_commit() != 0) return 1;
    if (test_backend_swap() != 0) return 1;
    return 0;
}
