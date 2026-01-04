/*
FILE: source/dominium/launcher/ui/launcher_ui_session_state.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/ui
RESPONSIBILITY: Implements dev-only UI session state TLV load/save helpers.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS/UI toolkit headers; launcher core headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Local-only persistence; not part of deterministic outputs.
VERSIONING / ABI / DATA FORMAT NOTES: TLV schema version=1.
EXTENSION POINTS: Add new TLV tags with version bump.
*/
#include "ui/launcher_ui_session_state.h"

#include <cstdio>
#include <vector>

#include "dominium/core_tlv.h"
#include "dom_launcher/launcher_context.h"
#include "dom_shared/os_paths.h"

namespace dom {

LauncherUiSessionState::LauncherUiSessionState()
    : schema_version(1u),
      tab_id(0u),
      instance_id(),
      play_target_item_id(0u),
      window_x(0),
      window_y(0),
      window_w(0),
      window_h(0) {}

static bool read_file_bytes(const std::string& path,
                            std::vector<unsigned char>& out_bytes,
                            std::string& out_error) {
    std::FILE* f;
    long size;
    size_t got;
    out_bytes.clear();
    out_error.clear();

    f = std::fopen(path.c_str(), "rb");
    if (!f) {
        out_error = "open_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        out_error = "seek_end_failed";
        return false;
    }
    size = std::ftell(f);
    if (size < 0) {
        std::fclose(f);
        out_error = "tell_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        out_error = "seek_set_failed";
        return false;
    }
    out_bytes.resize((size_t)size);
    got = 0u;
    if (size > 0) {
        got = std::fread(&out_bytes[0], 1u, (size_t)size, f);
    }
    std::fclose(f);
    if (got != (size_t)size) {
        out_bytes.clear();
        out_error = "read_failed";
        return false;
    }
    return true;
}

static bool write_file_bytes(const std::string& path,
                             const std::vector<unsigned char>& bytes,
                             std::string& out_error) {
    std::FILE* f;
    size_t wrote;
    out_error.clear();

    if (path.empty()) {
        out_error = "bad_path";
        return false;
    }

    f = std::fopen(path.c_str(), "wb");
    if (!f) {
        out_error = "open_failed";
        return false;
    }
    wrote = 0u;
    if (!bytes.empty()) {
        wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
    }
    std::fclose(f);
    if (wrote != bytes.size()) {
        out_error = "write_failed";
        return false;
    }
    return true;
}

std::string launcher_ui_session_state_path() {
    const dom_launcher::LauncherContext ctx = dom_launcher::get_launcher_context();
    return dom_shared::os_path_join(ctx.user_data_root, "ui_session_state.tlv");
}

bool launcher_ui_session_state_load(LauncherUiSessionState& out_state, std::string& out_error) {
    std::vector<unsigned char> bytes;
    core_tlv::TlvReader reader(0, 0u);
    core_tlv::TlvRecord rec;
    u32 version = 1u;
    bool version_seen = false;

    out_state = LauncherUiSessionState();
    out_error.clear();

    {
        const std::string path = launcher_ui_session_state_path();
        if (!dom_shared::os_file_exists(path)) {
            out_error = "state_missing";
            return false;
        }
        if (!read_file_bytes(path, bytes, out_error) || bytes.empty()) {
            if (out_error.empty()) {
                out_error = "read_failed";
            }
            return false;
        }
    }

    reader = core_tlv::TlvReader(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size());
    while (reader.next(rec)) {
        if (rec.tag == (u32)UI_SESSION_TAG_SCHEMA_VERSION) {
            if (!core_tlv::tlv_read_u32_le(rec.payload, rec.len, version)) {
                out_error = "schema_version_invalid";
                return false;
            }
            version_seen = true;
            continue;
        }
        if (rec.tag == (u32)UI_SESSION_TAG_TAB_ID) {
            (void)core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_state.tab_id);
        } else if (rec.tag == (u32)UI_SESSION_TAG_INSTANCE_ID) {
            out_state.instance_id = core_tlv::tlv_read_string(rec.payload, rec.len);
        } else if (rec.tag == (u32)UI_SESSION_TAG_PLAY_TARGET_ITEM_ID) {
            (void)core_tlv::tlv_read_u32_le(rec.payload, rec.len, out_state.play_target_item_id);
        } else if (rec.tag == (u32)UI_SESSION_TAG_WINDOW_X) {
            (void)core_tlv::tlv_read_i32_le(rec.payload, rec.len, out_state.window_x);
        } else if (rec.tag == (u32)UI_SESSION_TAG_WINDOW_Y) {
            (void)core_tlv::tlv_read_i32_le(rec.payload, rec.len, out_state.window_y);
        } else if (rec.tag == (u32)UI_SESSION_TAG_WINDOW_W) {
            (void)core_tlv::tlv_read_i32_le(rec.payload, rec.len, out_state.window_w);
        } else if (rec.tag == (u32)UI_SESSION_TAG_WINDOW_H) {
            (void)core_tlv::tlv_read_i32_le(rec.payload, rec.len, out_state.window_h);
        }
    }

    if (version_seen && version != 1u) {
        out_error = "schema_version_mismatch";
        return false;
    }

    out_state.schema_version = version;
    return true;
}

bool launcher_ui_session_state_save(const LauncherUiSessionState& state, std::string& out_error) {
    core_tlv::TlvWriter writer;
    const dom_launcher::LauncherContext ctx = dom_launcher::get_launcher_context();

    out_error.clear();
    if (!dom_shared::os_ensure_directory_exists(ctx.user_data_root)) {
        out_error = "ensure_dir_failed";
        return false;
    }

    writer.add_u32((u32)UI_SESSION_TAG_SCHEMA_VERSION, 1u);
    writer.add_u32((u32)UI_SESSION_TAG_TAB_ID, state.tab_id);
    writer.add_string((u32)UI_SESSION_TAG_INSTANCE_ID, state.instance_id);
    writer.add_u32((u32)UI_SESSION_TAG_PLAY_TARGET_ITEM_ID, state.play_target_item_id);
    writer.add_i32((u32)UI_SESSION_TAG_WINDOW_X, state.window_x);
    writer.add_i32((u32)UI_SESSION_TAG_WINDOW_Y, state.window_y);
    writer.add_i32((u32)UI_SESSION_TAG_WINDOW_W, state.window_w);
    writer.add_i32((u32)UI_SESSION_TAG_WINDOW_H, state.window_h);

    return write_file_bytes(launcher_ui_session_state_path(), writer.bytes(), out_error);
}

} // namespace dom
