/*
FILE: source/dominium/launcher/core/include/launcher_selection_summary.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / selection_summary
RESPONSIBILITY: Deterministic "selection summary" snapshot (derived from selected-and-why) with TLV persistence and stable text rendering.
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core model schemas only.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Canonical TLV encoding; stable text rendering with predictable ordering; skip-unknown on read.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_SELECTION_SUMMARY_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_SELECTION_SUMMARY_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {
namespace launcher_core {

/* TLV schema version for selection_summary.tlv root. */
enum { LAUNCHER_SELECTION_SUMMARY_TLV_VERSION = 1u };

struct LauncherSelectionBackendChoice {
    std::string backend_id;
    std::string why; /* stable short "override" / "priority" / etc */

    LauncherSelectionBackendChoice();
};

struct LauncherSelectionProviderChoice {
    std::string provider_type; /* net/trust/keychain/content/os_integration */
    std::string provider_id;
    std::string why;

    LauncherSelectionProviderChoice();
};

struct LauncherSelectionSummary {
    u32 schema_version;

    u64 run_id;
    std::string instance_id;

    std::string launcher_profile_id;
    std::string determinism_profile_id;

    u32 offline_mode; /* 0/1 */
    u32 safe_mode;    /* 0/1 */

    /* Instance manifest identity */
    u64 manifest_hash64; /* 0 when absent */
    std::vector<unsigned char> manifest_hash_bytes; /* SHA-256 recommended; may be empty */

    /* Selected subsystem backends (ids + why). */
    LauncherSelectionBackendChoice ui_backend;
    std::vector<LauncherSelectionBackendChoice> platform_backends;
    std::vector<LauncherSelectionBackendChoice> renderer_backends;
    std::vector<LauncherSelectionProviderChoice> provider_backends;

    /* Resolved packs (deterministic order). */
    u32 resolved_packs_count;
    std::string resolved_packs_summary; /* comma-separated pack ids */

    /* Optional: merged effective caps + explain output (raw TLV bytes). */
    std::vector<unsigned char> effective_caps_tlv;
    std::vector<unsigned char> explanation_tlv;

    LauncherSelectionSummary();
};

bool launcher_selection_summary_to_tlv_bytes(const LauncherSelectionSummary& s,
                                             std::vector<unsigned char>& out_bytes);
bool launcher_selection_summary_from_tlv_bytes(const unsigned char* data,
                                               size_t size,
                                               LauncherSelectionSummary& out_s);

/* Stable line-oriented dump (predictable ordering). */
std::string launcher_selection_summary_to_text(const LauncherSelectionSummary& s);

/* Stable single-line summary for UI status bars / terse CLI output. */
std::string launcher_selection_summary_to_compact_line(const LauncherSelectionSummary& s);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_SELECTION_SUMMARY_H */

