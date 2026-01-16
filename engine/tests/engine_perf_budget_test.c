/*
Performance regression fixtures for PERF3 (telemetry + budget outputs).
*/
#include "domino/system/dsys_perf.h"
#include "domino/system/dsys_guard.h"
#include "domino/sim/dg_due_sched.h"
#include "sim/lod/dg_interest.h"

#include <string.h>
#include <stdlib.h>

#define LATENT_ENTRY_COUNT 10000u

typedef struct perf_due_entry {
    dom_act_time_t next_due;
    dom_act_time_t step;
} perf_due_entry;

static u64 g_test_clock_us = 0u;

static u64 perf_test_clock(void* user)
{
    (void)user;
    g_test_clock_us += 100u;
    return g_test_clock_us;
}

static dom_act_time_t perf_due_next(void* user, dom_act_time_t now_tick)
{
    perf_due_entry* entry = (perf_due_entry*)user;
    if (!entry) {
        return DG_DUE_TICK_NONE;
    }
    if (entry->next_due == DG_DUE_TICK_NONE) {
        return DG_DUE_TICK_NONE;
    }
    if (entry->next_due < now_tick) {
        return now_tick;
    }
    return entry->next_due;
}

static int perf_due_process(void* user, dom_act_time_t target_tick)
{
    perf_due_entry* entry = (perf_due_entry*)user;
    if (!entry) {
        return -1;
    }
    if (entry->step <= 0) {
        entry->next_due = DG_DUE_TICK_NONE;
        return 0;
    }
    entry->next_due = target_tick + entry->step;
    return 0;
}

static const dg_due_vtable g_perf_due_vtable = {
    perf_due_next,
    perf_due_process
};

static void perf_interest_source(dg_tick tick, dg_interest_list* out_list, void* user_ctx)
{
    dg_interest_volume vol;
    (void)tick;
    (void)user_ctx;
    memset(&vol, 0, sizeof(vol));
    vol.type = DG_IV_PLAYER;
    vol.shape = DG_IV_SHAPE_SPHERE;
    vol.domain_id = 1u;
    vol.src_entity = 1u;
    vol.center.x = (q16_16)(1 << Q16_16_FRAC_BITS);
    vol.center.y = (q16_16)(1 << Q16_16_FRAC_BITS);
    vol.center.z = (q16_16)(1 << Q16_16_FRAC_BITS);
    vol.radius = (q16_16)(1 << Q16_16_FRAC_BITS);
    (void)dg_interest_list_push(out_list, &vol);
}

static void perf_job_fn(void* user)
{
    int* flag = (int*)user;
    if (flag) {
        *flag = 1;
    }
}

static int perf_init_interest(dg_interest_ctx* ctx, dg_interest_list* list)
{
    if (!ctx || !list) {
        return -1;
    }
    dg_interest_init(ctx);
    dg_interest_list_init(list);
    if (dg_interest_reserve(ctx, 4u) != 0) {
        return -1;
    }
    if (dg_interest_list_reserve(list, 8u) != 0) {
        return -1;
    }
    if (dg_interest_register_source(ctx, perf_interest_source, 1u, NULL) != 0) {
        return -1;
    }
    return 0;
}

static void perf_free_interest(dg_interest_ctx* ctx, dg_interest_list* list)
{
    if (list) {
        dg_interest_list_free(list);
    }
    if (ctx) {
        dg_interest_free(ctx);
    }
}

static int perf_run_fixture_earth(const char* tier)
{
    dom_time_event events[8];
    dg_due_entry entries[8];
    dg_due_scheduler sched;
    perf_due_entry earth_entry;
    dg_interest_ctx interest_ctx;
    dg_interest_list interest_list;
    dsys_perf_timer sim_timer;
    dsys_perf_flush_desc flush_desc;
    u32 tick;

    if (dg_due_scheduler_init(&sched, events, 8u, entries, 8u, 0) != DG_DUE_OK) {
        return 1;
    }

    memset(&earth_entry, 0, sizeof(earth_entry));
    earth_entry.next_due = 1;
    earth_entry.step = 1;
    if (dg_due_scheduler_register(&sched, &g_perf_due_vtable, &earth_entry, 1u, NULL) != DG_DUE_OK) {
        return 1;
    }

    if (perf_init_interest(&interest_ctx, &interest_list) != 0) {
        return 1;
    }

    for (tick = 1u; tick <= 5u; ++tick) {
        int job_flag = 0;
        dsys_derived_job_desc job_desc;

        dsys_perf_tick_begin((dom_act_time_t)tick, (u64)tick);
        dsys_perf_timer_begin(&sim_timer, DSYS_PERF_LANE_MACRO, DSYS_PERF_METRIC_SIM_TICK_US);

        if (dg_due_scheduler_advance(&sched, (dom_act_time_t)tick) != DG_DUE_OK) {
            perf_free_interest(&interest_ctx, &interest_list);
            return 1;
        }

        if (dg_interest_collect(&interest_ctx, tick, &interest_list) != 0) {
            perf_free_interest(&interest_ctx, &interest_list);
            return 1;
        }

        job_desc.fn = perf_job_fn;
        job_desc.user = &job_flag;
        job_desc.tag = "perf_job";
        if (dsys_derived_job_submit(&job_desc) != 0) {
            perf_free_interest(&interest_ctx, &interest_list);
            return 1;
        }
        (void)dsys_derived_job_run_next();

        dsys_perf_metric_set(DSYS_PERF_LANE_LOCAL, DSYS_PERF_METRIC_RENDER_SUBMIT_US, 500u);
        dsys_perf_metric_set(DSYS_PERF_LANE_LOCAL, DSYS_PERF_METRIC_STREAM_BYTES, 65536u);
        dsys_perf_metric_add(DSYS_PERF_LANE_MACRO, DSYS_PERF_METRIC_NET_MSG_SENT, 2u);
        dsys_perf_metric_add(DSYS_PERF_LANE_MACRO, DSYS_PERF_METRIC_NET_MSG_RECV, 2u);
        dsys_perf_metric_add(DSYS_PERF_LANE_MACRO, DSYS_PERF_METRIC_NET_BYTES_SENT, 512u);
        dsys_perf_metric_add(DSYS_PERF_LANE_MACRO, DSYS_PERF_METRIC_NET_BYTES_RECV, 512u);

        dsys_perf_timer_end(&sim_timer);
        dsys_perf_tick_end();
    }

    memset(&flush_desc, 0, sizeof(flush_desc));
    flush_desc.fixture = "earth_only";
    flush_desc.tier = tier;
    flush_desc.emit_telemetry = 1u;
    flush_desc.emit_budget_report = 1u;
    if (dsys_perf_flush(&flush_desc) != 0) {
        perf_free_interest(&interest_ctx, &interest_list);
        return 1;
    }

    perf_free_interest(&interest_ctx, &interest_list);
    return 0;
}

static dom_time_event g_latent_events[LATENT_ENTRY_COUNT];
static dg_due_entry g_latent_entries[LATENT_ENTRY_COUNT];
static perf_due_entry g_latent_due[LATENT_ENTRY_COUNT];

static int perf_run_fixture_latent(const char* tier)
{
    dg_due_scheduler sched;
    dsys_perf_timer sim_timer;
    dsys_perf_flush_desc flush_desc;
    u32 i;
    u32 tick = 1u;

    if (dg_due_scheduler_init(&sched, g_latent_events, LATENT_ENTRY_COUNT, g_latent_entries, LATENT_ENTRY_COUNT, 0) != DG_DUE_OK) {
        return 1;
    }

    for (i = 0u; i < LATENT_ENTRY_COUNT; ++i) {
        perf_due_entry* entry = &g_latent_due[i];
        memset(entry, 0, sizeof(*entry));
        entry->next_due = DG_DUE_TICK_NONE;
        entry->step = 0;
        if (i == 0u) {
            entry->next_due = 1;
            entry->step = 0;
        }
        if (dg_due_scheduler_register(&sched, &g_perf_due_vtable, entry, (u64)(i + 1u), NULL) != DG_DUE_OK) {
            return 1;
        }
    }

    dsys_perf_tick_begin((dom_act_time_t)tick, (u64)tick);
    dsys_perf_timer_begin(&sim_timer, DSYS_PERF_LANE_MACRO, DSYS_PERF_METRIC_SIM_TICK_US);
    if (dg_due_scheduler_advance(&sched, (dom_act_time_t)tick) != DG_DUE_OK) {
        return 1;
    }
    dsys_perf_metric_set(DSYS_PERF_LANE_LOCAL, DSYS_PERF_METRIC_RENDER_SUBMIT_US, 250u);
    dsys_perf_metric_set(DSYS_PERF_LANE_LOCAL, DSYS_PERF_METRIC_STREAM_BYTES, 32768u);
    dsys_perf_timer_end(&sim_timer);
    dsys_perf_tick_end();

    memset(&flush_desc, 0, sizeof(flush_desc));
    flush_desc.fixture = "latent_10k";
    flush_desc.tier = tier;
    flush_desc.emit_telemetry = 1u;
    flush_desc.emit_budget_report = 1u;
    if (dsys_perf_flush(&flush_desc) != 0) {
        return 1;
    }

    return 0;
}

int main(void)
{
    const char* tier = getenv("DOMINIUM_PERF_TIER");
    if (!tier || !tier[0]) {
        tier = "baseline";
    }

    dsys_perf_set_enabled(1);
    dsys_perf_set_clock(perf_test_clock, NULL);
    dsys_perf_set_manual_clock(0u);

    dsys_perf_reset();
    g_test_clock_us = 0u;
    if (perf_run_fixture_earth(tier) != 0) {
        return 1;
    }

    dsys_perf_reset();
    g_test_clock_us = 0u;
    if (perf_run_fixture_latent(tier) != 0) {
        return 1;
    }

    return 0;
}
