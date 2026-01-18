/*
FILE: tools/validation/validate_all_main.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validation
RESPONSIBILITY: Unified validation runner for GOV0.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Validator output is deterministic for a given repo state.
*/
#include <cstdio>
#include <cstring>

#include "validator_common.h"
#include "validator_reports.h"
#include "validators_registry.h"

static void usage() {
    std::printf("Usage: validate_all --repo-root=<path> [--strict=1] [--json-out=<path>] [--text-out=<path>]\n");
}

static bool write_file(const std::string& path, const std::string& text) {
    FILE* f = std::fopen(path.c_str(), "wb");
    if (!f) {
        return false;
    }
    if (!text.empty()) {
        std::fwrite(text.c_str(), 1u, text.size(), f);
    }
    std::fclose(f);
    return true;
}

int main(int argc, char** argv) {
    std::string repo_root;
    std::string json_out;
    std::string text_out;
    bool strict = true;
    int i;

    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i] ? argv[i] : "";
        if (std::strncmp(arg, "--repo-root=", 12) == 0) {
            repo_root = std::string(arg + 12);
        } else if (std::strncmp(arg, "--json-out=", 11) == 0) {
            json_out = std::string(arg + 11);
        } else if (std::strncmp(arg, "--text-out=", 11) == 0) {
            text_out = std::string(arg + 11);
        } else if (std::strncmp(arg, "--strict=", 9) == 0) {
            strict = (arg[9] != '0');
        } else if (std::strcmp(arg, "--help") == 0 || std::strcmp(arg, "-h") == 0) {
            usage();
            return 0;
        } else {
            std::fprintf(stderr, "Unknown arg: %s\n", arg);
            usage();
            return 2;
        }
    }

    if (repo_root.empty()) {
        usage();
        return 2;
    }

    dom::validation::ValidationContext ctx;
    ctx.repo_root = repo_root;
    ctx.strict = strict;

    dom::validation::ValidationReport report;
    dom::validation::run_all_validators(ctx, report);

    std::string json = dom::validation::report_to_json(report);
    std::string text = dom::validation::report_to_text(report);
    std::printf("%s\n", text.c_str());
    std::printf("%s\n", json.c_str());

    if (!json_out.empty()) {
        if (!write_file(json_out, json)) {
            std::fprintf(stderr, "Failed to write json report: %s\n", json_out.c_str());
            return 2;
        }
    }
    if (!text_out.empty()) {
        if (!write_file(text_out, text)) {
            std::fprintf(stderr, "Failed to write text report: %s\n", text_out.c_str());
            return 2;
        }
    }

    if (report.has_errors()) {
        return 1;
    }
    if (report.warning_count > 0u && strict) {
        return 3;
    }
    return 0;
}
