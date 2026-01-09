/*
FILE: source/dominium/launcher/core/include/launcher_tools_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / tools_registry
RESPONSIBILITY: Tool registry TLV schema + deterministic encode/decode + instance-scoped enumeration helpers (tools-as-instances).
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core instance model + services facade types only.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Canonical encoding with explicit ordering; skip-unknown supported; hash-stable across OS/architecture for same bytes.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_TOOLS_REGISTRY_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_TOOLS_REGISTRY_H

#include <string>
#include <vector>

extern "C" {
#include "launcher_core_api.h"
}

#include "launcher_instance.h"

namespace dom {
namespace launcher_core {

enum { LAUNCHER_TOOLS_REGISTRY_TLV_VERSION = 1u };

/* tools_registry.tlv schema (versioned root; skip-unknown; canonical ordering).
 *
 * Root required fields:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32): must be `LAUNCHER_TOOLS_REGISTRY_TLV_VERSION`.
 * - `LAUNCHER_TOOLS_REGISTRY_TLV_TAG_TOOL_ENTRY` (container, repeated)
 *
 * Tool entry payload (container TLV):
 * - `LAUNCHER_TOOL_ENTRY_TLV_TAG_TOOL_ID` (string)
 * - `LAUNCHER_TOOL_ENTRY_TLV_TAG_DISPLAY_NAME` (string)
 * - `LAUNCHER_TOOL_ENTRY_TLV_TAG_DESCRIPTION` (string)
 * - `LAUNCHER_TOOL_ENTRY_TLV_TAG_EXECUTABLE_ARTIFACT_HASH` (bytes)
 * - `LAUNCHER_TOOL_ENTRY_TLV_TAG_REQUIRED_PACK` (string, repeated)
 * - `LAUNCHER_TOOL_ENTRY_TLV_TAG_OPTIONAL_PACK` (string, repeated)
 * - `LAUNCHER_TOOL_ENTRY_TLV_TAG_CAPABILITY_REQUIREMENT` (string, repeated)
 * - `LAUNCHER_TOOL_ENTRY_TLV_TAG_UI_ENTRYPOINT_METADATA` (container, optional)
 * - `LAUNCHER_TOOL_ENTRY_TLV_TAG_UI_MODE` (string; "cli"|"tui"|"gui"; optional)
 *
 * UI entrypoint metadata payload (container TLV; placeholders only):
 * - `LAUNCHER_TOOL_UI_META_TLV_TAG_LABEL` (string)
 * - `LAUNCHER_TOOL_UI_META_TLV_TAG_ICON_PLACEHOLDER` (string)
 */
enum LauncherToolsRegistryTlvTag {
    LAUNCHER_TOOLS_REGISTRY_TLV_TAG_TOOL_ENTRY = 2u
};

enum LauncherToolEntryTlvTag {
    LAUNCHER_TOOL_ENTRY_TLV_TAG_TOOL_ID = 1u,
    LAUNCHER_TOOL_ENTRY_TLV_TAG_DISPLAY_NAME = 2u,
    LAUNCHER_TOOL_ENTRY_TLV_TAG_DESCRIPTION = 3u,
    LAUNCHER_TOOL_ENTRY_TLV_TAG_EXECUTABLE_ARTIFACT_HASH = 4u,
    LAUNCHER_TOOL_ENTRY_TLV_TAG_REQUIRED_PACK = 5u,
    LAUNCHER_TOOL_ENTRY_TLV_TAG_OPTIONAL_PACK = 6u,
    LAUNCHER_TOOL_ENTRY_TLV_TAG_CAPABILITY_REQUIREMENT = 7u,
    LAUNCHER_TOOL_ENTRY_TLV_TAG_UI_ENTRYPOINT_METADATA = 8u,
    LAUNCHER_TOOL_ENTRY_TLV_TAG_UI_MODE = 9u
};

enum LauncherToolUiMetaTlvTag {
    LAUNCHER_TOOL_UI_META_TLV_TAG_LABEL = 1u,
    LAUNCHER_TOOL_UI_META_TLV_TAG_ICON_PLACEHOLDER = 2u
};

struct LauncherToolUiMetadata {
    std::string label;
    std::string icon_placeholder;

    LauncherToolUiMetadata();
};

struct LauncherToolEntry {
    std::string tool_id;
    std::string display_name;
    std::string description;
    std::string ui_mode;
    std::vector<unsigned char> executable_artifact_hash_bytes;
    std::vector<std::string> required_packs;
    std::vector<std::string> optional_packs;
    std::vector<std::string> capability_requirements;
    LauncherToolUiMetadata ui_entrypoint_metadata;

    LauncherToolEntry();
};

struct LauncherToolsRegistry {
    u32 schema_version;
    std::vector<LauncherToolEntry> tools;

    LauncherToolsRegistry();
};

bool launcher_tools_registry_to_tlv_bytes(const LauncherToolsRegistry& reg,
                                          std::vector<unsigned char>& out_bytes);
bool launcher_tools_registry_from_tlv_bytes(const unsigned char* data,
                                            size_t size,
                                            LauncherToolsRegistry& out_reg);

/* Loads from:
 * - `<state_root>/tools_registry.tlv` (preferred)
 * - `<state_root>/data/tools_registry.tlv` (fallback)
 */
bool launcher_tools_registry_load(const launcher_services_api_v1* services,
                                  const std::string& state_root_override,
                                  LauncherToolsRegistry& out_reg,
                                  std::string* out_loaded_path,
                                  std::string* out_error);

/* Deterministic find (exact match). */
bool launcher_tools_registry_find(const LauncherToolsRegistry& reg,
                                  const std::string& tool_id,
                                  LauncherToolEntry& out_entry);

/* Enumerates tools available under an instance manifest (required_packs enabled).
 * Output order is tool_id lexicographic.
 */
void launcher_tools_registry_enumerate_for_instance(const LauncherToolsRegistry& reg,
                                                    const LauncherInstanceManifest& manifest,
                                                    std::vector<LauncherToolEntry>& out_tools);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_TOOLS_REGISTRY_H */

