/*
FILE: source/dominium/setup/cli/setup_cli.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/cli/setup_cli
RESPONSIBILITY: Defines internal contract for `setup_cli`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SETUP_CLI_H
#define DOM_SETUP_CLI_H

#include "dom_setup/dom_setup_config.h"

bool is_stdin_interactive();
void print_usage();

#endif /* DOM_SETUP_CLI_H */
