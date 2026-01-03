/*
FILE: source/dominium/launcher/tools/tool_manifest_inspector.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/tools / tool_manifest_inspector
RESPONSIBILITY: Example tool that reads `--handshake=` + instance manifest and prints a stable, structured report to stdout (no UI required).
*/

#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>

#include "core/include/launcher_handshake.h"
#include "core/include/launcher_instance.h"
#include "core/include/launcher_sha256.h"

namespace {

static bool is_sep(char c) { return c == '/' || c == '\\'; }

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static std::string dirname_of(const std::string& path) {
    size_t i;
    for (i = path.size(); i > 0u; --i) {
        if (is_sep(path[i - 1u])) {
            return path.substr(0u, i - 1u);
        }
    }
    return std::string();
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static bool file_exists(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    std::fclose(f);
    return true;
}

static bool read_file_all(const std::string& path, std::vector<unsigned char>& out_bytes) {
    FILE* f;
    long sz;
    size_t got;
    out_bytes.clear();
    f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    sz = std::ftell(f);
    if (sz < 0) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    if (sz == 0) {
        std::fclose(f);
        return true;
    }
    out_bytes.resize((size_t)sz);
    got = std::fread(out_bytes.empty() ? (void*)0 : &out_bytes[0], 1u, (size_t)sz, f);
    std::fclose(f);
    if (got != (size_t)sz) {
        out_bytes.clear();
        return false;
    }
    return true;
}

static std::string u64_hex16(u64 v) {
    static const char* hex = "0123456789abcdef";
    char buf[17];
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        buf[i] = hex[nib & 0xFu];
    }
    buf[16] = '\0';
    return std::string(buf);
}

static bool is_abs_path(const std::string& path) {
    if (path.empty()) {
        return false;
    }
    if (path[0] == '/' || path[0] == '\\') {
        return true;
    }
    return (path.size() > 1u && path[1] == ':');
}

static std::string resolve_handshake_path(const std::string& handshake_arg) {
    if (handshake_arg.empty() || is_abs_path(handshake_arg)) {
        return handshake_arg;
    }
    {
        const char* run_root = std::getenv("DOMINIUM_RUN_ROOT");
        if (run_root && run_root[0]) {
            return path_join(run_root, handshake_arg);
        }
    }
    return handshake_arg;
}

static std::string u32_to_string(u32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%u", (unsigned)v);
    return std::string(buf);
}

static std::string bytes_to_hex_lower(const std::vector<unsigned char>& bytes) {
    static const char* hex = "0123456789abcdef";
    std::string out;
    size_t i;
    out.reserve(bytes.size() * 2u);
    for (i = 0u; i < bytes.size(); ++i) {
        unsigned v = (unsigned)bytes[i];
        out.push_back(hex[(v >> 4u) & 0xFu]);
        out.push_back(hex[v & 0xFu]);
    }
    return out;
}

static std::string resolve_instance_manifest_path_from_handshake_path(const std::string& handshake_path,
                                                                      const std::string& instance_id) {
    /* Preferred: infer instance_root by walking up: run_id -> runs -> logs -> instance_root. */
    {
        std::string d = normalize_seps(handshake_path);
        d = dirname_of(d); /* .../logs/runs/<run_id> */
        d = dirname_of(d); /* .../logs/runs */
        d = dirname_of(d); /* .../logs */
        d = dirname_of(d); /* .../<instance_root> */
        if (!d.empty()) {
            std::string cand = path_join(d, "manifest.tlv");
            if (file_exists(cand)) {
                return cand;
            }
        }
    }

    /* Fallback: assume cwd is state_root. */
    if (!instance_id.empty()) {
        return path_join(path_join("instances", instance_id), "manifest.tlv");
    }
    return std::string("manifest.tlv");
}

static void out_kv(const char* key, const std::string& val) {
    std::printf("%s=%s\n", key ? key : "", val.c_str());
}

static void out_kv(const char* key, const char* val) {
    std::printf("%s=%s\n", key ? key : "", val ? val : "");
}

static void out_kv_u32(const char* key, u32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%u", (unsigned)v);
    out_kv(key, buf);
}

static void out_kv_i32(const char* key, i32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%d", (int)v);
    out_kv(key, buf);
}

} /* namespace */

int main(int argc, char** argv) {
    std::string handshake_path;
    std::vector<unsigned char> hs_bytes;
    dom::launcher_core::LauncherHandshake hs;
    std::vector<unsigned char> man_bytes;
    dom::launcher_core::LauncherInstanceManifest m;
    std::string manifest_path;
    std::vector<unsigned char> man_tlv;
    unsigned char man_sha[dom::launcher_core::LAUNCHER_SHA256_BYTES];
    std::vector<unsigned char> man_sha_vec;
    u64 hs_hash64 = 0ull;
    u64 man_hash64 = 0ull;
    size_t i;

    for (i = 1; i < (size_t)((argc > 0) ? argc : 0); ++i) {
        const char* a = argv[i];
        if (!a) continue;
        if (std::strncmp(a, "--handshake=", 12) == 0) {
            handshake_path = std::string(a + 12);
        }
    }

    handshake_path = resolve_handshake_path(handshake_path);

    out_kv("tool", "tool_manifest_inspector");
    out_kv("handshake.path", handshake_path);

    if (handshake_path.empty()) {
        out_kv("result", "fail");
        out_kv("error", "missing_handshake_arg");
        return 2;
    }

    if (!read_file_all(handshake_path, hs_bytes) || hs_bytes.empty()) {
        out_kv("result", "fail");
        out_kv("error", "read_handshake_failed");
        return 1;
    }
    if (!dom::launcher_core::launcher_handshake_from_tlv_bytes(&hs_bytes[0], hs_bytes.size(), hs)) {
        out_kv("result", "fail");
        out_kv("error", "decode_handshake_failed");
        return 1;
    }

    hs_hash64 = dom::launcher_core::launcher_handshake_hash64(hs);

    out_kv("handshake.run_id", std::string("0x") + u64_hex16(hs.run_id));
    out_kv("handshake.instance_id", hs.instance_id);
    out_kv("handshake.hash64", std::string("0x") + u64_hex16(hs_hash64));
    out_kv("handshake.manifest_sha256_hex", bytes_to_hex_lower(hs.instance_manifest_hash_bytes));

    manifest_path = resolve_instance_manifest_path_from_handshake_path(handshake_path, hs.instance_id);
    out_kv("manifest.path", manifest_path);

    if (!read_file_all(manifest_path, man_bytes) || man_bytes.empty()) {
        out_kv("result", "fail");
        out_kv("error", "read_manifest_failed");
        return 1;
    }
    if (!dom::launcher_core::launcher_instance_manifest_from_tlv_bytes(&man_bytes[0], man_bytes.size(), m)) {
        out_kv("result", "fail");
        out_kv("error", "decode_manifest_failed");
        return 1;
    }

    man_hash64 = dom::launcher_core::launcher_instance_manifest_hash64(m);
    out_kv("manifest.instance_id", m.instance_id);
    out_kv("manifest.hash64", std::string("0x") + u64_hex16(man_hash64));
    out_kv("manifest.pinned_engine_build_id", m.pinned_engine_build_id);
    out_kv("manifest.pinned_game_build_id", m.pinned_game_build_id);

    std::memset(man_sha, 0, sizeof(man_sha));
    if (dom::launcher_core::launcher_instance_manifest_to_tlv_bytes(m, man_tlv)) {
        dom::launcher_core::launcher_sha256_bytes(man_tlv.empty() ? (const unsigned char*)0 : &man_tlv[0], man_tlv.size(), man_sha);
        man_sha_vec.assign(man_sha, man_sha + (size_t)dom::launcher_core::LAUNCHER_SHA256_BYTES);
        out_kv("manifest.sha256_hex", bytes_to_hex_lower(man_sha_vec));
        out_kv("manifest.sha256_matches_handshake", (man_sha_vec == hs.instance_manifest_hash_bytes) ? "1" : "0");
    }

    out_kv_u32("packs.count", (u32)hs.resolved_packs.size());
    for (i = 0u; i < hs.resolved_packs.size(); ++i) {
        const dom::launcher_core::LauncherHandshakePackEntry& pe = hs.resolved_packs[i];
        const std::string pfx = std::string("packs[") + u32_to_string((u32)i) + "].";
        size_t j;
        out_kv((pfx + "id").c_str(), pe.pack_id);
        out_kv((pfx + "version").c_str(), pe.version);
        out_kv_u32((pfx + "enabled").c_str(), pe.enabled);
        out_kv((pfx + "hash_hex").c_str(), bytes_to_hex_lower(pe.hash_bytes));
        out_kv_u32((pfx + "offline_mode_flag").c_str(), pe.offline_mode_flag);
        out_kv_u32((pfx + "sim_flags.count").c_str(), (u32)pe.sim_affecting_flags.size());
        for (j = 0u; j < pe.sim_affecting_flags.size(); ++j) {
            out_kv((pfx + "sim_flags[" + u32_to_string((u32)j) + "]").c_str(), pe.sim_affecting_flags[j]);
        }
        out_kv_u32((pfx + "safe_mode_flags.count").c_str(), (u32)pe.safe_mode_flags.size());
        for (j = 0u; j < pe.safe_mode_flags.size(); ++j) {
            out_kv((pfx + "safe_mode_flags[" + u32_to_string((u32)j) + "]").c_str(), pe.safe_mode_flags[j]);
        }
    }

    out_kv("result", "ok");
    out_kv_i32("exit_code", 0);
    return 0;
}
