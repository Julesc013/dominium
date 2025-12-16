/*
FILE: include/dominium/_internal/dom_priv/dom_shared/manifest_install.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_shared/manifest_install
RESPONSIBILITY: Defines the public contract for `manifest_install` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SHARED_MANIFEST_INSTALL_H
#define DOM_SHARED_MANIFEST_INSTALL_H

#include <string>

namespace dom_shared {

struct InstallInfo {
    std::string install_id;     // uuid
    std::string install_type;   // "portable"|"per-user"|"system"
    std::string platform;       // "win_nt"|"linux"|"mac"
    std::string version;        // e.g. "0.1.0"
    std::string root_path;      // absolute path to INSTALL_ROOT
    std::string created_at;     // ISO8601 string
    std::string created_by;     // "setup"|"portable-zip"|"package"|"unknown"
};

bool manifest_install_exists(const std::string& root_path);

// Attempts to parse INSTALL_ROOT/dominium_install.json
// On failure, returns false and leaves out_info unchanged.
bool parse_install_manifest(const std::string& root_path, InstallInfo& out_info);

// Writes INSTALL_ROOT/dominium_install.json with info fields.
// Returns false on IO/serialization error.
bool write_install_manifest(const InstallInfo& info);

} // namespace dom_shared

#endif
