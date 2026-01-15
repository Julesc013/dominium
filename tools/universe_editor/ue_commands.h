/*
FILE: source/dominium/tools/universe_editor/ue_commands.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/universe_editor
RESPONSIBILITY: Deterministic edit operations for universe bundles (v0).
*/
#ifndef DOM_UNIVERSE_EDITOR_COMMANDS_H
#define DOM_UNIVERSE_EDITOR_COMMANDS_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "runtime/dom_universe_bundle.h"

namespace dom {
namespace tools {

struct UeSystemEntry {
    u64 id;
    u64 parent_id;
    std::string string_id;
};

struct UeRouteEntry {
    u64 id;
    u64 src_station_id;
    u64 dst_station_id;
    u64 duration_ticks;
    u64 capacity_units;
};

bool ue_load_systems(dom_universe_bundle *bundle,
                     std::vector<UeSystemEntry> &out,
                     std::string *err);
bool ue_store_systems(dom_universe_bundle *bundle,
                      const std::vector<UeSystemEntry> &systems,
                      std::string *err);
bool ue_add_system(dom_universe_bundle *bundle,
                   const std::string &string_id,
                   u64 parent_id,
                   std::string *err);
bool ue_remove_system(dom_universe_bundle *bundle,
                      u64 system_id,
                      std::string *err);

bool ue_load_routes(dom_universe_bundle *bundle,
                    std::vector<UeRouteEntry> &out,
                    std::string *err);
bool ue_store_routes(dom_universe_bundle *bundle,
                     const std::vector<UeRouteEntry> &routes,
                     std::string *err);
bool ue_upsert_route(dom_universe_bundle *bundle,
                     const UeRouteEntry &route,
                     std::string *err);
bool ue_remove_route(dom_universe_bundle *bundle,
                     u64 route_id,
                     std::string *err);

} // namespace tools
} // namespace dom

#endif /* DOM_UNIVERSE_EDITOR_COMMANDS_H */
