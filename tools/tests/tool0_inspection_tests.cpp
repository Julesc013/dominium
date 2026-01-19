/*
TOOL0 inspection tests: replay equivalence, provenance trace, ledger conservation, and mutation refusal.
*/
#include "inspect_access.h"
#include "replay_inspector.h"
#include "provenance_browser.h"
#include "ledger_inspector.h"
#include "event_timeline_view.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int test_replay_equivalence(void) {
    tool_replay_event events[3];
    tool_replay replay;
    tool_replay_inspector inspector;
    tool_replay_view_event view;
    tool_access_context access;
    u64 hash_before;
    u64 hash_after;
    int res;
    u32 count = 0u;

    memset(events, 0, sizeof(events));
    events[0].event_id = 10u;
    events[0].act = 5;
    events[0].kind = TOOL_REPLAY_EVENT_COMMAND;
    events[0].required_knowledge = 1u;
    events[1].event_id = 20u;
    events[1].act = 10;
    events[1].kind = TOOL_REPLAY_EVENT_OUTCOME;
    events[1].required_knowledge = 1u;
    events[2].event_id = 30u;
    events[2].act = 15;
    events[2].kind = TOOL_REPLAY_EVENT_SCHEDULE;
    events[2].required_knowledge = 1u;

    replay.events = events;
    replay.event_count = 3u;
    hash_before = tool_replay_hash(&replay);

    access.mode = TOOL_ACCESS_PRIVILEGED;
    access.knowledge_mask = 0u;
    EXPECT(tool_replay_inspector_init(&inspector, &replay, &access) == TOOL_INSPECT_OK,
           "replay init");
    EXPECT(tool_replay_inspector_seek(&inspector, 0) == TOOL_INSPECT_OK,
           "replay seek");

    while ((res = tool_replay_inspector_next(&inspector, &view)) == TOOL_INSPECT_OK) {
        EXPECT(view.visible == 1u, "replay view visible");
        count += 1u;
    }
    EXPECT(res == TOOL_INSPECT_NO_DATA, "replay next should finish");
    EXPECT(count == 3u, "replay event count mismatch");

    hash_after = tool_replay_hash(&replay);
    EXPECT(hash_before == hash_after, "replay hash changed after inspection");
    return 0;
}

static int test_provenance_trace(void) {
    tool_provenance_link links[3];
    tool_provenance_graph graph;
    tool_access_context access;
    u64 path[4];
    u32 path_len = 0u;
    tool_provenance_refusal refusal = TOOL_PROVENANCE_OK;

    memset(links, 0, sizeof(links));
    links[0].child_id = 3u;
    links[0].parent_id = 2u;
    links[0].event_id = 50u;
    links[0].required_knowledge = 1u;
    links[1].child_id = 3u;
    links[1].parent_id = 4u;
    links[1].event_id = 60u;
    links[1].required_knowledge = 1u;
    links[2].child_id = 2u;
    links[2].parent_id = 1u;
    links[2].event_id = 70u;
    links[2].required_knowledge = 1u;

    graph.links = links;
    graph.link_count = 3u;
    access.mode = TOOL_ACCESS_EPISTEMIC;
    access.knowledge_mask = 1u;

    EXPECT(tool_provenance_trace(&graph, 3u, &access, path, 4u, &path_len, &refusal) == TOOL_INSPECT_OK,
           "provenance trace");
    EXPECT(refusal == TOOL_PROVENANCE_OK, "provenance refusal");
    EXPECT(path_len == 3u, "provenance path length");
    EXPECT(path[0] == 3u && path[1] == 2u && path[2] == 1u, "provenance path mismatch");
    return 0;
}

static int test_ledger_conservation(void) {
    tool_ledger_entry entries[3];
    tool_ledger_inspector insp;
    tool_access_context access;
    tool_ledger_balance_summary summary;
    d_bool balanced = D_FALSE;
    int result = TOOL_INSPECT_OK;

    memset(entries, 0, sizeof(entries));
    entries[0].entry_id = 1u;
    entries[0].asset_id = 10u;
    entries[0].delta = 5;
    entries[0].act = 1;
    entries[0].required_knowledge = 1u;
    entries[1].entry_id = 2u;
    entries[1].asset_id = 10u;
    entries[1].delta = -2;
    entries[1].act = 2;
    entries[1].required_knowledge = 1u;
    entries[2].entry_id = 3u;
    entries[2].asset_id = 10u;
    entries[2].delta = -3;
    entries[2].act = 3;
    entries[2].required_knowledge = 1u;

    insp.entries = entries;
    insp.entry_count = 3u;
    access.mode = TOOL_ACCESS_PRIVILEGED;
    access.knowledge_mask = 0u;

    EXPECT(tool_ledger_balance(&insp, 10u, &access, &summary, &result) == TOOL_INSPECT_OK,
           "ledger balance");
    EXPECT(result == TOOL_INSPECT_OK, "ledger result");
    EXPECT(summary.net == 0, "ledger net");

    EXPECT(tool_ledger_is_balanced(&insp, 10u, &access, &balanced, &result) == TOOL_INSPECT_OK,
           "ledger balanced");
    EXPECT(balanced == D_TRUE, "ledger not balanced");

    access.mode = TOOL_ACCESS_EPISTEMIC;
    access.knowledge_mask = 0u;
    EXPECT(tool_ledger_is_balanced(&insp, 10u, &access, &balanced, &result) == TOOL_INSPECT_REFUSED,
           "ledger epistemic refusal");
    EXPECT(result == TOOL_INSPECT_REFUSED, "ledger refusal code");
    return 0;
}

static int test_mutation_refused(void) {
    tool_access_context access;
    access.mode = TOOL_ACCESS_PRIVILEGED;
    access.knowledge_mask = 0u;
    EXPECT(tool_inspect_request_mutation(&access) == TOOL_INSPECT_REFUSED,
           "mutation should be refused");
    return 0;
}

static int test_timeline_next_due(void) {
    tool_event_record events[3];
    tool_event_timeline timeline;
    tool_access_context access;
    dom_act_time_t next_act = 0;

    memset(events, 0, sizeof(events));
    events[0].event_id = 11u;
    events[0].act = 5;
    events[0].state = TOOL_EVENT_PENDING;
    events[0].required_knowledge = 1u;
    events[1].event_id = 12u;
    events[1].act = 9;
    events[1].state = TOOL_EVENT_PENDING;
    events[1].required_knowledge = 1u;
    events[2].event_id = 13u;
    events[2].act = 3;
    events[2].state = TOOL_EVENT_FIRED;
    events[2].required_knowledge = 1u;

    timeline.events = events;
    timeline.event_count = 3u;
    access.mode = TOOL_ACCESS_EPISTEMIC;
    access.knowledge_mask = 1u;

    EXPECT(tool_event_timeline_next_due(&timeline, &access, 4, &next_act) == TOOL_INSPECT_OK,
           "timeline next due");
    EXPECT(next_act == 5, "timeline next act mismatch");
    return 0;
}

int main(void) {
    if (test_replay_equivalence() != 0) return 1;
    if (test_provenance_trace() != 0) return 1;
    if (test_ledger_conservation() != 0) return 1;
    if (test_mutation_refused() != 0) return 1;
    if (test_timeline_next_due() != 0) return 1;
    return 0;
}
