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
#include "validate/tool_validation.h"

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

static bool is_backend_name(const std::string& name) {
    return name == "null" || name == "software" || name == "vulkan" || name == "d3d12" ||
           name == "metal" || name == "d3d11" || name == "gl" || name == "d3d9" ||
           name == "d3d7" || name == "gl_fixed";
}

static bool is_backend_alias(const std::string& name) {
    return name == "d3d" || name == "dx" || name == "vk" || name == "sw" ||
           name == "soft" || name == "software" || name == "gl" || name == "vulkan" ||
           name == "metal" || name == "null";
}

static void validate_render_dirs(const ValidationContext& ctx, ValidationReport& report) {
    std::vector<std::string> skip_dirs;
    skip_dirs.push_back(".git");
    skip_dirs.push_back("build");
    skip_dirs.push_back("dist");
    skip_dirs.push_back("out");
    skip_dirs.push_back("legacy");
    skip_dirs.push_back(".vs");
    skip_dirs.push_back(".vscode");
    skip_dirs.push_back("external");
    skip_dirs.push_back("third_party");
    skip_dirs.push_back("deps");
    skip_dirs.push_back("sdk");

    std::string backends_root = ctx.repo_root + "/engine/render/backends";
    if (is_dir(backends_root)) {
        std::vector<DirEntry> entries;
        list_dir(backends_root, entries);
        for (size_t i = 0u; i < entries.size(); ++i) {
            if (!entries[i].is_dir) {
                continue;
            }
            std::string name = entries[i].name;
            if (name == "implicit" || name == "legacy") {
                report.add("GOV-VAL-REND-002", VAL_SEV_ERROR,
                           backends_root + "/" + name, 1u,
                           "capability-named backend folder",
                           "Use renderer identity folders under engine/render/backends.");
                continue;
            }
            const bool known_backend = is_backend_name(name);
            if (!known_backend) {
                report.add("GOV-VAL-REND-002", VAL_SEV_ERROR,
                           backends_root + "/" + name, 1u,
                           "unknown backend folder name",
                           "Use only canonical backend folder names.");
            }
            if (!known_backend && name.find("gl") == 0u && name.size() > 2u) {
                report.add("GOV-VAL-REND-002", VAL_SEV_ERROR,
                           backends_root + "/" + name, 1u,
                           "version bucket backend folder",
                           "Encode versions via RenderCaps, not folder names.");
            }
            if (!known_backend && name.find("metal") == 0u && name.size() > 5u) {
                report.add("GOV-VAL-REND-002", VAL_SEV_ERROR,
                           backends_root + "/" + name, 1u,
                           "version bucket backend folder",
                           "Encode versions via RenderCaps, not folder names.");
            }
        }
    }

    std::vector<DirEntry> entries;
    list_dir(ctx.repo_root, entries);
    for (size_t i = 0u; i < entries.size(); ++i) {
        if (!entries[i].is_dir) {
            continue;
        }
        if (is_backend_name(entries[i].name)) {
            report.add("GOV-VAL-REND-002", VAL_SEV_ERROR,
                       ctx.repo_root + "/" + entries[i].name, 1u,
                       "backend folder outside engine/render/backends",
                       "Move backend folders under engine/render/backends only.");
        }
    }

    std::string render_root = ctx.repo_root + "/engine/render";
    if (is_dir(render_root)) {
        std::vector<DirEntry> render_entries;
        list_dir(render_root, render_entries);
        for (size_t i = 0u; i < render_entries.size(); ++i) {
            if (!render_entries[i].is_dir) {
                continue;
            }
            const std::string& name = render_entries[i].name;
            if (name == "backends" || name == "core" || name == "graph" ||
                name == "features" || name == "shader" || name == "tests") {
                continue;
            }
            if (is_backend_name(name) || is_backend_alias(name)) {
                report.add("GOV-VAL-REND-002", VAL_SEV_ERROR,
                           render_root + "/" + name, 1u,
                           "backend folder outside engine/render/backends",
                           "Move backend folders under engine/render/backends only.");
            }
        }
    }
}

static bool line_has_backend_include(const std::string& line_lower) {
    if (line_lower.find("#include") == std::string::npos) {
        return false;
    }
    std::string line = line_lower;
    for (size_t i = 0u; i < line.size(); ++i) {
        if (line[i] == '\\') {
            line[i] = '/';
        }
    }
    if (line.find("vulkan/") != std::string::npos || line.find("vulkan.h") != std::string::npos) {
        return true;
    }
    if (line.find("d3d9") != std::string::npos || line.find("d3d11") != std::string::npos ||
        line.find("d3d12") != std::string::npos || line.find("dxgi") != std::string::npos) {
        return true;
    }
    if (line.find("opengl") != std::string::npos) {
        return true;
    }
    if (line.find("gl/") != std::string::npos || line.find("gl.h") != std::string::npos ||
        line.find("glad") != std::string::npos || line.find("glew") != std::string::npos) {
        return true;
    }
    if (line.find("metal/") != std::string::npos || line.find("metal.h") != std::string::npos ||
        line.find("<metal") != std::string::npos || line.find("\"metal") != std::string::npos) {
        return true;
    }
    if (line.find("mtl/") != std::string::npos || line.find("<mtl") != std::string::npos ||
        line.find("\"mtl") != std::string::npos) {
        return true;
    }
    return false;
}

static void validate_render_api_references(const ValidationContext& ctx, ValidationReport& report) {
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
    list_files_recursive(ctx.repo_root + "/game", exts, skip_dirs, files);
    for (size_t i = 0u; i < files.size(); ++i) {
        std::string text;
        if (!read_file_text(files[i], text)) {
            continue;
        }
        unsigned int line_no = 1u;
        size_t start = 0u;
        while (start <= text.size()) {
            size_t end = text.find('\n', start);
            if (end == std::string::npos) {
                end = text.size();
            }
            std::string line = text.substr(start, end - start);
            std::string lower = to_lower(line);
            if (line_has_backend_include(lower)) {
                report.add("GOV-VAL-REND-002", VAL_SEV_ERROR, files[i], line_no,
                           "backend API include in game code",
                           "Route renderer API usage through engine/render only.");
                break;
            }
            if (end == text.size()) {
                break;
            }
            start = end + 1u;
            line_no += 1u;
        }
    }
}

static void validate_epistemic_ui(const ValidationContext& ctx, ValidationReport& report) {
    std::vector<std::string> roots;
    roots.push_back(ctx.repo_root + "/game/ui");
    roots.push_back(ctx.repo_root + "/client");
    roots.push_back(ctx.repo_root + "/tools");
    std::vector<std::string> exts;
    std::vector<std::string> skip_dirs;
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
    for (size_t r = 0u; r < roots.size(); ++r) {
        if (!is_dir(roots[r])) {
            continue;
        }
        std::vector<std::string> files;
        list_files_recursive(roots[r], exts, skip_dirs, files);
        for (size_t i = 0u; i < files.size(); ++i) {
            std::string text;
            if (!read_file_text(files[i], text)) {
                continue;
            }
            std::string lower = to_lower(text);
            if (lower.find("#include") != std::string::npos) {
                if (lower.find("engine/modules/") != std::string::npos ||
                    lower.find("game/rules/") != std::string::npos ||
                    lower.find("game/economy/") != std::string::npos ||
                    lower.find("domino/sim/") != std::string::npos ||
                    lower.find("domino/world/") != std::string::npos ||
                    lower.find("domino/state/") != std::string::npos) {
                    report.add("GOV-VAL-EPIS-003", VAL_SEV_ERROR, files[i], 1u,
                               "authoritative include in UI/tool code",
                               "Use EIL/capability snapshot interfaces only.");
                }
            }
            if (lower.find("dom_sim_") != std::string::npos ||
                lower.find("dom_world_") != std::string::npos ||
                lower.find("dom_time_") != std::string::npos) {
                report.add("GOV-VAL-EPIS-003", VAL_SEV_ERROR, files[i], 1u,
                           "authoritative API call in UI/tool code",
                           "Route through Epistemic Interface Layer only.");
            }
        }
    }
}

void run_all_validators(const ValidationContext& ctx, ValidationReport& report) {
    validate_schema_specs(ctx, report);
    validate_determinism_schema_tokens(ctx, report);
    validate_perf_tokens(ctx, report);
    validate_render_features(ctx, report);
    validate_provenance_tokens(ctx, report);
    validate_render_dirs(ctx, report);
    validate_render_api_references(ctx, report);
    validate_epistemic_ui(ctx, report);
    validate_tooling_inventory(ctx, report);
}

} /* namespace validation */
} /* namespace dom */
