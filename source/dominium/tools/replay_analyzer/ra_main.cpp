/*
FILE: source/dominium/tools/replay_analyzer/ra_main.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/replay_analyzer
RESPONSIBILITY: Replay analyzer CLI entry point.
*/
#include <cstdio>
#include <cstring>
#include <string>

#include "dom_tool_runtime.h"
#include "ra_parser.h"
#include "ra_diff.h"

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

static std::string u64_hex(u64 v) {
    static const char *hex = "0123456789abcdef";
    char buf[17];
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4u);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        buf[i] = hex[nib & 0xFu];
    }
    buf[16] = '\0';
    return std::string(buf);
}

static void usage() {
    std::printf("Usage: tool_replay_analyzer --replay-ref=<run|home>:<rel> [options]\n");
    std::printf("Options:\n");
    std::printf("  --handshake=<rel>         handshake path relative to RUN_ROOT (default handshake.tlv)\n");
    std::printf("  --desync-ref=<run|home>:<rel>  optional desync bundle\n");
    std::printf("  --dump-timeline[=<name>]  emit timeline.csv (default name timeline.csv)\n");
}

} // namespace

int main(int argc, char **argv) {
    std::string handshake_rel = "handshake.tlv";
    dom::DomGamePathRef replay_ref;
    dom::DomGamePathRef desync_ref;
    bool has_replay_ref = false;
    bool has_desync_ref = false;
    bool dump_timeline = false;
    std::string timeline_name = "timeline.csv";
    std::string err;
    int i;

    for (i = 1; i < argc; ++i) {
        const char *a = argv[i] ? argv[i] : "";
        if (std::strncmp(a, "--handshake=", 12) == 0) {
            handshake_rel = std::string(a + 12);
        } else if (std::strncmp(a, "--replay-ref=", 13) == 0) {
            dom::DomGamePathRef ref;
            if (!parse_path_ref(std::string(a + 13), ref, &err)) {
                std::fprintf(stderr, "replay-ref error: %s\n", err.c_str());
                return 2;
            }
            replay_ref = ref;
            has_replay_ref = true;
        } else if (std::strncmp(a, "--desync-ref=", 13) == 0) {
            dom::DomGamePathRef ref;
            if (!parse_path_ref(std::string(a + 13), ref, &err)) {
                std::fprintf(stderr, "desync-ref error: %s\n", err.c_str());
                return 2;
            }
            desync_ref = ref;
            has_desync_ref = true;
        } else if (std::strcmp(a, "--dump-timeline") == 0) {
            dump_timeline = true;
        } else if (std::strncmp(a, "--dump-timeline=", 16) == 0) {
            dump_timeline = true;
            timeline_name = std::string(a + 16);
        } else if (std::strcmp(a, "--help") == 0 || std::strcmp(a, "-h") == 0) {
            usage();
            return 0;
        } else {
            std::fprintf(stderr, "Unknown arg: %s\n", a);
            usage();
            return 2;
        }
    }

    if (!has_replay_ref) {
        usage();
        return 2;
    }

    dom::tools::DomToolRuntime rt;
    if (!dom::tools::tool_runtime_init(rt,
                                       "replay_analyzer",
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

    std::string replay_path;
    if (!dom::dom_game_paths_resolve_rel(rt.paths, replay_ref.base_kind, replay_ref.rel, replay_path)) {
        err = "replay path refused";
        dom::tools::tool_runtime_refuse(rt, rt.last_refusal, err);
        return 4;
    }

    dom::tools::RaReplaySummary summary;
    const bool capture_ticks = dump_timeline || has_desync_ref;
    if (!dom::tools::ra_parse_replay(replay_path, capture_ticks, summary, &err)) {
        dom::tools::tool_runtime_refuse(rt, dom::tools::DOM_TOOL_REFUSAL_IO, err);
        std::fprintf(stderr, "replay parse failed: %s\n", err.c_str());
        return 4;
    }

    std::string desync_note;
    if (has_desync_ref) {
        std::string desync_path;
        dom::tools::RaDesyncInfo desync;
        u64 tick = 0ull;
        u64 hash = 0ull;
        if (!dom::dom_game_paths_resolve_rel(rt.paths, desync_ref.base_kind, desync_ref.rel, desync_path)) {
            err = "desync path refused";
            dom::tools::tool_runtime_refuse(rt, rt.last_refusal, err);
            return 4;
        }
        if (!dom::tools::ra_load_desync(desync_path, desync, &err)) {
            dom::tools::tool_runtime_refuse(rt, dom::tools::DOM_TOOL_REFUSAL_IO, err);
            std::fprintf(stderr, "desync load failed: %s\n", err.c_str());
            return 4;
        }
        if (dom::tools::ra_compare_desync(summary, desync, tick, hash, &err)) {
            desync_note = std::string("tick=") + u64_hex(tick) +
                          " replay_hash=0x" + u64_hex(hash);
        } else {
            desync_note = std::string("compare_failed:") + err;
        }
    }

    if (dump_timeline && !summary.ticks.empty()) {
        std::string csv;
        size_t j;
        csv.reserve(128u + summary.ticks.size() * 48u);
        csv += "tick,cmd_count,hash64\n";
        for (j = 0u; j < summary.ticks.size(); ++j) {
            char buf[96];
            std::snprintf(buf, sizeof(buf), "%llu,%u,0x%s\n",
                          (unsigned long long)summary.ticks[j].tick,
                          (unsigned)summary.ticks[j].cmd_count,
                          u64_hex(summary.ticks[j].hash64).c_str());
            csv += buf;
        }
        dom::tools::tool_runtime_emit_output(rt, timeline_name,
                                             csv.empty() ? 0 : (const unsigned char *)csv.c_str(),
                                             csv.size(),
                                             0);
        std::printf("%s", csv.c_str());
    }

    {
        std::string report;
        char buf[64];
        report += "{";
        report += "\"instance_id\":\"";
        report += summary.instance_id;
        report += "\",";
        std::snprintf(buf, sizeof(buf), "%llu", (unsigned long long)summary.run_id);
        report += "\"run_id\":";
        report += buf;
        report += ",";
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)summary.ups);
        report += "\"ups\":";
        report += buf;
        report += ",";
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)summary.feature_epoch);
        report += "\"feature_epoch\":";
        report += buf;
        report += ",";
        std::snprintf(buf, sizeof(buf), "%llu", (unsigned long long)summary.last_tick);
        report += "\"last_tick\":";
        report += buf;
        report += ",";
        std::snprintf(buf, sizeof(buf), "%llu", (unsigned long long)summary.total_cmds);
        report += "\"total_cmds\":";
        report += buf;
        report += ",";
        report += "\"hash64\":\"0x";
        report += u64_hex(summary.hash64);
        report += "\"";
        if (!desync_note.empty()) {
            report += ",\"desync\":\"";
            report += desync_note;
            report += "\"";
        }
        report += "}";
        dom::tools::tool_runtime_emit_output(rt, "replay_report.json",
                                             report.empty() ? 0 : (const unsigned char *)report.c_str(),
                                             report.size(),
                                             0);
        std::printf("%s\n", report.c_str());
    }

    return 0;
}
