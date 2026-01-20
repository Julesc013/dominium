/*
ECS packed view tests (ECSX3).
*/
#include "domino/ecs/ecs_packed_view.h"
#include "domino/ecs/ecs_delta_codec.h"

#include <string.h>
#include <stdio.h>

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

static dom_packed_field_desc make_field(dom_component_id component_id,
                                        dom_field_id field_id,
                                        u32 element_type,
                                        u32 element_size)
{
    dom_packed_field_desc desc;
    desc.component_id = component_id;
    desc.field_id = field_id;
    desc.element_type = element_type;
    desc.element_size = element_size;
    desc.flags = DOM_PACK_FIELD_NONE;
    desc.quant_bits = 0u;
    return desc;
}

static int test_deterministic_pack_output(void)
{
    dom_packed_field_desc fields[2];
    dom_packed_field_source sources[2];
    u32 data_a[3] = { 0x11223344u, 0x55667788u, 0x99AABBCCu };
    u16 data_b[3] = { 0x0102u, 0x0304u, 0x0506u };
    unsigned char buffer_a[18];
    unsigned char buffer_b[18];
    dom_packed_view view_a;
    dom_packed_view view_b;

    fields[0] = make_field(1u, 1u, DOM_ECS_ELEM_U32, sizeof(u32));
    fields[1] = make_field(2u, 1u, DOM_ECS_ELEM_U16, sizeof(u16));
    sources[0].data = data_a;
    sources[0].stride = sizeof(u32);
    sources[1].data = data_b;
    sources[1].stride = sizeof(u16);

    TEST_CHECK(dom_packed_view_init(&view_a, 1u, fields, 2u, 3u, buffer_a, sizeof(buffer_a)) == 0);
    TEST_CHECK(dom_packed_view_init(&view_b, 1u, fields, 2u, 3u, buffer_b, sizeof(buffer_b)) == 0);
    TEST_CHECK(dom_packed_view_rebuild(&view_a, sources, 2u) > 0);
    TEST_CHECK(dom_packed_view_rebuild(&view_b, sources, 2u) > 0);
    TEST_CHECK(memcmp(buffer_a, buffer_b, sizeof(buffer_a)) == 0);
    return 0;
}

static int test_deterministic_delta_output(void)
{
    dom_packed_field_desc fields[2];
    dom_packed_field_source sources_base[2];
    dom_packed_field_source sources_cur[2];
    u32 base_a[3] = { 1u, 2u, 3u };
    u16 base_b[3] = { 10u, 20u, 30u };
    u32 cur_a[3] = { 1u, 22u, 3u };
    u16 cur_b[3] = { 10u, 20u, 33u };
    unsigned char base_buf[18];
    unsigned char cur_buf[18];
    unsigned char delta_a[64];
    unsigned char delta_b[64];
    dom_packed_view base_view;
    dom_packed_view cur_view;
    dom_packed_delta_info info_a;
    dom_packed_delta_info info_b;

    fields[0] = make_field(1u, 1u, DOM_ECS_ELEM_U32, sizeof(u32));
    fields[1] = make_field(2u, 1u, DOM_ECS_ELEM_U16, sizeof(u16));
    sources_base[0].data = base_a;
    sources_base[0].stride = sizeof(u32);
    sources_base[1].data = base_b;
    sources_base[1].stride = sizeof(u16);
    sources_cur[0].data = cur_a;
    sources_cur[0].stride = sizeof(u32);
    sources_cur[1].data = cur_b;
    sources_cur[1].stride = sizeof(u16);

    TEST_CHECK(dom_packed_view_init(&base_view, 2u, fields, 2u, 3u, base_buf, sizeof(base_buf)) == 0);
    TEST_CHECK(dom_packed_view_init(&cur_view, 2u, fields, 2u, 3u, cur_buf, sizeof(cur_buf)) == 0);
    base_view.baseline_id = 42u;
    TEST_CHECK(dom_packed_view_rebuild(&base_view, sources_base, 2u) > 0);
    TEST_CHECK(dom_packed_view_rebuild(&cur_view, sources_cur, 2u) > 0);

    TEST_CHECK(dom_delta_build(&base_view, &cur_view, delta_a, sizeof(delta_a), &info_a) == 0);
    TEST_CHECK(dom_delta_build(&base_view, &cur_view, delta_b, sizeof(delta_b), &info_b) == 0);
    TEST_CHECK(info_a.changed_count == 2u);
    TEST_CHECK(info_a.total_bytes == info_b.total_bytes);
    TEST_CHECK(memcmp(delta_a, delta_b, info_a.total_bytes) == 0);
    return 0;
}

static int test_field_ordering_and_reject_unsorted(void)
{
    dom_packed_field_desc unsorted[2];
    dom_packed_field_desc sorted[2];
    dom_packed_field_source sources[2];
    unsigned char buffer[8];
    dom_packed_view view;
    u8 value_a[1] = { 0x33u };
    u16 value_b[1] = { 0x1122u };

    unsorted[0] = make_field(1u, 2u, DOM_ECS_ELEM_U16, sizeof(u16));
    unsorted[1] = make_field(1u, 1u, DOM_ECS_ELEM_U8, sizeof(u8));
    TEST_CHECK(dom_packed_view_init(&view, 3u, unsorted, 2u, 1u, buffer, sizeof(buffer)) != 0);

    sorted[0] = make_field(1u, 1u, DOM_ECS_ELEM_U8, sizeof(u8));
    sorted[1] = make_field(1u, 2u, DOM_ECS_ELEM_U16, sizeof(u16));
    sources[0].data = value_a;
    sources[0].stride = sizeof(u8);
    sources[1].data = value_b;
    sources[1].stride = sizeof(u16);

    TEST_CHECK(dom_packed_view_init(&view, 3u, sorted, 2u, 1u, buffer, sizeof(buffer)) == 0);
    TEST_CHECK(dom_packed_view_rebuild(&view, sources, 2u) > 0);
    TEST_CHECK(buffer[0] == 0x33u);
    TEST_CHECK(buffer[1] == 0x22u);
    TEST_CHECK(buffer[2] == 0x11u);
    return 0;
}

static int test_explicit_byte_order(void)
{
    dom_packed_field_desc fields[1];
    dom_packed_field_source sources[1];
    u32 value[1] = { 0x11223344u };
    unsigned char buffer[4];
    dom_packed_view view;

    fields[0] = make_field(1u, 1u, DOM_ECS_ELEM_U32, sizeof(u32));
    sources[0].data = value;
    sources[0].stride = sizeof(u32);

    TEST_CHECK(dom_packed_view_init(&view, 4u, fields, 1u, 1u, buffer, sizeof(buffer)) == 0);
    TEST_CHECK(dom_packed_view_rebuild(&view, sources, 1u) > 0);
    TEST_CHECK(buffer[0] == 0x44u);
    TEST_CHECK(buffer[1] == 0x33u);
    TEST_CHECK(buffer[2] == 0x22u);
    TEST_CHECK(buffer[3] == 0x11u);
    return 0;
}

static int test_incremental_rebuild_determinism(void)
{
    dom_packed_field_desc fields[2];
    dom_packed_field_source sources[2];
    u32 data_a[3] = { 7u, 8u, 9u };
    u16 data_b[3] = { 100u, 200u, 300u };
    unsigned char buffer_full[18];
    unsigned char buffer_step[18];
    dom_packed_view view_full;
    dom_packed_view view_step;
    int step_result;

    fields[0] = make_field(1u, 1u, DOM_ECS_ELEM_U32, sizeof(u32));
    fields[1] = make_field(2u, 1u, DOM_ECS_ELEM_U16, sizeof(u16));
    sources[0].data = data_a;
    sources[0].stride = sizeof(u32);
    sources[1].data = data_b;
    sources[1].stride = sizeof(u16);

    TEST_CHECK(dom_packed_view_init(&view_full, 5u, fields, 2u, 3u, buffer_full, sizeof(buffer_full)) == 0);
    TEST_CHECK(dom_packed_view_init(&view_step, 5u, fields, 2u, 3u, buffer_step, sizeof(buffer_step)) == 0);
    TEST_CHECK(dom_packed_view_rebuild(&view_full, sources, 2u) > 0);

    do {
        step_result = dom_packed_view_rebuild_step(&view_step, sources, 2u, 1u);
        TEST_CHECK(step_result >= 0);
    } while (step_result == 0);

    TEST_CHECK(memcmp(buffer_full, buffer_step, sizeof(buffer_full)) == 0);
    return 0;
}

int main(void)
{
    if (test_deterministic_pack_output() != 0) return 1;
    if (test_deterministic_delta_output() != 0) return 1;
    if (test_field_ordering_and_reject_unsorted() != 0) return 1;
    if (test_explicit_byte_order() != 0) return 1;
    if (test_incremental_rebuild_determinism() != 0) return 1;
    return 0;
}
