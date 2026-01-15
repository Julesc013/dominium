/*
FILE: source/tests/dom_no_modal_loading_test.cpp
MODULE: Dominium Tests
PURPOSE: Validate no-modal-loading guards (IO ban + derived job budgets).
*/
#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/core/types.h"
}

#include "runtime/dom_derived_jobs.h"
#include "runtime/dom_io_guard.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

int main() {
    dom_io_guard_reset();

    dom_io_guard_enter_ui();
    if (dom_io_guard_io_allowed()) {
        return fail("io_allowed_in_ui");
    }
    dom_io_guard_note_violation("test_io", "test_path");
    if (dom_io_guard_violation_count() != 1u) {
        return fail("violation_count_not_incremented");
    }
    dom_io_guard_exit_ui();

    dom_derived_queue_desc desc;
    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_DERIVED_QUEUE_DESC_VERSION;

    dom_derived_queue *queue = dom_derived_queue_create(&desc);
    if (!queue) {
        return fail("queue_create");
    }

    dom_derived_job_budget_hint hint;
    hint.work_ms = 50u;
    hint.io_bytes = 1024u;

    dom_derived_job_payload payload;
    payload.data = &hint;
    payload.size = sizeof(hint);

    dom_derived_job_id job = dom_derived_submit(queue, DERIVED_IO_READ_FILE, &payload, 0);
    if (job == 0u) {
        dom_derived_queue_destroy(queue);
        return fail("submit_io_job");
    }

    /* Budget too small: IO job must stay pending (deferred, not blocking). */
    if (dom_derived_pump(queue, 1u, 512u, 1u) != 0) {
        dom_derived_queue_destroy(queue);
        return fail("io_job_processed_with_small_budget");
    }

    dom_derived_job_status status;
    std::memset(&status, 0, sizeof(status));
    if (dom_derived_poll(queue, job, &status) != 0) {
        dom_derived_queue_destroy(queue);
        return fail("poll_status");
    }
    if (status.state != DOM_DERIVED_JOB_PENDING) {
        dom_derived_queue_destroy(queue);
        return fail("io_job_not_pending");
    }

    dom_derived_queue_destroy(queue);
    return 0;
}
