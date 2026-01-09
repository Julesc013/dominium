/*
FILE: source/dominium/launcher/core/src/tool/launcher_tools_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / tools_registry
RESPONSIBILITY: Implements tools_registry.tlv encode/decode and deterministic instance-scoped enumeration helpers.
*/

#include "launcher_tools_registry.h"

#include <algorithm>
#include <cstring>

#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {

static bool str_lt(const std::string& a, const std::string& b) {
    return a < b;
}

static void sort_strings(std::vector<std::string>& v) {
    std::sort(v.begin(), v.end(), str_lt);
}

static bool entry_lt(const LauncherToolEntry& a, const LauncherToolEntry& b) {
    return a.tool_id < b.tool_id;
}

static const launcher_fs_api_v1* get_fs(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_FS_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_fs_api_v1*)iface;
}

static bool get_state_root(const launcher_fs_api_v1* fs, std::string& out) {
    char buf[512];
    if (!fs || !fs->get_path) {
        return false;
    }
    std::memset(buf, 0, sizeof(buf));
    if (!fs->get_path(LAUNCHER_FS_PATH_STATE, buf, sizeof(buf))) {
        return false;
    }
    out = std::string(buf);
    return !out.empty();
}

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string path_join(const std::string& a, const std::string& b) {
    if (a.empty()) return b;
    if (b.empty()) return a;
    if (is_sep(a[a.size() - 1u])) return a + b;
    return a + std::string("/") + b;
}

static bool fs_read_all(const launcher_fs_api_v1* fs, const std::string& path, std::vector<unsigned char>& out) {
    void* fh;
    long size;
    size_t got;
    out.clear();
    if (!fs || !fs->file_open || !fs->file_seek || !fs->file_tell || !fs->file_read || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }
    if (fs->file_seek(fh, 0, 2) != 0) {
        (void)fs->file_close(fh);
        return false;
    }
    size = fs->file_tell(fh);
    if (size < 0) {
        (void)fs->file_close(fh);
        return false;
    }
    if (fs->file_seek(fh, 0, 0) != 0) {
        (void)fs->file_close(fh);
        return false;
    }
    if (size == 0) {
        (void)fs->file_close(fh);
        return true;
    }
    out.resize((size_t)size);
    got = fs->file_read(fh, out.empty() ? (void*)0 : &out[0], (size_t)size);
    (void)fs->file_close(fh);
    if (got != (size_t)size) {
        out.clear();
        return false;
    }
    return true;
}

static bool fs_file_exists(const launcher_fs_api_v1* fs, const std::string& path) {
    void* fh;
    if (!fs || !fs->file_open || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }
    (void)fs->file_close(fh);
    return true;
}

static bool manifest_has_enabled_entry_id(const LauncherInstanceManifest& manifest, const std::string& id) {
    size_t i;
    for (i = 0u; i < manifest.content_entries.size(); ++i) {
        const LauncherContentEntry& e = manifest.content_entries[i];
        if (e.id == id && e.enabled != 0u) {
            return true;
        }
    }
    return false;
}

} /* namespace */

LauncherToolUiMetadata::LauncherToolUiMetadata()
    : label(),
      icon_placeholder() {
}

LauncherToolEntry::LauncherToolEntry()
    : tool_id(),
      display_name(),
      description(),
      ui_mode(),
      executable_artifact_hash_bytes(),
      required_packs(),
      optional_packs(),
      capability_requirements(),
      ui_entrypoint_metadata() {
}

LauncherToolsRegistry::LauncherToolsRegistry()
    : schema_version(LAUNCHER_TOOLS_REGISTRY_TLV_VERSION),
      tools() {
}

bool launcher_tools_registry_to_tlv_bytes(const LauncherToolsRegistry& reg,
                                          std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    std::vector<LauncherToolEntry> tools = reg.tools;
    size_t i;

    out_bytes.clear();

    std::sort(tools.begin(), tools.end(), entry_lt);

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_TOOLS_REGISTRY_TLV_VERSION);
    for (i = 0u; i < tools.size(); ++i) {
        LauncherToolEntry t = tools[i];
        std::vector<std::string> req = t.required_packs;
        std::vector<std::string> opt = t.optional_packs;
        std::vector<std::string> caps = t.capability_requirements;
        TlvWriter tw;
        size_t j;

        sort_strings(req);
        sort_strings(opt);
        sort_strings(caps);

        tw.add_string(LAUNCHER_TOOL_ENTRY_TLV_TAG_TOOL_ID, t.tool_id);
        tw.add_string(LAUNCHER_TOOL_ENTRY_TLV_TAG_DISPLAY_NAME, t.display_name);
        tw.add_string(LAUNCHER_TOOL_ENTRY_TLV_TAG_DESCRIPTION, t.description);
        if (!t.ui_mode.empty()) {
            tw.add_string(LAUNCHER_TOOL_ENTRY_TLV_TAG_UI_MODE, t.ui_mode);
        }
        if (!t.executable_artifact_hash_bytes.empty()) {
            tw.add_bytes(LAUNCHER_TOOL_ENTRY_TLV_TAG_EXECUTABLE_ARTIFACT_HASH,
                         &t.executable_artifact_hash_bytes[0],
                         (u32)t.executable_artifact_hash_bytes.size());
        } else {
            tw.add_bytes(LAUNCHER_TOOL_ENTRY_TLV_TAG_EXECUTABLE_ARTIFACT_HASH, (const unsigned char*)0, 0u);
        }
        for (j = 0u; j < req.size(); ++j) {
            tw.add_string(LAUNCHER_TOOL_ENTRY_TLV_TAG_REQUIRED_PACK, req[j]);
        }
        for (j = 0u; j < opt.size(); ++j) {
            tw.add_string(LAUNCHER_TOOL_ENTRY_TLV_TAG_OPTIONAL_PACK, opt[j]);
        }
        for (j = 0u; j < caps.size(); ++j) {
            tw.add_string(LAUNCHER_TOOL_ENTRY_TLV_TAG_CAPABILITY_REQUIREMENT, caps[j]);
        }

        if (!t.ui_entrypoint_metadata.label.empty() || !t.ui_entrypoint_metadata.icon_placeholder.empty()) {
            TlvWriter uw;
            uw.add_string(LAUNCHER_TOOL_UI_META_TLV_TAG_LABEL, t.ui_entrypoint_metadata.label);
            uw.add_string(LAUNCHER_TOOL_UI_META_TLV_TAG_ICON_PLACEHOLDER, t.ui_entrypoint_metadata.icon_placeholder);
            tw.add_container(LAUNCHER_TOOL_ENTRY_TLV_TAG_UI_ENTRYPOINT_METADATA, uw.bytes());
        }

        w.add_container(LAUNCHER_TOOLS_REGISTRY_TLV_TAG_TOOL_ENTRY, tw.bytes());
    }

    out_bytes = w.bytes();
    return true;
}

bool launcher_tools_registry_from_tlv_bytes(const unsigned char* data,
                                            size_t size,
                                            LauncherToolsRegistry& out_reg) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;

    out_reg = LauncherToolsRegistry();
    if (!tlv_read_schema_version_or_default(data, size, version, LAUNCHER_TOOLS_REGISTRY_TLV_VERSION)) {
        return false;
    }
    if (version != LAUNCHER_TOOLS_REGISTRY_TLV_VERSION) {
        return false;
    }
    out_reg.schema_version = version;

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case LAUNCHER_TOOLS_REGISTRY_TLV_TAG_TOOL_ENTRY: {
            LauncherToolEntry t;
            TlvReader tr(rec.payload, rec.len);
            TlvRecord trr;
            while (tr.next(trr)) {
                switch (trr.tag) {
                case LAUNCHER_TOOL_ENTRY_TLV_TAG_TOOL_ID:
                    t.tool_id = tlv_read_string(trr.payload, trr.len);
                    break;
                case LAUNCHER_TOOL_ENTRY_TLV_TAG_DISPLAY_NAME:
                    t.display_name = tlv_read_string(trr.payload, trr.len);
                    break;
                case LAUNCHER_TOOL_ENTRY_TLV_TAG_DESCRIPTION:
                    t.description = tlv_read_string(trr.payload, trr.len);
                    break;
                case LAUNCHER_TOOL_ENTRY_TLV_TAG_UI_MODE:
                    t.ui_mode = tlv_read_string(trr.payload, trr.len);
                    break;
                case LAUNCHER_TOOL_ENTRY_TLV_TAG_EXECUTABLE_ARTIFACT_HASH:
                    t.executable_artifact_hash_bytes.assign(trr.payload, trr.payload + (size_t)trr.len);
                    break;
                case LAUNCHER_TOOL_ENTRY_TLV_TAG_REQUIRED_PACK:
                    t.required_packs.push_back(tlv_read_string(trr.payload, trr.len));
                    break;
                case LAUNCHER_TOOL_ENTRY_TLV_TAG_OPTIONAL_PACK:
                    t.optional_packs.push_back(tlv_read_string(trr.payload, trr.len));
                    break;
                case LAUNCHER_TOOL_ENTRY_TLV_TAG_CAPABILITY_REQUIREMENT:
                    t.capability_requirements.push_back(tlv_read_string(trr.payload, trr.len));
                    break;
                case LAUNCHER_TOOL_ENTRY_TLV_TAG_UI_ENTRYPOINT_METADATA: {
                    TlvReader ur(trr.payload, trr.len);
                    TlvRecord urr;
                    while (ur.next(urr)) {
                        switch (urr.tag) {
                        case LAUNCHER_TOOL_UI_META_TLV_TAG_LABEL:
                            t.ui_entrypoint_metadata.label = tlv_read_string(urr.payload, urr.len);
                            break;
                        case LAUNCHER_TOOL_UI_META_TLV_TAG_ICON_PLACEHOLDER:
                            t.ui_entrypoint_metadata.icon_placeholder = tlv_read_string(urr.payload, urr.len);
                            break;
                        default:
                            break;
                        }
                    }
                    break;
                }
                default:
                    break;
                }
            }
            out_reg.tools.push_back(t);
            break;
        }
        default:
            break;
        }
    }

    return true;
}

bool launcher_tools_registry_load(const launcher_services_api_v1* services,
                                  const std::string& state_root_override,
                                  LauncherToolsRegistry& out_reg,
                                  std::string* out_loaded_path,
                                  std::string* out_error) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root;
    std::vector<unsigned char> bytes;
    std::string p0;
    std::string p1;

    if (out_loaded_path) {
        out_loaded_path->clear();
    }
    if (out_error) {
        out_error->clear();
    }

    if (!services || !fs) {
        if (out_error) *out_error = "missing_services_or_fs";
        return false;
    }

    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        if (out_error) *out_error = "state_root_unavailable";
        return false;
    }

    p0 = path_join(state_root, "tools_registry.tlv");
    p1 = path_join(path_join(state_root, "data"), "tools_registry.tlv");

    if (fs_file_exists(fs, p0)) {
        if (!fs_read_all(fs, p0, bytes) || bytes.empty()) {
            if (out_error) *out_error = std::string("read_failed;path=") + p0;
            return false;
        }
        if (!launcher_tools_registry_from_tlv_bytes(&bytes[0], bytes.size(), out_reg)) {
            if (out_error) *out_error = std::string("decode_failed;path=") + p0;
            return false;
        }
        if (out_loaded_path) *out_loaded_path = p0;
        return true;
    }

    if (fs_file_exists(fs, p1)) {
        if (!fs_read_all(fs, p1, bytes) || bytes.empty()) {
            if (out_error) *out_error = std::string("read_failed;path=") + p1;
            return false;
        }
        if (!launcher_tools_registry_from_tlv_bytes(&bytes[0], bytes.size(), out_reg)) {
            if (out_error) *out_error = std::string("decode_failed;path=") + p1;
            return false;
        }
        if (out_loaded_path) *out_loaded_path = p1;
        return true;
    }

    if (out_error) *out_error = "tools_registry_missing";
    return false;
}

bool launcher_tools_registry_find(const LauncherToolsRegistry& reg,
                                  const std::string& tool_id,
                                  LauncherToolEntry& out_entry) {
    size_t i;
    out_entry = LauncherToolEntry();
    if (tool_id.empty()) {
        return false;
    }
    for (i = 0u; i < reg.tools.size(); ++i) {
        if (reg.tools[i].tool_id == tool_id) {
            out_entry = reg.tools[i];
            return true;
        }
    }
    return false;
}

void launcher_tools_registry_enumerate_for_instance(const LauncherToolsRegistry& reg,
                                                    const LauncherInstanceManifest& manifest,
                                                    std::vector<LauncherToolEntry>& out_tools) {
    size_t i;
    out_tools.clear();
    for (i = 0u; i < reg.tools.size(); ++i) {
        const LauncherToolEntry& t = reg.tools[i];
        bool ok = true;
        size_t j;
        for (j = 0u; j < t.required_packs.size(); ++j) {
            if (!manifest_has_enabled_entry_id(manifest, t.required_packs[j])) {
                ok = false;
                break;
            }
        }
        if (ok) {
            out_tools.push_back(t);
        }
    }
    std::sort(out_tools.begin(), out_tools.end(), entry_lt);
}

} /* namespace launcher_core */
} /* namespace dom */

