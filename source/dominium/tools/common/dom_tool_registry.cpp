/*
FILE: source/dominium/tools/common/dom_tool_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_registry
RESPONSIBILITY: Implements `dom_tool_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_tool_registry.h"

#include <cstring>

namespace dom {
namespace tools {
namespace {

static const DomToolDesc g_tools[] = {
    { "world_editor",     "World Editor",     "Edit world metadata and topology",          "dominium-world-editor" },
    { "blueprint_editor", "Blueprint Editor", "Create reusable structure layouts",         "dominium-blueprint-editor" },
    { "tech_editor",      "Tech Tree Editor", "Edit research graphs and unlocks",          "dominium-tech-editor" },
    { "policy_editor",    "Policy Editor",    "Edit rulesets and effect graphs",           "dominium-policy-editor" },
    { "process_editor",   "Process Editor",   "Edit production recipes and IO",            "dominium-process-editor" },
    { "transport_editor", "Transport Editor", "Edit spline transport profiles",            "dominium-transport-editor" },
    { "struct_editor",    "Structure Editor", "Edit structures, machines, vehicles",       "dominium-struct-editor" },
    { "item_editor",      "Item Editor",      "Edit items, materials, categories, icons",  "dominium-item-editor" },
    { "pack_editor",      "Pack Editor",      "Edit UI skins, icons, sprites, audio",      "dominium-pack-editor" },
    { "mod_builder",      "Mod Builder",      "Build deterministic .dmod packages",        "dominium-mod-builder" },
    { "save_inspector",   "Save Inspector",   "Inspect saves and compute world hashes",    "dominium-save-inspector" },
    { "replay_viewer",    "Replay Viewer",    "Inspect replays and analyze desyncs",       "dominium-replay-viewer" },
    { "net_inspector",    "Net Inspector",    "Inspect network sessions and packet logs", "dominium-net-inspector" },
};

static size_t g_tool_count = sizeof(g_tools) / sizeof(g_tools[0]);

static int streq(const char *a, const char *b) {
    if (!a || !b) {
        return 0;
    }
    return std::strcmp(a, b) == 0;
}

} // namespace

const DomToolDesc *tool_list(size_t *out_count) {
    if (out_count) {
        *out_count = g_tool_count;
    }
    return g_tools;
}

const DomToolDesc *find_tool(const char *id) {
    size_t i;
    if (!id) {
        return 0;
    }
    for (i = 0u; i < g_tool_count; ++i) {
        if (streq(g_tools[i].id, id)) {
            return &g_tools[i];
        }
    }
    return 0;
}

} // namespace tools
} // namespace dom

