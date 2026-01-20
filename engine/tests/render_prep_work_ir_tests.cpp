/*
Render prep Work IR migration tests (ADOPT2).
*/
#include "render_prep_system.h"
#include "dominium/execution/system_registry.h"
#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"

#include <stdio.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static u64 fnv1a_init(void)
{
    return 1469598103934665603ULL;
}

static u64 fnv1a_u64(u64 h, u64 v)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        h ^= (u64)((v >> (i * 8u)) & 0xFFu);
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 fnv1a_u32(u64 h, u32 v)
{
    u32 i;
    for (i = 0u; i < 4u; ++i) {
        h ^= (u64)((v >> (i * 8u)) & 0xFFu);
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 hash_task_graph(const dom_task_graph* graph)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!graph || !graph->tasks) {
        return h;
    }
    h = fnv1a_u64(h, graph->graph_id);
    h = fnv1a_u64(h, graph->epoch_id);
    h = fnv1a_u32(h, graph->task_count);
    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* t = &graph->tasks[i];
        h = fnv1a_u64(h, t->task_id);
        h = fnv1a_u64(h, t->system_id);
        h = fnv1a_u32(h, t->category);
        h = fnv1a_u32(h, t->determinism_class);
        h = fnv1a_u32(h, t->fidelity_tier);
        h = fnv1a_u64(h, t->next_due_tick);
        h = fnv1a_u64(h, t->access_set_id);
        h = fnv1a_u64(h, t->cost_model_id);
        h = fnv1a_u32(h, t->law_target_count);
        h = fnv1a_u32(h, t->phase_id);
        h = fnv1a_u32(h, t->commit_key.phase_id);
        h = fnv1a_u64(h, t->commit_key.task_id);
        h = fnv1a_u32(h, t->commit_key.sub_index);
        if (t->policy_params && t->policy_params_size == sizeof(dom_render_prep_task_params)) {
            const dom_render_prep_task_params* params = (const dom_render_prep_task_params*)t->policy_params;
            h = fnv1a_u32(h, params->op);
            h = fnv1a_u32(h, params->fidelity);
            h = fnv1a_u32(h, params->pass_count);
            h = fnv1a_u32(h, params->flags);
            h = fnv1a_u64(h, params->frame_graph_id);
        }
    }
    return h;
}

static int emit_with_registry(dom_system_registry* registry,
                              dom_work_graph_builder* graph_builder,
                              dom_access_set_builder* access_builder,
                              dom_task_graph* out_graph)
{
    if (!registry || !graph_builder || !access_builder || !out_graph) {
        return -1;
    }
    dom_work_graph_builder_reset(graph_builder);
    dom_access_set_builder_reset(access_builder);
    dom_work_graph_builder_set_ids(graph_builder, 500u, 1u);
    if (dom_system_registry_emit(registry, 0, 10, graph_builder, access_builder) != 0) {
        return -2;
    }
    dom_work_graph_builder_finalize(graph_builder, out_graph);
    return 0;
}

static int test_deterministic_emission(void)
{
    dom_render_prep_inputs inputs;
    dom_render_prep_buffers buffers;
    RenderPrepSystem system;
    dom_system_registry registry;
    dom_system_entry entries[1];
    dom_task_node tasks[8];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[8];
    dom_access_set access_sets[8];
    dom_access_range reads[16];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_task_graph graph_a;
    dom_task_graph graph_b;
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    u64 hash_a;
    u64 hash_b;

    inputs.scene_id = 42u;
    inputs.packed_view_set_id = 1001u;
    inputs.visibility_mask_set_id = 2001u;
    inputs.visible_region_count = 12u;
    inputs.instance_count = 80u;

    buffers.visibility_buffer_id = 3001u;
    buffers.instance_buffer_id = 3002u;
    buffers.draw_list_buffer_id = 3003u;

    system.init(&inputs, &buffers);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register_render_prep(&registry, &system) == 0, "register render prep");
    EXPECT(dom_system_registry_set_fidelity(&registry, system.system_id(), DOM_FIDELITY_MICRO) == 0, "set fidelity");
    EXPECT(dom_system_registry_set_budget_hint(&registry, system.system_id(), 3u) == 0, "set budget");

    dom_work_graph_builder_init(&graph_builder, tasks, 8u, deps, 1u, barriers, 1u, costs, 8u);
    dom_access_set_builder_init(&access_builder, access_sets, 8u, reads, 16u, writes, 16u, reduces, 4u);

    EXPECT(emit_with_registry(&registry, &graph_builder, &access_builder, &graph_a) == 0, "emit A");
    hash_a = hash_task_graph(&graph_a);
    EXPECT(emit_with_registry(&registry, &graph_builder, &access_builder, &graph_b) == 0, "emit B");
    hash_b = hash_task_graph(&graph_b);

    EXPECT(hash_a == hash_b, "deterministic hash mismatch");
    return 0;
}

static int test_budget_degradation(void)
{
    dom_render_prep_inputs inputs;
    dom_render_prep_buffers buffers;
    RenderPrepSystem system;
    dom_system_registry registry;
    dom_system_entry entries[1];
    dom_task_node tasks[8];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[8];
    dom_access_set access_sets[8];
    dom_access_range reads[16];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_task_graph graph;
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    const dom_render_prep_task_params* params;

    inputs.scene_id = 7u;
    inputs.packed_view_set_id = 2001u;
    inputs.visibility_mask_set_id = 3001u;
    inputs.visible_region_count = 2u;
    inputs.instance_count = 5u;

    buffers.visibility_buffer_id = 4001u;
    buffers.instance_buffer_id = 4002u;
    buffers.draw_list_buffer_id = 4003u;

    system.init(&inputs, &buffers);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register_render_prep(&registry, &system) == 0, "register render prep");
    EXPECT(dom_system_registry_set_fidelity(&registry, system.system_id(), DOM_FIDELITY_FOCUS) == 0, "set fidelity");
    EXPECT(dom_system_registry_set_budget_hint(&registry, system.system_id(), 1u) == 0, "set budget");

    dom_work_graph_builder_init(&graph_builder, tasks, 8u, deps, 1u, barriers, 1u, costs, 8u);
    dom_access_set_builder_init(&access_builder, access_sets, 8u, reads, 16u, writes, 16u, reduces, 4u);

    EXPECT(emit_with_registry(&registry, &graph_builder, &access_builder, &graph) == 0, "emit budget");
    EXPECT(graph.task_count == 1u, "budget task count");
    params = (const dom_render_prep_task_params*)graph.tasks[0].policy_params;
    EXPECT(params != 0, "missing params");
    EXPECT(params->op == DOM_RENDER_PREP_OP_BUILD_DRAW_LIST, "budget op selection");
    return 0;
}

static int test_law_disable(void)
{
    dom_render_prep_inputs inputs;
    dom_render_prep_buffers buffers;
    RenderPrepSystem system;
    dom_system_registry registry;
    dom_system_entry entries[1];
    dom_task_node tasks[8];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[8];
    dom_access_set access_sets[8];
    dom_access_range reads[16];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_task_graph graph;
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;

    inputs.scene_id = 9u;
    inputs.packed_view_set_id = 1201u;
    inputs.visibility_mask_set_id = 1301u;
    inputs.visible_region_count = 3u;
    inputs.instance_count = 9u;

    buffers.visibility_buffer_id = 5001u;
    buffers.instance_buffer_id = 5002u;
    buffers.draw_list_buffer_id = 5003u;

    system.init(&inputs, &buffers);
    system.set_presentation_enabled(D_FALSE);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register_render_prep(&registry, &system) == 0, "register render prep");
    EXPECT(dom_system_registry_set_fidelity(&registry, system.system_id(), DOM_FIDELITY_MICRO) == 0, "set fidelity");

    dom_work_graph_builder_init(&graph_builder, tasks, 8u, deps, 1u, barriers, 1u, costs, 8u);
    dom_access_set_builder_init(&access_builder, access_sets, 8u, reads, 16u, writes, 16u, reduces, 4u);

    EXPECT(emit_with_registry(&registry, &graph_builder, &access_builder, &graph) == 0, "emit disabled");
    EXPECT(graph.task_count == 0u, "presentation disabled");
    return 0;
}

static int test_stale_fallback(void)
{
    dom_render_prep_inputs inputs;
    dom_render_prep_buffers buffers;
    RenderPrepSystem system;
    dom_system_registry registry;
    dom_system_entry entries[1];
    dom_task_node tasks[8];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[8];
    dom_access_set access_sets[8];
    dom_access_range reads[16];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_task_graph graph;
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    u64 frame_id_a;
    u64 frame_id_b;

    inputs.scene_id = 77u;
    inputs.packed_view_set_id = 2201u;
    inputs.visibility_mask_set_id = 2301u;
    inputs.visible_region_count = 6u;
    inputs.instance_count = 12u;

    buffers.visibility_buffer_id = 6001u;
    buffers.instance_buffer_id = 6002u;
    buffers.draw_list_buffer_id = 6003u;

    system.init(&inputs, &buffers);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register_render_prep(&registry, &system) == 0, "register render prep");
    EXPECT(dom_system_registry_set_budget_hint(&registry, system.system_id(), 3u) == 0, "set budget");

    dom_work_graph_builder_init(&graph_builder, tasks, 8u, deps, 1u, barriers, 1u, costs, 8u);
    dom_access_set_builder_init(&access_builder, access_sets, 8u, reads, 16u, writes, 16u, reduces, 4u);

    EXPECT(dom_system_registry_set_fidelity(&registry, system.system_id(), DOM_FIDELITY_MICRO) == 0, "set micro");
    EXPECT(emit_with_registry(&registry, &graph_builder, &access_builder, &graph) == 0, "emit micro");
    frame_id_a = system.last_frame_id();
    EXPECT(frame_id_a != 0u, "frame id set");

    EXPECT(dom_system_registry_set_fidelity(&registry, system.system_id(), DOM_FIDELITY_LATENT) == 0, "set latent");
    EXPECT(emit_with_registry(&registry, &graph_builder, &access_builder, &graph) == 0, "emit latent");
    frame_id_b = system.last_frame_id();
    EXPECT(graph.task_count == 0u, "latent emits no tasks");
    EXPECT(frame_id_a == frame_id_b, "stale frame reused");
    return 0;
}

int main(void)
{
    if (test_deterministic_emission() != 0) return 1;
    if (test_budget_degradation() != 0) return 1;
    if (test_law_disable() != 0) return 1;
    if (test_stale_fallback() != 0) return 1;
    return 0;
}
