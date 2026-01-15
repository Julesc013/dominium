/*
FILE: source/dominium/tools/validator/validator_main.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/validator
RESPONSIBILITY: Universe bundle validator CLI entry point.
*/
#include <cstdio>
#include <cstring>
#include <string>

#include "dom_tool_runtime.h"
#include "validator_checks.h"

namespace {

static bool parse_path_ref(const std::string &arg, dom::DomGamePathRef &out, std::string *err) {
    const size_t sep = arg.find(':');
    if (sep == std::string::npos) {
        if (err) *err = "path_ref_missing_base";
        return false;
    }
    const std::string base = arg.substr(0u, sep);
    const std::string rel = arg.substr(sep + 1u);
    if (rel.empty()) {
        if (err) *err = "path_ref_empty_rel";
        return false;
    }
    if (base == "run") {
        out.base_kind = dom::DOM_GAME_PATH_BASE_RUN_ROOT;
    } else if (base == "home") {
        out.base_kind = dom::DOM_GAME_PATH_BASE_HOME_ROOT;
    } else {
        if (err) *err = "path_ref_base_invalid";
        return false;
    }
    out.rel = rel;
    out.has_value = true;
    return true;
}

static void usage() {
    std::printf("Usage: tool_validator --bundle-ref=<run|home>:<rel> [--handshake=<rel>]\n");
}

} // namespace

int main(int argc, char **argv) {
    std::string handshake_rel = "handshake.tlv";
    dom::DomGamePathRef bundle_ref;
    bool has_bundle_ref = false;
    std::string err;
    int i;

    for (i = 1; i < argc; ++i) {
        const char *a = argv[i] ? argv[i] : "";
        if (std::strncmp(a, "--handshake=", 12) == 0) {
            handshake_rel = std::string(a + 12);
        } else if (std::strncmp(a, "--bundle-ref=", 13) == 0) {
            dom::DomGamePathRef ref;
            if (!parse_path_ref(std::string(a + 13), ref, &err)) {
                std::fprintf(stderr, "bundle-ref error: %s\n", err.c_str());
                return 2;
            }
            bundle_ref = ref;
            has_bundle_ref = true;
        } else if (std::strcmp(a, "--help") == 0 || std::strcmp(a, "-h") == 0) {
            usage();
            return 0;
        } else {
            std::fprintf(stderr, "Unknown arg: %s\n", a);
            usage();
            return 2;
        }
    }

    if (!has_bundle_ref) {
        usage();
        return 2;
    }

    dom::tools::DomToolRuntime rt;
    if (!dom::tools::tool_runtime_init(rt,
                                       "validator",
                                       handshake_rel,
                                       dom::DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED,
                                       false,
                                       &err)) {
        dom::tools::tool_runtime_refuse(rt, rt.last_refusal, err);
        std::fprintf(stderr, "tool init failed: %s\n", err.c_str());
        return 3;
    }
    if (!dom::tools::tool_runtime_validate_identity(rt, &err)) {
        dom::tools::tool_runtime_refuse(rt, rt.last_refusal, err);
        std::fprintf(stderr, "identity failed: %s\n", err.c_str());
        return 3;
    }

    dom_universe_bundle *bundle = 0;
    dom_universe_bundle_identity id;
    int rc = dom::tools::tool_runtime_load_universe(rt, bundle_ref, &bundle, &id, &err);
    if (rc != DOM_UNIVERSE_BUNDLE_OK || !bundle) {
        dom::tools::tool_runtime_refuse(rt, rt.last_refusal ? rt.last_refusal : dom::tools::DOM_TOOL_REFUSAL_IO, err);
        std::fprintf(stderr, "bundle load failed: %s\n", err.c_str());
        return 4;
    }

    dom::tools::DomToolDiagnostics diag;
    const bool ok = dom::tools::validator_check_bundle(bundle, diag, &id);
    const std::string report = dom::tools::validator_report_json(diag, &id, ok);
    dom::tools::tool_runtime_emit_output(rt, "validator_report.json",
                                         report.empty() ? 0 : (const unsigned char *)report.c_str(),
                                         report.size(),
                                         0);
    std::printf("%s\n", report.c_str());

    dom_universe_bundle_destroy(bundle);
    return ok ? 0 : 2;
}
