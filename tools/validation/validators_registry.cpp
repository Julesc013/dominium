/*
FILE: tools/validation/validators_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validation
RESPONSIBILITY: Registers and executes validation passes for GOV0.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Validation order is deterministic.
*/
#include "validators_registry.h"

namespace dom {
namespace validation {

static void collect_spec_files(const ValidationContext& ctx,
                               std::vector<std::string>& out_files) {
    std::vector<std::string> exts;
    std::vector<std::string> skip_dirs;
    exts.push_back(".md");
    skip_dirs.push_back(".git");
    skip_dirs.push_back("build");
    skip_dirs.push_back("dist");
    skip_dirs.push_back("out");
    skip_dirs.push_back("legacy");
    skip_dirs.push_back(".vs");
    skip_dirs.push_back(".vscode");
    list_files_recursive(ctx.repo_root + "/schema", exts, skip_dirs, out_files);
}

static void validate_schema_specs(const ValidationContext& ctx, ValidationReport& report) {
    std::vector<std::string> files;
    collect_spec_files(ctx, files);
    for (size_t i = 0u; i < files.size(); ++i) {
        const std::string& path = files[i];
        if (path.find("SPEC_") == std::string::npos) {
            continue;
        }
        std::string text;
        if (!read_file_text(path, text)) {
            report.add("GOV-VAL-001", VAL_SEV_ERROR, path, 0u,
                       "schema spec unreadable",
                       "Ensure schema spec files are present and readable.");
            continue;
        }
        std::string lower = to_lower(text);
        if (lower.find("status:") == std::string::npos ||
            lower.find("version:") == std::string::npos) {
            report.add("GOV-VAL-001", VAL_SEV_ERROR, path, 1u,
                       "schema spec missing Status/Version metadata",
                       "Add Status and Version fields to the schema spec.");
        }
    }
}

static void validate_determinism_schema_tokens(const ValidationContext& ctx, ValidationReport& report) {
    std::vector<std::string> exts;
    std::vector<std::string> skip_dirs;
    std::vector<std::string> files;
    exts.push_back(".c");
    exts.push_back(".cpp");
    exts.push_back(".h");
    skip_dirs.push_back(".git");
    skip_dirs.push_back("build");
    skip_dirs.push_back("dist");
    skip_dirs.push_back("out");
    skip_dirs.push_back("legacy");
    skip_dirs.push_back(".vs");
    skip_dirs.push_back(".vscode");
    list_files_recursive(ctx.repo_root + "/schema", exts, skip_dirs, files);
    for (size_t i = 0u; i < files.size(); ++i) {
        const std::string& path = files[i];
        std::string text;
        if (!read_file_text(path, text)) {
            continue;
        }
        if (text.find("DOM_SCHEMA_FIELD_F32") != std::string::npos ||
            text.find("DOM_SCHEMA_FIELD_F64") != std::string::npos) {
            report.add("GOV-VAL-001", VAL_SEV_ERROR, path, 1u,
                       "float field in schema descriptor",
                       "Use fixed-point or integer fields for authoritative schemas.");
        }
    }
}

void run_all_validators(const ValidationContext& ctx, ValidationReport& report) {
    validate_schema_specs(ctx, report);
    validate_determinism_schema_tokens(ctx, report);
}

} /* namespace validation */
} /* namespace dom */
