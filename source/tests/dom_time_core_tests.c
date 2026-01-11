/*
FILE: source/tests/dom_time_core_tests.c
MODULE: Repository
RESPONSIBILITY: Engine time core tests (ACT, events, frames).
*/
#include <stdio.h>

#include "domino/core/dom_time_core.h"
#include "domino/core/dom_time_events.h"
#include "domino/core/dom_time_frames.h"

static int g_failures = 0;

static void check(int cond, const char *msg) {
    if (!cond) {
        printf("FAIL: %s\n", msg);
        g_failures += 1;
    }
}

static int on_event_count(void *user, const dom_time_event *ev) {
    u32 *count = (u32 *)user;
    (void)ev;
    *count += 1u;
    return DOM_TIME_OK;
}

int main(void) {
    dom_time_core core;
    dom_act_time_t act;
    int rc;

    rc = dom_time_core_init(&core, 0);
    check(rc == DOM_TIME_OK, "init core");

    rc = dom_time_advance(&core, 10);
    check(rc == DOM_TIME_OK, "advance +10");
    rc = dom_time_get_act(&core, &act);
    check(rc == DOM_TIME_OK && act == 10, "act == 10");

    rc = dom_time_advance(&core, -1);
    check(rc == DOM_TIME_BACKWARDS, "advance negative refuses");
    rc = dom_time_get_act(&core, &act);
    check(rc == DOM_TIME_OK && act == 10, "act unchanged after negative");

    rc = dom_time_advance_to(&core, 5);
    check(rc == DOM_TIME_BACKWARDS, "advance_to backwards refuses");

    /* Batch vs step equivalence. */
    {
        dom_time_core a;
        dom_time_core b;
        u32 i;
        dom_time_core_init(&a, 0);
        dom_time_core_init(&b, 0);
        for (i = 0u; i < 100u; ++i) {
            dom_time_advance(&a, 1);
        }
        dom_time_advance(&b, 100);
        dom_time_get_act(&a, &act);
        check(act == 100, "step advance 100");
        dom_time_get_act(&b, &act);
        check(act == 100, "batch advance 100");
    }

    /* Large delta stepping. */
    {
        dom_time_core big;
        dom_time_core_init(&big, 0);
        rc = dom_time_advance(&big, 1000000000);
        check(rc == DOM_TIME_OK, "large delta ok");
        dom_time_get_act(&big, &act);
        check(act == 1000000000, "large delta matches");
    }

    /* Frame conversion determinism. */
    {
        dom_act_time_t bst = 0;
        dom_act_time_t gct = 0;
        dom_act_time_t cpt = 0;
        rc = dom_time_act_to_bst(12345, &bst);
        check(rc == DOM_TIME_OK && bst == 12345, "ACT->BST stub");
        rc = dom_time_act_to_gct(12345, &gct);
        check(rc == DOM_TIME_OK && gct == 12345, "ACT->GCT stub");
        rc = dom_time_act_to_cpt(12345, &cpt);
        check(rc == DOM_TIME_OK && cpt == 12345, "ACT->CPT stub");
        rc = dom_time_frame_convert(DOM_TIME_FRAME_BST, 12345, &bst);
        check(rc == DOM_TIME_OK && bst == 12345, "frame convert BST");
    }

    /* Event ordering determinism. */
    {
        dom_time_event_queue q;
        dom_time_event storage[4];
        dom_time_event ev;
        dom_time_event e1 = {1u, 10, 2u, 0u};
        dom_time_event e2 = {2u, 10, 1u, 0u};
        dom_time_event e3 = {3u, 5,  1u, 0u};
        dom_time_event e4 = {4u, 10, 1u, 0u};

        dom_time_event_queue_init(&q, storage, 4u);
        dom_time_event_schedule(&q, &e1);
        dom_time_event_schedule(&q, &e2);
        dom_time_event_schedule(&q, &e3);
        dom_time_event_schedule(&q, &e4);

        dom_time_event_pop(&q, &ev);
        check(ev.event_id == 3u, "event order #1");
        dom_time_event_pop(&q, &ev);
        check(ev.event_id == 2u, "event order #2");
        dom_time_event_pop(&q, &ev);
        check(ev.event_id == 4u, "event order #3");
        dom_time_event_pop(&q, &ev);
        check(ev.event_id == 1u, "event order #4");
    }

    /* Event cancellation correctness. */
    {
        dom_time_event_queue q;
        dom_time_event storage[4];
        dom_time_event ev;
        dom_time_event e1 = {1u, 10, 2u, 0u};
        dom_time_event e2 = {2u, 8,  1u, 0u};
        dom_time_event e3 = {3u, 12, 1u, 0u};

        dom_time_event_queue_init(&q, storage, 4u);
        dom_time_event_schedule(&q, &e1);
        dom_time_event_schedule(&q, &e2);
        dom_time_event_schedule(&q, &e3);

        rc = dom_time_event_cancel(&q, 2u);
        check(rc == DOM_TIME_OK, "cancel event");
        dom_time_event_pop(&q, &ev);
        check(ev.event_id == 1u, "cancel leaves correct #1");
        dom_time_event_pop(&q, &ev);
        check(ev.event_id == 3u, "cancel leaves correct #2");
    }

    /* Batch processing helper. */
    {
        dom_time_event_queue q;
        dom_time_event storage[4];
        dom_time_event e1 = {1u, 5,  1u, 0u};
        dom_time_event e2 = {2u, 7,  1u, 0u};
        dom_time_event e3 = {3u, 12, 1u, 0u};
        u32 count = 0u;
        dom_act_time_t next_time = 0;

        dom_time_event_queue_init(&q, storage, 4u);
        dom_time_event_schedule(&q, &e1);
        dom_time_event_schedule(&q, &e2);
        dom_time_event_schedule(&q, &e3);

        rc = dom_time_process_until(&q, 7, on_event_count, &count);
        check(rc == DOM_TIME_OK && count == 2u, "process_until count");
        rc = dom_time_event_next_time(&q, &next_time);
        check(rc == DOM_TIME_OK && next_time == 12, "next event time after batch");
    }

    if (g_failures == 0) {
        printf("dom_time_core_tests: PASS\n");
        return 0;
    }
    printf("dom_time_core_tests: FAIL (%d)\n", g_failures);
    return 1;
}
