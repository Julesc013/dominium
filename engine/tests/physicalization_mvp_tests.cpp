/*
Physicalization MVP tests (PHYS-1/TestX).
*/
#include "dominium/physical/field_storage.h"
#include "dominium/physical/terrain_processes.h"
#include "dominium/physical/resource_processes.h"
#include "dominium/physical/parts_and_assemblies.h"
#include "dominium/physical/network_graph.h"
#include "dominium/physical/machine_ops.h"
#include "dominium/physical/infrastructure_effects.h"
#include "dominium/agents/agent_goal.h"
#include "dominium/agents/agent_planner.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static i32 q16(i32 v)
{
    return (i32)(v << 16);
}

static void init_basic_fields(dom_field_storage* storage,
                              dom_field_layer* layers,
                              i32* elevation,
                              i32* slope,
                              i32* bearing,
                              i32* pollution)
{
    dom_domain_volume_ref domain;
    domain.id = 1u;
    domain.version = 1u;
    dom_field_storage_init(storage, domain, 2u, 2u, 0u, layers, 4u);
    dom_field_layer_add(storage, DOM_FIELD_ELEVATION, DOM_FIELD_VALUE_Q16_16,
                        q16(0), DOM_FIELD_VALUE_UNKNOWN, elevation);
    dom_field_layer_add(storage, DOM_FIELD_SLOPE, DOM_FIELD_VALUE_Q16_16,
                        q16(0), DOM_FIELD_VALUE_UNKNOWN, slope);
    dom_field_layer_add(storage, DOM_FIELD_BEARING_CAPACITY, DOM_FIELD_VALUE_Q16_16,
                        q16(10), DOM_FIELD_VALUE_UNKNOWN, bearing);
    dom_field_layer_add(storage, DOM_FIELD_POLLUTION, DOM_FIELD_VALUE_Q16_16,
                        q16(0), DOM_FIELD_VALUE_UNKNOWN, pollution);
}

static int test_terrain_modification_determinism(void)
{
    dom_field_storage a;
    dom_field_storage b;
    dom_field_layer layers_a[4];
    dom_field_layer layers_b[4];
    i32 elevation_a[4];
    i32 slope_a[4];
    i32 bearing_a[4];
    i32 pollution_a[4];
    i32 elevation_b[4];
    i32 slope_b[4];
    i32 bearing_b[4];
    i32 pollution_b[4];
    dom_terrain_process_desc desc;
    dom_physical_process_context ctx;
    dom_physical_process_result result_a;
    dom_physical_process_result result_b;
    i32 value_a;
    i32 value_b;

    init_basic_fields(&a, layers_a, elevation_a, slope_a, bearing_a, pollution_a);
    init_basic_fields(&b, layers_b, elevation_b, slope_b, bearing_b, pollution_b);

    dom_terrain_process_desc_default(DOM_TERRAIN_EXCAVATE, &desc);
    desc.delta_q16 = q16(2);

    memset(&ctx, 0, sizeof(ctx));
    ctx.actor_id = 1u;
    ctx.capability_mask = DOM_PHYS_CAP_TERRAIN;
    ctx.authority_mask = DOM_PHYS_AUTH_TERRAIN;
    ctx.now_act = 10u;

    EXPECT(dom_terrain_apply_process(&a, &desc, 0u, 0u, &ctx, &result_a) == 0, "terrain apply a");
    EXPECT(dom_terrain_apply_process(&b, &desc, 0u, 0u, &ctx, &result_b) == 0, "terrain apply b");
    EXPECT(result_a.ok && result_b.ok, "terrain results ok");

    EXPECT(dom_field_get_value(&a, DOM_FIELD_ELEVATION, 0u, 0u, &value_a) == 0, "elevation a");
    EXPECT(dom_field_get_value(&b, DOM_FIELD_ELEVATION, 0u, 0u, &value_b) == 0, "elevation b");
    EXPECT(value_a == value_b, "deterministic elevation");
    return 0;
}

static int test_structure_support(void)
{
    dom_physical_part_desc part_desc;
    dom_assembly_part parts[2];
    dom_assembly_connection connections[1];
    dom_assembly assembly;
    u32 a_idx;
    u32 b_idx;

    memset(&part_desc, 0, sizeof(part_desc));
    part_desc.part_id = 100u;
    part_desc.flags = DOM_PART_FLAG_REQUIRES_SUPPORT;
    part_desc.interface_mask = DOM_PART_IFACE_MECHANICAL;

    dom_assembly_init(&assembly, 200u, parts, 2u, connections, 1u);
    EXPECT(dom_assembly_add_part(&assembly, &part_desc, &a_idx) == 0, "add part A");
    part_desc.part_id = 101u;
    EXPECT(dom_assembly_add_part(&assembly, &part_desc, &b_idx) == 0, "add part B");
    EXPECT(dom_assembly_connect(&assembly, a_idx, b_idx, DOM_PART_IFACE_MECHANICAL) == 0,
           "connect parts");
    EXPECT(dom_assembly_check_support(&assembly) == 0, "unsupported assembly fails");
    EXPECT(dom_assembly_set_grounded(&assembly, a_idx, 1) == 0, "ground part");
    EXPECT(dom_assembly_check_support(&assembly) != 0, "supported assembly passes");
    return 0;
}

static int test_extraction_conserves_mass(void)
{
    dom_field_storage storage;
    dom_field_layer layers[2];
    i32 ore_density[1];
    i32 pollution[1];
    dom_resource_process_desc extract_desc;
    dom_resource_process_desc refine_desc;
    dom_resource_process_result extract_result;
    dom_resource_process_result refine_result;
    dom_physical_process_context ctx;
    i32 remaining;
    i32 expected_refined;

    dom_domain_volume_ref domain;
    domain.id = 2u;
    domain.version = 1u;
    dom_field_storage_init(&storage, domain, 1u, 1u, 0u, layers, 2u);
    dom_field_layer_add(&storage, DOM_FIELD_ORE_DENSITY, DOM_FIELD_VALUE_Q16_16,
                        q16(100), DOM_FIELD_VALUE_UNKNOWN, ore_density);
    dom_field_layer_add(&storage, DOM_FIELD_POLLUTION, DOM_FIELD_VALUE_Q16_16,
                        q16(0), DOM_FIELD_VALUE_UNKNOWN, pollution);

    memset(&ctx, 0, sizeof(ctx));
    ctx.capability_mask = DOM_PHYS_CAP_EXTRACTION;
    ctx.authority_mask = DOM_PHYS_AUTH_EXTRACTION;

    dom_resource_process_desc_default(DOM_RESOURCE_EXTRACT_MATERIAL, &extract_desc);
    extract_desc.field_id = DOM_FIELD_ORE_DENSITY;
    extract_desc.amount_q16 = q16(30);
    EXPECT(dom_resource_apply_process(&storage, &extract_desc, 0u, 0u, &ctx, &extract_result) == 0,
           "extract apply");
    EXPECT(extract_result.extracted_q16 == extract_desc.amount_q16, "extracted amount");
    EXPECT(dom_field_get_value(&storage, DOM_FIELD_ORE_DENSITY, 0u, 0u, &remaining) == 0,
           "remaining");
    EXPECT(remaining == q16(70), "deposit reduced");

    dom_resource_process_desc_default(DOM_RESOURCE_REFINE_MATERIAL, &refine_desc);
    refine_desc.amount_q16 = extract_desc.amount_q16;
    refine_desc.yield_q16 = q16(1) - (q16(1) / 5);
    EXPECT(dom_resource_apply_process(&storage, &refine_desc, 0u, 0u, &ctx, &refine_result) == 0,
           "refine apply");
    expected_refined = (i32)(((i64)refine_desc.amount_q16 * (i64)refine_desc.yield_q16) >> 16);
    EXPECT(refine_result.refined_q16 == expected_refined, "refined amount");
    EXPECT(refine_result.refined_q16 + refine_result.waste_q16 == refine_desc.amount_q16,
           "mass conserved");
    return 0;
}

static int test_network_overload_failure(void)
{
    dom_network_node nodes[2];
    dom_network_edge edges[1];
    dom_network_graph graph;
    dom_network_edge* edge;
    i32 capacity;
    i32 overload;

    dom_network_graph_init(&graph, DOM_NETWORK_ELECTRICAL, nodes, 2u, edges, 1u);
    dom_network_add_node(&graph, 1u, q16(100));
    dom_network_add_node(&graph, 2u, q16(100));
    edge = dom_network_add_edge(&graph, 10u, 1u, 2u, q16(50), 0);
    EXPECT(edge != 0, "edge add");
    capacity = edge->capacity_q16;
    overload = capacity + q16(10);
    EXPECT(dom_network_route_flow(&graph, 1u, 2u, overload, 0, 10u) != 0,
           "overload fails");
    EXPECT(edge->status == DOM_NETWORK_FAILED, "edge failed");
    return 0;
}

static int test_machine_wear_accumulates(void)
{
    dom_machine_state machine;
    dom_machine_init(&machine, 1u, 60u);
    dom_machine_operate(&machine, 10u, 0, 1u);
    EXPECT(machine.wear_level == 10u, "wear increment");
    dom_machine_overload(&machine, 30u, 0, 2u);
    EXPECT(machine.wear_level == 40u, "wear overload");
    dom_machine_operate(&machine, 30u, 0, 3u);
    EXPECT(machine.status == DOM_MACHINE_FAILED, "machine failed");
    return 0;
}

static int test_infrastructure_affects_agents(void)
{
    dom_network_node nodes[1];
    dom_network_edge edges[1];
    dom_network_graph graph;
    dom_infra_binding binding;
    dom_agent_capability caps[1];
    agent_goal_registry goals;
    agent_goal goal_storage[1];
    agent_goal_desc desc;
    agent_context ctx;
    agent_plan plan;
    agent_refusal_code refusal = AGENT_REFUSAL_NONE;

    dom_network_graph_init(&graph, DOM_NETWORK_DATA, nodes, 1u, edges, 1u);
    dom_network_add_node(&graph, 100u, q16(10));

    binding.agent_id = 500u;
    binding.node_id = 100u;
    binding.capability_mask = AGENT_CAP_TRADE;

    memset(caps, 0, sizeof(caps));
    caps[0].agent_id = 500u;
    caps[0].capability_mask = 0u;

    dom_infra_apply_agent_caps(caps, 1u, &graph, &binding, 1u);
    EXPECT((caps[0].capability_mask & AGENT_CAP_TRADE) != 0u, "infra grants cap");

    agent_goal_registry_init(&goals, goal_storage, 1u, 1u);
    memset(&desc, 0, sizeof(desc));
    desc.agent_id = 500u;
    desc.type = AGENT_GOAL_TRADE;
    desc.preconditions.required_capabilities = AGENT_CAP_TRADE;
    EXPECT(agent_goal_register(&goals, &desc, 0) == 0, "goal register");
    memset(&ctx, 0, sizeof(ctx));
    ctx.agent_id = 500u;
    ctx.capability_mask = caps[0].capability_mask;
    ctx.authority_mask = AGENT_AUTH_TRADE;
    EXPECT(agent_planner_build(&goal_storage[0], &ctx, 0, 1u, &plan, &refusal) == 0,
           "planner succeeds with infra");

    nodes[0].status = DOM_NETWORK_FAILED;
    dom_infra_apply_agent_caps(caps, 1u, &graph, &binding, 1u);
    EXPECT((caps[0].capability_mask & AGENT_CAP_TRADE) == 0u, "infra removed cap");
    ctx.capability_mask = caps[0].capability_mask;
    EXPECT(agent_planner_build(&goal_storage[0], &ctx, 0, 2u, &plan, &refusal) != 0,
           "planner fails without infra");
    EXPECT(refusal == AGENT_REFUSAL_INSUFFICIENT_CAPABILITY, "refusal matches");
    return 0;
}

static int test_zero_asset_boot(void)
{
    dom_field_storage storage;
    dom_network_graph graph;
    dom_part_registry parts;

    dom_domain_volume_ref domain;
    domain.id = 0u;
    domain.version = 0u;
    dom_field_storage_init(&storage, domain, 0u, 0u, 0u, 0, 0u);
    EXPECT(storage.layer_count == 0u, "empty field storage");

    dom_network_graph_init(&graph, DOM_NETWORK_DATA, 0, 0u, 0, 0u);
    EXPECT(graph.node_count == 0u && graph.edge_count == 0u, "empty network");

    dom_part_registry_init(&parts, 0, 0u);
    EXPECT(parts.count == 0u, "empty parts");
    return 0;
}

int main(void)
{
    if (test_terrain_modification_determinism() != 0) return 1;
    if (test_structure_support() != 0) return 1;
    if (test_extraction_conserves_mass() != 0) return 1;
    if (test_network_overload_failure() != 0) return 1;
    if (test_machine_wear_accumulates() != 0) return 1;
    if (test_infrastructure_affects_agents() != 0) return 1;
    if (test_zero_asset_boot() != 0) return 1;
    return 0;
}
