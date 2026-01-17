/*
Epistemic UI enforcement tests (EPIS0).
*/
#include "dominium/epistemic.h"

#include <stdio.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int ui_time_visible(const dom_capability_snapshot* snap, dom_act_time_t now_tick)
{
    dom_epistemic_view view = dom_epistemic_query(snap, DOM_CAP_TIME_READOUT, 0u, 0u, now_tick);
    return view.state == DOM_EPI_KNOWN;
}

static int ui_time_status(const dom_capability_snapshot* snap, dom_act_time_t now_tick)
{
    dom_epistemic_view view = dom_epistemic_query(snap, DOM_CAP_TIME_READOUT, 0u, 0u, now_tick);
    if (view.state == DOM_EPI_UNKNOWN) {
        return 0;
    }
    if (view.is_stale) {
        return 2;
    }
    if (view.is_uncertain) {
        return 3;
    }
    return 1;
}

static int snapshot_equal(const dom_capability_snapshot* a, const dom_capability_snapshot* b)
{
    u32 i;
    if (!a || !b) {
        return 0;
    }
    if (a->count != b->count) {
        return 0;
    }
    for (i = 0u; i < a->count; ++i) {
        const dom_capability_entry* ea = &a->entries[i];
        const dom_capability_entry* eb = &b->entries[i];
        if (ea->capability_id != eb->capability_id ||
            ea->subject_kind != eb->subject_kind ||
            ea->subject_id != eb->subject_id ||
            ea->state != eb->state ||
            ea->uncertainty_q16 != eb->uncertainty_q16 ||
            ea->latency_ticks != eb->latency_ticks ||
            ea->observed_tick != eb->observed_tick ||
            ea->expires_tick != eb->expires_tick ||
            ea->source_mask != eb->source_mask) {
            return 0;
        }
    }
    return 1;
}

static int test_capability_removal(void)
{
    dom_capability_entry storage[4];
    dom_capability_snapshot snap;
    dom_capability_entry entry;

    dom_capability_snapshot_init(&snap, storage, 4u);

    entry.capability_id = DOM_CAP_TIME_READOUT;
    entry.subject_kind = 0u;
    entry.subject_id = 0u;
    entry.state = DOM_EPI_KNOWN;
    entry.uncertainty_q16 = 0u;
    entry.latency_ticks = 0u;
    entry.observed_tick = 10;
    entry.expires_tick = DOM_EPISTEMIC_EXPIRES_NEVER;
    entry.source_mask = 1u;

    EXPECT(dom_capability_snapshot_add(&snap, &entry) == 0, "add capability failed");
    dom_capability_snapshot_finalize(&snap);
    EXPECT(ui_time_visible(&snap, 10) == 1, "time should be visible");

    dom_capability_snapshot_clear(&snap);
    dom_capability_snapshot_finalize(&snap);
    EXPECT(ui_time_visible(&snap, 11) == 0, "time should be hidden after removal");
    return 0;
}

static int test_latency_uncertainty(void)
{
    dom_capability_entry storage[4];
    dom_capability_snapshot snap;
    dom_capability_entry entry;
    int status;

    dom_capability_snapshot_init(&snap, storage, 4u);

    entry.capability_id = DOM_CAP_TIME_READOUT;
    entry.subject_kind = 0u;
    entry.subject_id = 0u;
    entry.state = DOM_EPI_KNOWN;
    entry.uncertainty_q16 = 4096u;
    entry.latency_ticks = 5u;
    entry.observed_tick = 10;
    entry.expires_tick = DOM_EPISTEMIC_EXPIRES_NEVER;
    entry.source_mask = 1u;

    EXPECT(dom_capability_snapshot_add(&snap, &entry) == 0, "add capability failed");
    dom_capability_snapshot_finalize(&snap);

    status = ui_time_status(&snap, 20);
    EXPECT(status == 2 || status == 3, "UI must reflect latency/uncertainty");
    return 0;
}

static int test_replay_equivalence(void)
{
    dom_capability_entry storage_a[4];
    dom_capability_entry storage_b[4];
    dom_capability_snapshot a;
    dom_capability_snapshot b;
    dom_capability_entry e1;
    dom_capability_entry e2;

    dom_capability_snapshot_init(&a, storage_a, 4u);
    dom_capability_snapshot_init(&b, storage_b, 4u);

    e1.capability_id = DOM_CAP_TIME_READOUT;
    e1.subject_kind = 0u;
    e1.subject_id = 0u;
    e1.state = DOM_EPI_KNOWN;
    e1.uncertainty_q16 = 0u;
    e1.latency_ticks = 0u;
    e1.observed_tick = 5;
    e1.expires_tick = DOM_EPISTEMIC_EXPIRES_NEVER;
    e1.source_mask = 1u;

    e2.capability_id = DOM_CAP_MAP_VIEW;
    e2.subject_kind = 1u;
    e2.subject_id = 42u;
    e2.state = DOM_EPI_KNOWN;
    e2.uncertainty_q16 = 256u;
    e2.latency_ticks = 2u;
    e2.observed_tick = 5;
    e2.expires_tick = DOM_EPISTEMIC_EXPIRES_NEVER;
    e2.source_mask = 1u;

    EXPECT(dom_capability_snapshot_add(&a, &e1) == 0, "add e1 failed");
    EXPECT(dom_capability_snapshot_add(&a, &e2) == 0, "add e2 failed");
    EXPECT(dom_capability_snapshot_add(&b, &e2) == 0, "add e2 failed");
    EXPECT(dom_capability_snapshot_add(&b, &e1) == 0, "add e1 failed");

    dom_capability_snapshot_finalize(&a);
    dom_capability_snapshot_finalize(&b);

    EXPECT(snapshot_equal(&a, &b), "snapshot ordering not deterministic");
    EXPECT(ui_time_visible(&a, 6) == ui_time_visible(&b, 6), "UI output differs on replay");
    return 0;
}

int main(void)
{
    if (test_capability_removal() != 0) {
        return 1;
    }
    if (test_latency_uncertainty() != 0) {
        return 1;
    }
    if (test_replay_equivalence() != 0) {
        return 1;
    }
    return 0;
}
