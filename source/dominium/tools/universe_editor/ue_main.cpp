/*
FILE: source/dominium/tools/universe_editor/ue_main.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/universe_editor
RESPONSIBILITY: Universe editor CLI entry point (tools-as-instances).
*/
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "dom_tool_runtime.h"
#include "ue_commands.h"
#include "ue_queries.h"

extern "C" {
#include "domino/core/types.h"
}

namespace {

static bool parse_u64(const char *s, u64 &out) {
    char *end = 0;
    unsigned long long v;
    if (!s || s[0] == '\0') {
        return false;
    }
    v = std::strtoull(s, &end, 0);
    if (!end || end[0] != '\0') {
        return false;
    }
    out = (u64)v;
    return true;
}

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

static bool parse_system_arg(const std::string &arg, std::string &out_id, u64 &out_parent) {
    const size_t sep = arg.find(',');
    out_id = (sep == std::string::npos) ? arg : arg.substr(0u, sep);
    out_parent = 0ull;
    if (sep != std::string::npos) {
        const std::string parent = arg.substr(sep + 1u);
        if (!parent.empty()) {
            return parse_u64(parent.c_str(), out_parent);
        }
    }
    return !out_id.empty();
}

static bool parse_route_arg(const std::string &arg, dom::tools::UeRouteEntry &out) {
    std::vector<std::string> parts;
    size_t start = 0u;
    size_t pos = 0u;
    u64 vals[5];
    size_t i;

    std::memset(&out, 0, sizeof(out));

    while (true) {
        pos = arg.find(',', start);
        if (pos == std::string::npos) {
            parts.push_back(arg.substr(start));
            break;
        }
        parts.push_back(arg.substr(start, pos - start));
        start = pos + 1u;
    }

    if (parts.size() != 5u) {
        return false;
    }
    for (i = 0u; i < 5u; ++i) {
        if (!parse_u64(parts[i].c_str(), vals[i])) {
            return false;
        }
    }
    out.id = vals[0];
    out.src_station_id = vals[1];
    out.dst_station_id = vals[2];
    out.duration_ticks = vals[3];
    out.capacity_units = vals[4];
    return true;
}

static void usage() {
    std::printf("Usage: tool_universe_editor --bundle-ref=<run|home>:<rel> [options]\n");
    std::printf("Options:\n");
    std::printf("  --handshake=<rel>          handshake path relative to RUN_ROOT (default handshake.tlv)\n");
    std::printf("  --summary                  emit summary (default)\n");
    std::printf("  --list-systems             emit systems.csv\n");
    std::printf("  --list-routes              emit routes.csv\n");
    std::printf("  --edit                     enable edit mode (required for mutations)\n");
    std::printf("  --out-ref=<run>:<rel>       output bundle path (required for edit)\n");
    std::printf("  --add-system=<id>[,parent]  add system by string id\n");
    std::printf("  --remove-system=<id>        remove system by numeric id\n");
    std::printf("  --route=<id,src,dst,dur,cap> upsert route\n");
    std::printf("  --remove-route=<id>         remove route by numeric id\n");
}

} // namespace

int main(int argc, char **argv) {
    std::string handshake_rel = "handshake.tlv";
    dom::DomGamePathRef bundle_ref;
    dom::DomGamePathRef out_ref;
    bool has_bundle_ref = false;
    bool has_out_ref = false;
    bool edit_mode = false;
    bool summary = true;
    bool list_systems = false;
    bool list_routes = false;
    std::vector<std::string> add_systems;
    std::vector<u64> remove_systems;
    std::vector<dom::tools::UeRouteEntry> upsert_routes;
    std::vector<u64> remove_routes;
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
        } else if (std::strncmp(a, "--out-ref=", 10) == 0) {
            dom::DomGamePathRef ref;
            if (!parse_path_ref(std::string(a + 10), ref, &err)) {
                std::fprintf(stderr, "out-ref error: %s\n", err.c_str());
                return 2;
            }
            out_ref = ref;
            has_out_ref = true;
        } else if (std::strcmp(a, "--edit") == 0) {
            edit_mode = true;
        } else if (std::strcmp(a, "--summary") == 0) {
            summary = true;
        } else if (std::strcmp(a, "--list-systems") == 0) {
            list_systems = true;
        } else if (std::strcmp(a, "--list-routes") == 0) {
            list_routes = true;
        } else if (std::strncmp(a, "--add-system=", 13) == 0) {
            add_systems.push_back(std::string(a + 13));
        } else if (std::strncmp(a, "--remove-system=", 16) == 0) {
            u64 id = 0ull;
            if (!parse_u64(a + 16, id)) {
                std::fprintf(stderr, "remove-system: invalid id\n");
                return 2;
            }
            remove_systems.push_back(id);
        } else if (std::strncmp(a, "--route=", 8) == 0) {
            dom::tools::UeRouteEntry route;
            if (!parse_route_arg(std::string(a + 8), route)) {
                std::fprintf(stderr, "route: invalid format\n");
                return 2;
            }
            upsert_routes.push_back(route);
        } else if (std::strncmp(a, "--remove-route=", 15) == 0) {
            u64 id = 0ull;
            if (!parse_u64(a + 15, id)) {
                std::fprintf(stderr, "remove-route: invalid id\n");
                return 2;
            }
            remove_routes.push_back(id);
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

    const bool has_edits = !add_systems.empty() || !remove_systems.empty() ||
                           !upsert_routes.empty() || !remove_routes.empty();
    if (has_edits && !edit_mode) {
        std::fprintf(stderr, "Edit operations require --edit\n");
        return 2;
    }
    if (edit_mode) {
        if (!has_out_ref) {
            std::fprintf(stderr, "--out-ref is required in edit mode\n");
            return 2;
        }
        if (out_ref.base_kind != dom::DOM_GAME_PATH_BASE_RUN_ROOT) {
            std::fprintf(stderr, "--out-ref must be run:<rel>\n");
            return 2;
        }
        if (out_ref.base_kind == bundle_ref.base_kind && out_ref.rel == bundle_ref.rel) {
            std::fprintf(stderr, "--out-ref must differ from --bundle-ref\n");
            return 2;
        }
    }

    dom::tools::DomToolRuntime rt;
    if (!dom::tools::tool_runtime_init(rt,
                                       "universe_editor",
                                       handshake_rel,
                                       dom::DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED,
                                       edit_mode,
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

    if (has_edits) {
        size_t idx;
        for (idx = 0u; idx < add_systems.size(); ++idx) {
            std::string sys_id;
            u64 parent_id = 0ull;
            if (!parse_system_arg(add_systems[idx], sys_id, parent_id)) {
                err = "add-system invalid format";
                dom::tools::tool_runtime_refuse(rt, dom::tools::DOM_TOOL_REFUSAL_IO, err);
                dom_universe_bundle_destroy(bundle);
                return 4;
            }
            if (!dom::tools::ue_add_system(bundle, sys_id, parent_id, &err)) {
                dom::tools::tool_runtime_refuse(rt, dom::tools::DOM_TOOL_REFUSAL_IO, err);
                dom_universe_bundle_destroy(bundle);
                return 4;
            }
        }
        for (idx = 0u; idx < remove_systems.size(); ++idx) {
            if (!dom::tools::ue_remove_system(bundle, remove_systems[idx], &err)) {
                dom::tools::tool_runtime_refuse(rt, dom::tools::DOM_TOOL_REFUSAL_IO, err);
                dom_universe_bundle_destroy(bundle);
                return 4;
            }
        }
        for (idx = 0u; idx < upsert_routes.size(); ++idx) {
            if (!dom::tools::ue_upsert_route(bundle, upsert_routes[idx], &err)) {
                dom::tools::tool_runtime_refuse(rt, dom::tools::DOM_TOOL_REFUSAL_IO, err);
                dom_universe_bundle_destroy(bundle);
                return 4;
            }
        }
        for (idx = 0u; idx < remove_routes.size(); ++idx) {
            if (!dom::tools::ue_remove_route(bundle, remove_routes[idx], &err)) {
                dom::tools::tool_runtime_refuse(rt, dom::tools::DOM_TOOL_REFUSAL_IO, err);
                dom_universe_bundle_destroy(bundle);
                return 4;
            }
        }
    }

    if (summary) {
        dom::tools::UeSummary summary_out;
        std::string json;
        if (dom::tools::ue_build_summary(bundle, summary_out, &err)) {
            json = dom::tools::ue_summary_json(summary_out);
            dom::tools::tool_runtime_emit_output(rt, "summary.json",
                                                 json.empty() ? 0 : (const unsigned char *)json.c_str(),
                                                 json.size(),
                                                 0);
            std::printf("%s\n", json.c_str());
        } else {
            std::fprintf(stderr, "summary failed: %s\n", err.c_str());
        }
    }

    if (list_systems) {
        std::string csv;
        if (dom::tools::ue_list_systems(bundle, csv, &err)) {
            dom::tools::tool_runtime_emit_output(rt, "systems.csv",
                                                 csv.empty() ? 0 : (const unsigned char *)csv.c_str(),
                                                 csv.size(),
                                                 0);
            std::printf("%s", csv.c_str());
        } else {
            std::fprintf(stderr, "list systems failed: %s\n", err.c_str());
        }
    }

    if (list_routes) {
        std::string csv;
        if (dom::tools::ue_list_routes(bundle, csv, &err)) {
            dom::tools::tool_runtime_emit_output(rt, "routes.csv",
                                                 csv.empty() ? 0 : (const unsigned char *)csv.c_str(),
                                                 csv.size(),
                                                 0);
            std::printf("%s", csv.c_str());
        } else {
            std::fprintf(stderr, "list routes failed: %s\n", err.c_str());
        }
    }

    if (edit_mode) {
        std::string out_abs;
        if (!dom::dom_game_paths_resolve_rel(rt.paths, out_ref.base_kind, out_ref.rel, out_abs)) {
            err = "output path refused";
            dom::tools::tool_runtime_refuse(rt, rt.last_refusal, err);
            dom_universe_bundle_destroy(bundle);
            return 5;
        }
        rc = dom_universe_bundle_write_file(out_abs.c_str(), bundle);
        if (rc != DOM_UNIVERSE_BUNDLE_OK) {
            err = "bundle write failed";
            dom::tools::tool_runtime_refuse(rt, dom::tools::DOM_TOOL_REFUSAL_IO, err);
            dom_universe_bundle_destroy(bundle);
            return 5;
        }
        std::printf("Wrote bundle: %s\n", out_ref.rel.c_str());
    }

    dom_universe_bundle_destroy(bundle);
    return 0;
}
