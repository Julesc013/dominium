#define main det_sched_inner_main
#include "../../source/tests/sched_determinism_test.c"
#undef main

int main(void) {
    return det_sched_inner_main();
}

