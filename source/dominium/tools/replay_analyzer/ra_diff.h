/*
FILE: source/dominium/tools/replay_analyzer/ra_diff.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/replay_analyzer
RESPONSIBILITY: Desync bundle parsing and replay diff helpers.
*/
#ifndef DOM_REPLAY_ANALYZER_DIFF_H
#define DOM_REPLAY_ANALYZER_DIFF_H

#include <string>

extern "C" {
#include "domino/core/types.h"
}

#include "ra_parser.h"

namespace dom {
namespace tools {

struct RaDesyncInfo {
    u64 tick;
    u64 expected_hash64;
    u64 actual_hash64;
    bool has_expected;
    bool has_actual;
};

bool ra_load_desync(const std::string &path,
                    RaDesyncInfo &out,
                    std::string *err);

bool ra_compare_desync(const RaReplaySummary &summary,
                       const RaDesyncInfo &desync,
                       u64 &out_tick,
                       u64 &out_hash,
                       std::string *err);

} // namespace tools
} // namespace dom

#endif /* DOM_REPLAY_ANALYZER_DIFF_H */
