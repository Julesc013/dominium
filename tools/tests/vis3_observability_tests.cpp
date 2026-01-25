/*
VIS-3 observability tests: immutable snapshots, access filtering, deterministic replay, and read-only tooling.
*/
#include "agent_inspector.h"
#include "determinism_tools.h"
#include "history_viewer.h"
#include "institution_inspector.h"
#include "observability_api.h"
#include "observation_store.h"
#include "pack_inspector.h"
#include "visualization_view.h"
#include "world_inspector.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct test_fixture {
    tool_snapshot_record snapshots[1];
    tool_observe_event_record events[2];
    tool_history_record history[1];
    tool_pack_record packs[1];
    tool_capability_record capabilities[2];
    tool_agent_state agents[1];
    tool_agent_goal_record goals[1];
    tool_agent_belief_record beliefs[1];
    tool_agent_memory_record memories[1];
    tool_agent_plan_step_record plans[1];
    tool_agent_failure_record failures[1];
    tool_institution_state institutions[1];
    tool_contract_record contracts[1];
    tool_delegation_record delegations[1];
    tool_constraint_record constraints[1];
    tool_enforcement_record enforcement[1];
    tool_institution_collapse_record collapses[1];
    tool_world_cell world_cells[4];
    tool_topology_node topology[1];
    tool_observe_replay_event replay_events[2];
    tool_observe_replay replay;
    tool_observation_store store;
} test_fixture;

static u64 hash_bytes(u64 hash, const unsigned char* bytes, unsigned int len)
{
    unsigned int i;
    for (i = 0u; i < len; ++i) {
        hash ^= (u64)bytes[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u64 hash_fixture(const test_fixture* fix)
{
    u64 hash = 1469598103934665603ULL;
    hash = hash_bytes(hash, (const unsigned char*)fix->snapshots, (unsigned int)sizeof(fix->snapshots));
    hash = hash_bytes(hash, (const unsigned char*)fix->events, (unsigned int)sizeof(fix->events));
    hash = hash_bytes(hash, (const unsigned char*)fix->world_cells, (unsigned int)sizeof(fix->world_cells));
    return hash;
}

static void init_fixture(test_fixture* fix)
{
    tool_observation_store_desc desc;
    memset(fix, 0, sizeof(*fix));

    fix->snapshots[0].snapshot_id = 1u;
    fix->snapshots[0].schema_id = 10u;
    fix->snapshots[0].schema_version = 1u;
    fix->snapshots[0].kind = DOM_SNAPSHOT_SUBJECTIVE;
    fix->snapshots[0].lod_tag = 1u;
    fix->snapshots[0].budget_units = 4u;
    fix->snapshots[0].scope_mask = 1u;
    fix->snapshots[0].knowledge_mask = 1u;

    fix->events[0].event_id = 101u;
    fix->events[0].act = 10;
    fix->events[0].agent_id = 1u;
    fix->events[0].institution_id = 2u;
    fix->events[0].process_id = 500u;
    fix->events[0].kind = 1u;
    fix->events[0].required_knowledge = 1u;
    fix->events[0].authority_mask = 1u;
    fix->events[0].amount = 5;
    fix->events[1].event_id = 102u;
    fix->events[1].act = 11;
    fix->events[1].agent_id = 1u;
    fix->events[1].process_id = 501u;
    fix->events[1].kind = 2u;
    fix->events[1].required_knowledge = 2u;
    fix->events[1].authority_mask = 1u;
    fix->events[1].amount = 7;

    fix->history[0].history_id = 201u;
    fix->history[0].act = 12;
    fix->history[0].agent_id = 1u;
    fix->history[0].institution_id = 2u;
    fix->history[0].provenance_id = 7u;
    fix->history[0].kind = 1u;
    fix->history[0].flags = TOOL_HISTORY_FLAG_CONFLICT;
    fix->history[0].required_knowledge = 1u;
    fix->history[0].amount = 3;

    fix->packs[0].pack_id = 10u;
    fix->packs[0].precedence = 1u;
    fix->packs[0].flags = TOOL_PACK_FLAG_ENABLED;

    fix->capabilities[0].capability_id = 1000u;
    fix->capabilities[0].pack_id = 10u;
    fix->capabilities[0].provider_kind = 1u;
    fix->capabilities[1].capability_id = 2000u;
    fix->capabilities[1].pack_id = 10u;
    fix->capabilities[1].provider_kind = 2u;

    fix->agents[0].agent_id = 1u;
    fix->agents[0].capability_mask = 1u;
    fix->agents[0].authority_mask = 1u;
    fix->agents[0].knowledge_mask = 2u;
    fix->agents[0].goal_count = 1u;

    fix->goals[0].goal_id = 300u;
    fix->goals[0].agent_id = 1u;
    fix->goals[0].priority_q16 = 100u;
    fix->goals[0].urgency_q16 = 200u;
    fix->goals[0].risk_q16 = 50u;
    fix->goals[0].horizon_act = 100;
    fix->goals[0].confidence_q16 = 60000u;
    fix->goals[0].status = TOOL_AGENT_GOAL_ACTIVE;
    fix->goals[0].required_knowledge = 1u;

    fix->beliefs[0].belief_id = 400u;
    fix->beliefs[0].agent_id = 1u;
    fix->beliefs[0].knowledge_id = 900u;
    fix->beliefs[0].observed_act = 9;
    fix->beliefs[0].confidence_q16 = 55000u;
    fix->beliefs[0].required_knowledge = 1u;

    fix->memories[0].memory_id = 500u;
    fix->memories[0].agent_id = 1u;
    fix->memories[0].kind = 1u;
    fix->memories[0].strength_q16 = 40000u;
    fix->memories[0].decay_q16 = 100u;
    fix->memories[0].last_act = 8;
    fix->memories[0].required_knowledge = 1u;

    fix->plans[0].plan_id = 600u;
    fix->plans[0].agent_id = 1u;
    fix->plans[0].process_id = 500u;
    fix->plans[0].step_index = 0u;
    fix->plans[0].status = TOOL_PLAN_STEP_PENDING;
    fix->plans[0].required_capability = 1u;
    fix->plans[0].expected_cost_q16 = 1000u;
    fix->plans[0].confidence_q16 = 45000u;
    fix->plans[0].required_knowledge = 1u;

    fix->failures[0].failure_id = 700u;
    fix->failures[0].agent_id = 1u;
    fix->failures[0].process_id = 500u;
    fix->failures[0].act = 13;
    fix->failures[0].failure_kind = 1u;
    fix->failures[0].required_knowledge = 1u;

    fix->institutions[0].institution_id = 2u;
    fix->institutions[0].authority_mask = 1u;
    fix->institutions[0].knowledge_mask = 4u;
    fix->institutions[0].legitimacy_q16 = 60000u;
    fix->institutions[0].status = 1u;
    fix->institutions[0].constraint_count = 1u;

    fix->contracts[0].contract_id = 800u;
    fix->contracts[0].institution_id = 2u;
    fix->contracts[0].agent_a = 1u;
    fix->contracts[0].agent_b = 3u;
    fix->contracts[0].act = 5;
    fix->contracts[0].status = TOOL_CONTRACT_ACTIVE;
    fix->contracts[0].required_knowledge = 1u;

    fix->delegations[0].delegation_id = 900u;
    fix->delegations[0].from_agent_id = 2u;
    fix->delegations[0].to_agent_id = 1u;
    fix->delegations[0].institution_id = 2u;
    fix->delegations[0].act = 6;
    fix->delegations[0].authority_mask = 1u;
    fix->delegations[0].status = TOOL_DELEGATION_ACTIVE;
    fix->delegations[0].required_knowledge = 1u;

    fix->constraints[0].constraint_id = 100u;
    fix->constraints[0].institution_id = 2u;
    fix->constraints[0].kind = 1u;
    fix->constraints[0].status = TOOL_CONSTRAINT_ACTIVE;
    fix->constraints[0].required_knowledge = 1u;

    fix->enforcement[0].enforcement_id = 110u;
    fix->enforcement[0].institution_id = 2u;
    fix->enforcement[0].agent_id = 1u;
    fix->enforcement[0].process_id = 500u;
    fix->enforcement[0].act = 7;
    fix->enforcement[0].kind = TOOL_ENFORCEMENT_DENY;
    fix->enforcement[0].status = 1u;
    fix->enforcement[0].required_knowledge = 1u;

    fix->collapses[0].collapse_id = 120u;
    fix->collapses[0].institution_id = 2u;
    fix->collapses[0].act = 20;
    fix->collapses[0].kind = TOOL_INSTITUTION_COLLAPSE_FRAGMENT;
    fix->collapses[0].required_knowledge = 1u;

    fix->world_cells[0].x = 0u;
    fix->world_cells[0].y = 0u;
    fix->world_cells[0].field_id = 1u;
    fix->world_cells[0].value_q16 = 65536;
    fix->world_cells[1].x = 1u;
    fix->world_cells[1].y = 0u;
    fix->world_cells[1].field_id = 1u;
    fix->world_cells[1].value_q16 = 0;
    fix->world_cells[1].flags = TOOL_WORLD_VALUE_UNKNOWN;
    fix->world_cells[2].x = 0u;
    fix->world_cells[2].y = 1u;
    fix->world_cells[2].field_id = 1u;
    fix->world_cells[2].value_q16 = 32768;
    fix->world_cells[2].flags = TOOL_WORLD_VALUE_LATENT;
    fix->world_cells[3].x = 1u;
    fix->world_cells[3].y = 1u;
    fix->world_cells[3].field_id = 1u;
    fix->world_cells[3].value_q16 = 98304;

    fix->topology[0].node_id = 1u;
    fix->topology[0].parent_id = 0u;

    fix->replay_events[0].event_id = 1001u;
    fix->replay_events[0].act = 1;
    fix->replay_events[0].kind = 1u;
    fix->replay_events[0].flags = 0u;
    fix->replay_events[0].agent_id = 1u;
    fix->replay_events[1].event_id = 1002u;
    fix->replay_events[1].act = 2;
    fix->replay_events[1].kind = 2u;
    fix->replay_events[1].flags = 0u;
    fix->replay_events[1].agent_id = 1u;

    fix->replay.events = fix->replay_events;
    fix->replay.event_count = 2u;

    memset(&desc, 0, sizeof(desc));
    desc.snapshots = fix->snapshots;
    desc.snapshot_count = 1u;
    desc.events = fix->events;
    desc.event_count = 2u;
    desc.history = fix->history;
    desc.history_count = 1u;
    desc.packs = fix->packs;
    desc.pack_count = 1u;
    desc.capabilities = fix->capabilities;
    desc.capability_count = 2u;
    desc.agents = fix->agents;
    desc.agent_count = 1u;
    desc.agent_goals = fix->goals;
    desc.agent_goal_count = 1u;
    desc.agent_beliefs = fix->beliefs;
    desc.agent_belief_count = 1u;
    desc.agent_memory = fix->memories;
    desc.agent_memory_count = 1u;
    desc.agent_plan_steps = fix->plans;
    desc.agent_plan_step_count = 1u;
    desc.agent_failures = fix->failures;
    desc.agent_failure_count = 1u;
    desc.institutions = fix->institutions;
    desc.institution_count = 1u;
    desc.contracts = fix->contracts;
    desc.contract_count = 1u;
    desc.delegations = fix->delegations;
    desc.delegation_count = 1u;
    desc.constraints = fix->constraints;
    desc.constraint_count = 1u;
    desc.enforcement = fix->enforcement;
    desc.enforcement_count = 1u;
    desc.collapses = fix->collapses;
    desc.collapse_count = 1u;
    desc.world_cells = fix->world_cells;
    desc.world_cell_count = 4u;
    desc.topology = fix->topology;
    desc.topology_count = 1u;
    desc.replay = &fix->replay;
    tool_observation_store_init(&fix->store, &desc);
}

static int test_snapshot_access(void)
{
    test_fixture fix;
    tool_snapshot_request req;
    tool_snapshot_view view;
    tool_access_context access;

    init_fixture(&fix);
    memset(&req, 0, sizeof(req));
    req.snapshot_id = 1u;
    req.kind = DOM_SNAPSHOT_SUBJECTIVE;
    req.kind_set = 1u;
    req.lod_tag = 1u;
    req.budget_units = 4u;
    req.scope_mask = 1u;

    access.mode = TOOL_ACCESS_EPISTEMIC;
    access.knowledge_mask = 0u;
    EXPECT(tool_snapshot_query(&fix.store, &req, &access, &view) == TOOL_OBSERVE_REFUSED,
           "snapshot access refused");

    access.knowledge_mask = 1u;
    EXPECT(tool_snapshot_query(&fix.store, &req, &access, &view) == TOOL_OBSERVE_OK,
           "snapshot access ok");

    req.kind = DOM_SNAPSHOT_OBJECTIVE;
    req.kind_set = 1u;
    access.knowledge_mask = 1u;
    EXPECT(tool_snapshot_query(&fix.store, &req, &access, &view) == TOOL_OBSERVE_REFUSED,
           "objective snapshot refused");
    return 0;
}

static int test_event_stream_filter(void)
{
    test_fixture fix;
    tool_event_stream stream;
    tool_event_stream_request req;
    tool_observe_event_record ev;
    tool_access_context access;

    init_fixture(&fix);
    req.agent_id = 1u;
    req.required_knowledge = 0u;
    access.mode = TOOL_ACCESS_EPISTEMIC;
    access.knowledge_mask = 1u;

    EXPECT(tool_event_stream_subscribe(&fix.store, &req, &access, &stream) == TOOL_OBSERVE_OK,
           "event stream subscribe");
    EXPECT(tool_event_stream_next(&stream, &ev) == TOOL_OBSERVE_OK,
           "event stream next");
    EXPECT(ev.event_id == 101u, "event stream filter mismatch");
    EXPECT(tool_event_stream_next(&stream, &ev) == TOOL_OBSERVE_NO_DATA,
           "event stream should stop");

    access.mode = TOOL_ACCESS_PRIVILEGED;
    access.knowledge_mask = 0u;
    EXPECT(tool_event_stream_subscribe(&fix.store, &req, &access, &stream) == TOOL_OBSERVE_OK,
           "event stream subscribe privileged");
    EXPECT(tool_event_stream_next(&stream, &ev) == TOOL_OBSERVE_OK,
           "event stream next privileged 1");
    EXPECT(tool_event_stream_next(&stream, &ev) == TOOL_OBSERVE_OK,
           "event stream next privileged 2");
    EXPECT(ev.event_id == 102u, "event stream privileged mismatch");
    return 0;
}

static int test_agent_institution_inspectors(void)
{
    test_fixture fix;
    tool_agent_inspector agent_insp;
    tool_institution_inspector inst_insp;
    tool_agent_state agent_state;
    tool_institution_state inst_state;
    tool_access_context access;

    init_fixture(&fix);
    access.mode = TOOL_ACCESS_EPISTEMIC;
    access.knowledge_mask = 0u;
    EXPECT(tool_agent_inspector_init(&agent_insp, &fix.store, &access, 1u) == TOOL_OBSERVE_OK,
           "agent inspector init");
    EXPECT(tool_agent_inspector_state(&agent_insp, &agent_state) == TOOL_OBSERVE_REFUSED,
           "agent inspector refusal");

    access.mode = TOOL_ACCESS_PRIVILEGED;
    access.knowledge_mask = 0u;
    EXPECT(tool_agent_inspector_init(&agent_insp, &fix.store, &access, 1u) == TOOL_OBSERVE_OK,
           "agent inspector init privileged");
    EXPECT(tool_agent_inspector_state(&agent_insp, &agent_state) == TOOL_OBSERVE_OK,
           "agent inspector state ok");

    access.mode = TOOL_ACCESS_EPISTEMIC;
    access.knowledge_mask = 0u;
    EXPECT(tool_institution_inspector_init(&inst_insp, &fix.store, &access, 2u) == TOOL_OBSERVE_OK,
           "institution inspector init");
    EXPECT(tool_institution_inspector_state(&inst_insp, &inst_state) == TOOL_OBSERVE_REFUSED,
           "institution inspector refusal");
    return 0;
}

static int test_world_and_visualization(void)
{
    test_fixture fix;
    tool_world_inspector insp;
    tool_world_query query;
    tool_world_view_cell cell;
    tool_visualization_request vis;
    tool_access_context access;
    char buffer[32];
    u32 written = 0u;

    init_fixture(&fix);
    access.mode = TOOL_ACCESS_EPISTEMIC;
    access.knowledge_mask = 0u;
    EXPECT(tool_world_inspector_init(&insp, &fix.store, &access) == TOOL_OBSERVE_OK,
           "world inspector init");

    memset(&query, 0, sizeof(query));
    query.field_id = 1u;
    query.include_unknown = 1u;
    query.include_latent = 1u;
    EXPECT(tool_world_inspector_seek(&insp, &query) == TOOL_OBSERVE_OK,
           "world inspector seek");
    EXPECT(tool_world_inspector_next(&insp, &cell) == TOOL_OBSERVE_OK,
           "world inspector next 1");
    EXPECT(tool_world_inspector_next(&insp, &cell) == TOOL_OBSERVE_OK,
           "world inspector next 2");
    EXPECT(cell.visible == 0u, "unknown/latent should be redacted");

    memset(&vis, 0, sizeof(vis));
    vis.field_id = 1u;
    vis.width = 2u;
    vis.height = 2u;
    vis.flags = TOOL_VIS_FLAG_INCLUDE_UNKNOWN | TOOL_VIS_FLAG_INCLUDE_LATENT;
    EXPECT(tool_visualization_render_ascii(&fix.store, &vis, &access, buffer,
                                           (u32)sizeof(buffer), &written) == TOOL_OBSERVE_OK,
           "visualization render");
    EXPECT(written >= 4u, "visualization output too small");
    return 0;
}

static int test_determinism(void)
{
    test_fixture fix;
    tool_determinism_diff diff;
    tool_observe_replay_event other_events[2];
    tool_observe_replay other_replay;

    init_fixture(&fix);
    EXPECT(tool_determinism_compare_replays(&fix.replay, &fix.replay, &diff) == TOOL_OBSERVE_OK,
           "determinism compare ok");
    EXPECT(diff.diverged == 0u, "determinism should not diverge");

    memcpy(other_events, fix.replay_events, sizeof(other_events));
    other_events[1].event_id = 999u;
    other_replay.events = other_events;
    other_replay.event_count = 2u;
    EXPECT(tool_determinism_compare_replays(&fix.replay, &other_replay, &diff) == TOOL_OBSERVE_OK,
           "determinism compare mismatch");
    EXPECT(diff.diverged == 1u, "determinism mismatch not detected");
    return 0;
}

static int test_pack_inspector(void)
{
    test_fixture fix;
    u64 required[2] = { 1000u, 9999u };
    u64 missing[2] = { 0u, 0u };
    u32 missing_count = 0u;

    init_fixture(&fix);
    EXPECT(tool_pack_inspector_missing_capabilities(&fix.store, required, 2u,
                                                    missing, 2u, &missing_count) == TOOL_OBSERVE_OK,
           "pack inspector missing");
    EXPECT(missing_count == 1u && missing[0] == 9999u,
           "pack inspector missing mismatch");
    return 0;
}

static int test_immutability(void)
{
    test_fixture fix;
    tool_snapshot_request req;
    tool_snapshot_view view;
    tool_access_context access;
    u64 hash_before;
    u64 hash_after;

    init_fixture(&fix);
    hash_before = hash_fixture(&fix);

    memset(&req, 0, sizeof(req));
    req.snapshot_id = 1u;
    req.kind = DOM_SNAPSHOT_SUBJECTIVE;
    req.kind_set = 1u;
    req.lod_tag = 1u;
    req.budget_units = 4u;
    req.scope_mask = 1u;
    access.mode = TOOL_ACCESS_PRIVILEGED;
    access.knowledge_mask = 0u;
    tool_snapshot_query(&fix.store, &req, &access, &view);

    hash_after = hash_fixture(&fix);
    EXPECT(hash_before == hash_after, "tooling mutated state");
    return 0;
}

int main(void)
{
    if (test_snapshot_access() != 0) return 1;
    if (test_event_stream_filter() != 0) return 1;
    if (test_agent_institution_inspectors() != 0) return 1;
    if (test_world_and_visualization() != 0) return 1;
    if (test_determinism() != 0) return 1;
    if (test_pack_inspector() != 0) return 1;
    if (test_immutability() != 0) return 1;
    return 0;
}
