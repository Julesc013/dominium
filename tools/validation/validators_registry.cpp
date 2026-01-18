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

static void validate_perf_tokens(const ValidationContext& ctx, ValidationReport& report) {
    std::vector<std::string> exts;
    std::vector<std::string> skip_dirs;
    std::vector<std::string> files;
    exts.push_back(".md");
    exts.push_back(".txt");
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
        if (text.find("UNBOUNDED_LIST") != std::string::npos) {
            report.add("GOV-VAL-PERF-005", VAL_SEV_ERROR, path, 1u,
                       "unbounded list marker in schema",
                       "Use bounded list sizes and explicit max_count.");
        }
    }
}

static void validate_render_features(const ValidationContext& ctx, ValidationReport& report) {
    std::vector<std::string> exts;
    std::vector<std::string> skip_dirs;
    std::vector<std::string> files;
    exts.push_back(".md");
    exts.push_back(".txt");
    exts.push_back(".toml");
    exts.push_back(".json");
    exts.push_back(".yaml");
    exts.push_back(".yml");
    exts.push_back(".ini");
    skip_dirs.push_back(".git");
    skip_dirs.push_back("build");
    skip_dirs.push_back("dist");
    skip_dirs.push_back("out");
    skip_dirs.push_back("legacy");
    skip_dirs.push_back(".vs");
    skip_dirs.push_back(".vscode");

    std::string features_root = ctx.repo_root + "/engine/render/features";
    if (!is_dir(features_root)) {
        return;
    }
    list_files_recursive(features_root, exts, skip_dirs, files);
    for (size_t i = 0u; i < files.size(); ++i) {
        const std::string& path = files[i];
        std::string text;
        if (!read_file_text(path, text)) {
            continue;
        }
        std::string lower = to_lower(text);
        if (lower.find("requires") == std::string::npos ||
            lower.find("fallback") == std::string::npos ||
            lower.find("cost") == std::string::npos) {
            report.add("GOV-VAL-PERF-005", VAL_SEV_ERROR, path, 1u,
                       "render feature missing requires/fallback/cost",
                       "Define requires, fallback, and cost for each render feature.");
        }
    }
}

static void validate_provenance_tokens(const ValidationContext& ctx, ValidationReport& report) {
    std::vector<std::string> exts;
    std::vector<std::string> skip_dirs;
    std::vector<std::string> files;
    exts.push_back(".md");
    exts.push_back(".txt");
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
        if (text.find("FABRICATED_POPULATION") != std::string::npos ||
            text.find("SPAWN_POPULATION") != std::string::npos) {
            report.add("GOV-VAL-PROV-004", VAL_SEV_ERROR, path, 1u,
                       "fabricated population marker in schema",
                       "Remove fabrication flags; require provenance-backed construction.");
        }
        if (text.find("LOOT_WITHOUT_PROVENANCE") != std::string::npos) {
            report.add("GOV-VAL-PROV-004", VAL_SEV_ERROR, path, 1u,
                       "loot without provenance marker in schema",
                       "Require physical inventory provenance for salvage/loot.");
        }
    }
}

void run_all_validators(const ValidationContext& ctx, ValidationReport& report) {
    validate_schema_specs(ctx, report);
    validate_determinism_schema_tokens(ctx, report);
    validate_perf_tokens(ctx, report);
    validate_render_features(ctx, report);
    validate_provenance_tokens(ctx, report);
}

} /* namespace validation */
} /* namespace dom */
