#define main det_agents_inner_main
#include "../../source/tests/agent_behavior_determinism_test.c"
#undef main

int main(void) {
    return det_agents_inner_main();
}

