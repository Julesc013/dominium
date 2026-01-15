/*
FILE: source/dominium/tools/universe_editor/ue_queries.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/universe_editor
RESPONSIBILITY: Read-only queries and summaries for universe bundles.
*/
#ifndef DOM_UNIVERSE_EDITOR_QUERIES_H
#define DOM_UNIVERSE_EDITOR_QUERIES_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "runtime/dom_universe_bundle.h"

namespace dom {
namespace tools {

struct UeChunkInfo {
    u32 type_id;
    u16 version;
    u32 size;
    bool present;
};

struct UeSummary {
    std::string universe_id;
    std::string instance_id;
    u64 tick_index;
    u32 ups;
    u32 feature_epoch;
    u32 systems_count;
    u32 routes_count;
    bool systems_parsed;
    bool routes_parsed;
    std::vector<UeChunkInfo> chunks;
};

bool ue_build_summary(dom_universe_bundle *bundle,
                      UeSummary &out,
                      std::string *err);
std::string ue_summary_json(const UeSummary &summary);

bool ue_list_systems(dom_universe_bundle *bundle,
                     std::string &out,
                     std::string *err);
bool ue_list_routes(dom_universe_bundle *bundle,
                    std::string &out,
                    std::string *err);

} // namespace tools
} // namespace dom

#endif /* DOM_UNIVERSE_EDITOR_QUERIES_H */
