/*
FILE: source/dominium/tools/replay_analyzer/ra_parser.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/replay_analyzer
RESPONSIBILITY: Replay parsing helpers for analysis tools.
*/
#ifndef DOM_REPLAY_ANALYZER_PARSER_H
#define DOM_REPLAY_ANALYZER_PARSER_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "runtime/dom_game_replay.h"
}

namespace dom {
namespace tools {

struct RaTickSummary {
    u64 tick;
    u32 cmd_count;
    u64 hash64;
};

struct RaReplaySummary {
    u64 last_tick;
    u64 total_cmds;
    u64 hash64;
    u32 ups;
    u32 feature_epoch;
    u64 run_id;
    std::string instance_id;
    std::vector<RaTickSummary> ticks;
};

bool ra_parse_replay(const std::string &path,
                     bool capture_ticks,
                     RaReplaySummary &out,
                     std::string *err);

} // namespace tools
} // namespace dom

#endif /* DOM_REPLAY_ANALYZER_PARSER_H */
