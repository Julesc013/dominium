/*
Macro due-event scheduler tests (event-driven stepping enforcement).
*/
#include "domino/sim/dg_due_sched.h"

#include <string.h>

#define TEST_ENTRY_CAP 10000u

typedef struct test_node {
    u64 key;
    dom_act_time_t next_due;
    int processed;
    dom_act_time_t last_target;
} test_node;

static dg_due_scheduler g_sched;
static dom_time_event g_events[TEST_ENTRY_CAP];
static dg_due_entry g_entries[TEST_ENTRY_CAP];
static test_node g_nodes[TEST_ENTRY_CAP];

static u64 g_order[8];
static u32 g_order_count = 0u;

static dom_act_time_t test_next_due(void* user, dom_act_time_t now_tick)
{
    test_node* node = (test_node*)user;
    (void)now_tick;
    if (!node) {
        return DG_DUE_TICK_NONE;
    }
    return node->next_due;
}

static int test_process_until(void* user, dom_act_time_t target_tick)
{
    test_node* node = (test_node*)user;
    if (!node) {
        return -1;
    }
    node->processed += 1;
    node->last_target = target_tick;
    node->next_due = DG_DUE_TICK_NONE;
    if (g_order_count < (u32)(sizeof(g_order) / sizeof(g_order[0]))) {
        g_order[g_order_count++] = node->key;
    }
    return 0;
}

static const dg_due_vtable g_vtable = {
    test_next_due,
    test_process_until
};

static int test_init_scheduler(dom_act_time_t start_tick)
{
    memset(g_events, 0, sizeof(g_events));
    memset(g_entries, 0, sizeof(g_entries));
    memset(g_nodes, 0, sizeof(g_nodes));
    g_order_count = 0u;
    return dg_due_scheduler_init(&g_sched, g_events, TEST_ENTRY_CAP, g_entries, TEST_ENTRY_CAP, start_tick);
}

static int test_latent_only_one_active(void)
{
    u32 i;
    u32 handle;
    int rc;
    int processed = 0;

    rc = test_init_scheduler(0);
    if (rc != DG_DUE_OK) {
        return 1;
    }
    for (i = 0u; i < TEST_ENTRY_CAP; ++i) {
        g_nodes[i].key = (u64)(i + 1u);
        g_nodes[i].next_due = DG_DUE_TICK_NONE;
        rc = dg_due_scheduler_register(&g_sched, &g_vtable, &g_nodes[i], g_nodes[i].key, &handle);
        if (rc != DG_DUE_OK) {
            return 1;
        }
    }
    g_nodes[42u].next_due = 5;
    (void)dg_due_scheduler_refresh(&g_sched, 42u);

    rc = dg_due_scheduler_advance(&g_sched, 5);
    if (rc != DG_DUE_OK) {
        return 1;
    }
    for (i = 0u; i < TEST_ENTRY_CAP; ++i) {
        processed += g_nodes[i].processed;
    }
    if (processed != 1) {
        return 1;
    }
    return 0;
}

static int test_no_global_iteration(void)
{
    u32 i;
    u32 handle;
    int rc;
    int processed = 0;

    rc = test_init_scheduler(10);
    if (rc != DG_DUE_OK) {
        return 1;
    }
    for (i = 0u; i < TEST_ENTRY_CAP; ++i) {
        g_nodes[i].key = (u64)(1000u + i);
        g_nodes[i].next_due = DG_DUE_TICK_NONE;
        rc = dg_due_scheduler_register(&g_sched, &g_vtable, &g_nodes[i], g_nodes[i].key, &handle);
        if (rc != DG_DUE_OK) {
            return 1;
        }
    }
    g_nodes[7u].next_due = 12;
    (void)dg_due_scheduler_refresh(&g_sched, 7u);
    rc = dg_due_scheduler_advance(&g_sched, 12);
    if (rc != DG_DUE_OK) {
        return 1;
    }
    for (i = 0u; i < TEST_ENTRY_CAP; ++i) {
        processed += g_nodes[i].processed;
    }
    if (processed != 1) {
        return 1;
    }
    return 0;
}

static int test_deterministic_ordering(void)
{
    u32 handle;
    int rc;
    int i;

    rc = test_init_scheduler(0);
    if (rc != DG_DUE_OK) {
        return 1;
    }
    g_nodes[0].key = 30u;
    g_nodes[0].next_due = 10;
    g_nodes[1].key = 10u;
    g_nodes[1].next_due = 10;
    g_nodes[2].key = 20u;
    g_nodes[2].next_due = 10;

    rc = dg_due_scheduler_register(&g_sched, &g_vtable, &g_nodes[0], g_nodes[0].key, &handle);
    if (rc != DG_DUE_OK) {
        return 1;
    }
    rc = dg_due_scheduler_register(&g_sched, &g_vtable, &g_nodes[2], g_nodes[2].key, &handle);
    if (rc != DG_DUE_OK) {
        return 1;
    }
    rc = dg_due_scheduler_register(&g_sched, &g_vtable, &g_nodes[1], g_nodes[1].key, &handle);
    if (rc != DG_DUE_OK) {
        return 1;
    }

    rc = dg_due_scheduler_advance(&g_sched, 10);
    if (rc != DG_DUE_OK) {
        return 1;
    }
    if (g_order_count != 3u) {
        return 1;
    }
    for (i = 0; i < 3; ++i) {
        if (g_order[i] != (u64)((i + 1) * 10)) {
            return 1;
        }
    }
    return 0;
}

int main(void)
{
    if (test_latent_only_one_active() != 0) {
        return 1;
    }
    if (test_no_global_iteration() != 0) {
        return 1;
    }
    if (test_deterministic_ordering() != 0) {
        return 1;
    }
    return 0;
}
