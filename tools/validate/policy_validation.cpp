/*
FILE: tools/validate/policy_validation.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validate
RESPONSIBILITY: Policy documentation validation for FINAL0 governance.
ALLOWED DEPENDENCIES: tools/validation helpers and C++98 standard headers.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Reported via ValidationReport; no exceptions.
DETERMINISM: Deterministic checks for required policy docs.
*/
#include "policy_validation.h"

namespace dom {
namespace validation {

static void require_doc(const ValidationContext& ctx,
                        ValidationReport& report,
                        const std::string& rel_path,
                        const std::string& rule_id,
                        const std::string& message,
                        const char* required_token) {
    std::string path = ctx.repo_root + "/" + rel_path;
    std::string text;
    if (!read_file_text(path, text)) {
        report.add(rule_id, VAL_SEV_ERROR, path, 0u, message,
                   "Restore the required policy document.");
        return;
    }
    std::string lower = to_lower(text);
    if (required_token && lower.find(required_token) == std::string::npos) {
        report.add(rule_id, VAL_SEV_ERROR, path, 1u,
                   "policy doc missing required section",
                   "Add the required section to satisfy FINAL0 policy checks.");
    }
    if (lower.find("status:") == std::string::npos ||
        lower.find("version:") == std::string::npos) {
        report.add(rule_id, VAL_SEV_ERROR, path, 1u,
                   "policy doc missing Status/Version metadata",
                   "Add Status and Version fields to policy docs.");
    }
}

static void require_governance_ref(const ValidationContext& ctx,
                                   ValidationReport& report,
                                   const std::string& token) {
    std::string path = ctx.repo_root + "/schema/SCHEMA_GOVERNANCE.md";
    std::string text;
    if (!read_file_text(path, text)) {
        report.add("FINAL-DOC-001", VAL_SEV_ERROR, path, 0u,
                   "schema governance missing",
                   "Restore schema governance policy file.");
        return;
    }
    if (to_lower(text).find(to_lower(token)) == std::string::npos) {
        report.add("FINAL-DOC-001", VAL_SEV_ERROR, path, 1u,
                   "schema governance missing FINAL0 references",
                   "Add FINAL0 policy references to schema governance.");
    }
}

void validate_policy_docs(const ValidationContext& ctx, ValidationReport& report) {
    require_doc(ctx, report, "docs/LONG_TERM_SUPPORT_POLICY.md",
                "FINAL-API-001", "long-term support policy missing",
                "abi notes");
    require_doc(ctx, report, "docs/DEPRECATION_POLICY.md",
                "FINAL-DOC-001", "deprecation policy missing",
                "deprecation");
    require_doc(ctx, report, "docs/COMPATIBILITY_PROMISES.md",
                "FINAL-COMPAT-001", "compatibility promises missing",
                "schema major");
    require_doc(ctx, report, "docs/FEATURE_EPOCH_POLICY.md",
                "FINAL-EPOCH-001", "feature epoch policy missing",
                "epoch bump");
    require_doc(ctx, report, "docs/RENDER_BACKEND_LIFECYCLE.md",
                "FINAL-RENDER-001", "render backend lifecycle missing",
                "deprecation");

    require_governance_ref(ctx, report, "LONG_TERM_SUPPORT_POLICY");
    require_governance_ref(ctx, report, "DEPRECATION_POLICY");
    require_governance_ref(ctx, report, "COMPATIBILITY_PROMISES");
    require_governance_ref(ctx, report, "FEATURE_EPOCH_POLICY");
    require_governance_ref(ctx, report, "RENDER_BACKEND_LIFECYCLE");
}

} /* namespace validation */
} /* namespace dom */
