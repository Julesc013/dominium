/*
FILE: include/dominium/_internal/dom_priv/launcher_internal/launcher_logging.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/launcher_internal/launcher_logging
RESPONSIBILITY: Defines the public contract for `launcher_logging` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_LOGGING_H
#define DOM_LAUNCHER_LOGGING_H

#include <string>

void launcher_log_info(const std::string &msg);
void launcher_log_warn(const std::string &msg);
void launcher_log_error(const std::string &msg);

#endif /* DOM_LAUNCHER_LOGGING_H */
