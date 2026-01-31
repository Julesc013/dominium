#include <stdio.h>

#include "domino/core/process_guard.h"

static int require_ok(int condition, const char *label)
{
    if (!condition) {
        printf("FAIL: %s\n", label);
        return 0;
    }
    return 1;
}

int main(void)
{
    int ok = 1;

    dom_process_guard_reset();
    dom_process_guard_note_mutation("test", 1);
    ok = require_ok(dom_process_guard_violation_count() == 1u, "violation when not in process") && ok;
    ok = require_ok(dom_process_guard_mutation_count() == 1u, "mutation count increments") && ok;

    dom_process_guard_enter("test.process");
    ok = require_ok(dom_process_guard_is_active() == 1, "guard active after enter") && ok;
    dom_process_guard_note_mutation("test", 2);
    ok = require_ok(dom_process_guard_violation_count() == 1u, "no new violation in process") && ok;
    dom_process_guard_exit();
    ok = require_ok(dom_process_guard_is_active() == 0, "guard inactive after exit") && ok;

    return ok ? 0 : 1;
}
