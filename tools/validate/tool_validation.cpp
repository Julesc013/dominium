/*
FILE: tools/validate/tool_validation.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validate
RESPONSIBILITY: Tooling inventory validation hooks for GOV0.
ALLOWED DEPENDENCIES: tools/validation helpers and C++98 standard headers.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Reported via ValidationReport; no exceptions.
DETERMINISM: Deterministic traversal and reporting order.
*/
#include "tool_validation.h"

namespace dom {
namespace validation {

static void require_text_file(const ValidationContext& ctx,
                              ValidationReport& report,
                              const std::string& rel_path,
                              const std::string& rule_id,
                              const std::string& message) {
    std::string path = ctx.repo_root + "/" + rel_path;
    std::string text;
    if (!read_file_text(path, text)) {
        report.add(rule_id, VAL_SEV_ERROR, path, 0u, message,
                   "Restore required tooling files and keep them tracked.");
    }
}

void validate_tooling_inventory(const ValidationContext& ctx, ValidationReport& report) {
    require_text_file(ctx, report, "tools/inspect/inspect_access.h",
                      "TOOL0-VAL-001", "tooling access header missing");
    require_text_file(ctx, report, "tools/inspect/replay_inspector.h",
                      "TOOL0-VAL-001", "replay inspector header missing");
    require_text_file(ctx, report, "tools/inspect/replay_inspector.cpp",
                      "TOOL0-VAL-001", "replay inspector implementation missing");
    require_text_file(ctx, report, "tools/inspect/provenance_browser.h",
                      "TOOL0-VAL-001", "provenance browser header missing");
    require_text_file(ctx, report, "tools/inspect/provenance_browser.cpp",
                      "TOOL0-VAL-001", "provenance browser implementation missing");
    require_text_file(ctx, report, "tools/inspect/ledger_inspector.h",
                      "TOOL0-VAL-001", "ledger inspector header missing");
    require_text_file(ctx, report, "tools/inspect/ledger_inspector.cpp",
                      "TOOL0-VAL-001", "ledger inspector implementation missing");
    require_text_file(ctx, report, "tools/inspect/event_timeline_view.h",
                      "TOOL0-VAL-001", "event timeline header missing");
    require_text_file(ctx, report, "tools/inspect/event_timeline_view.cpp",
                      "TOOL0-VAL-001", "event timeline implementation missing");
    require_text_file(ctx, report, "tools/tests/tool0_inspection_tests.cpp",
                      "TOOL0-VAL-001", "tooling inspection tests missing");
    require_text_file(ctx, report, "docs/TOOLING_OVERVIEW.md",
                      "TOOL0-VAL-001", "tooling overview documentation missing");
}

} /* namespace validation */
} /* namespace dom */
