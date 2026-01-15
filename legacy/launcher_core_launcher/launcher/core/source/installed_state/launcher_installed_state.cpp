/*
FILE: source/dominium/launcher/core/src/installed_state/launcher_installed_state.cpp
MODULE: Dominium
PURPOSE: Launcher-side installed_state parsing/writing helpers.
*/

#include "launcher_installed_state.h"

#include "dominium/core_tlv.h"

namespace dom {
namespace launcher_core {

bool launcher_installed_state_from_tlv_bytes(const unsigned char* data,
                                             size_t size,
                                             LauncherInstalledState& out_state) {
    return launcher_installed_state_from_tlv_bytes_ex(data, size, out_state, 0);
}

bool launcher_installed_state_from_tlv_bytes_ex(const unsigned char* data,
                                                size_t size,
                                                LauncherInstalledState& out_state,
                                                err_t* out_err) {
    err_t err = dom::core_installed_state::installed_state_parse(data, (u32)size, &out_state);
    if (out_err) {
        *out_err = err;
    }
    return err_is_ok(&err) ? true : false;
}

bool launcher_installed_state_to_tlv_bytes(const LauncherInstalledState& state,
                                           std::vector<unsigned char>& out_bytes) {
    return launcher_installed_state_to_tlv_bytes_ex(state, out_bytes, 0);
}

bool launcher_installed_state_to_tlv_bytes_ex(const LauncherInstalledState& state,
                                              std::vector<unsigned char>& out_bytes,
                                              err_t* out_err) {
    core_tlv_framed_buffer_t buf;
    err_t err = dom::core_installed_state::installed_state_write(&state, &buf);
    if (out_err) {
        *out_err = err;
    }
    if (!err_is_ok(&err)) {
        out_bytes.clear();
        return false;
    }
    out_bytes.assign(buf.data, buf.data + buf.size);
    core_tlv_framed_buffer_free(&buf);
    return true;
}

u64 launcher_installed_state_hash64(const LauncherInstalledState& state) {
    std::vector<unsigned char> bytes;
    if (!launcher_installed_state_to_tlv_bytes(state, bytes)) {
        return 0ull;
    }
    return dom::core_tlv::tlv_fnv1a64(bytes.empty() ? (const unsigned char*)0 : &bytes[0],
                                      bytes.size());
}

} /* namespace launcher_core */
} /* namespace dom */
