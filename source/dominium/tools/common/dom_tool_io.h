/*
FILE: source/dominium/tools/common/dom_tool_io.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_io
RESPONSIBILITY: Defines internal contract for `dom_tool_io`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TOOL_IO_H
#define DOM_TOOL_IO_H

#include <string>
#include <vector>

namespace dom {
namespace tools {

bool read_file(const std::string &path,
               std::vector<unsigned char> &out,
               std::string *err);

bool write_file(const std::string &path,
                const unsigned char *data,
                size_t len,
                std::string *err);

bool file_exists(const std::string &path);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_IO_H */

