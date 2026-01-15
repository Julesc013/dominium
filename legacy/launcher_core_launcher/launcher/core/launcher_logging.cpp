/*
FILE: source/dominium/launcher/core/launcher_logging.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/launcher_logging
RESPONSIBILITY: Implements `launcher_logging`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "launcher_logging.h"
#include "dom_shared/logging.h"

using namespace dom_shared;

void launcher_log_info(const std::string &msg) { log_info("[launcher] %s", msg.c_str()); }
void launcher_log_warn(const std::string &msg) { log_warn("[launcher] %s", msg.c_str()); }
void launcher_log_error(const std::string &msg) { log_error("[launcher] %s", msg.c_str()); }
