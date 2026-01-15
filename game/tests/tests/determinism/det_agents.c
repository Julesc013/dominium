/*
FILE: tests/determinism/det_agents.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/determinism
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#define main det_agents_inner_main
#include "../../source/tests/agent_behavior_determinism_test.c"
#undef main

int main(void) {
    return det_agents_inner_main();
}

