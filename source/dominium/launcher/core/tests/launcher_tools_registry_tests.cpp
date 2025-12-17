/*
FILE: source/dominium/launcher/core/tests/launcher_tools_registry_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / tests
RESPONSIBILITY: Tool registry TLV determinism + instance-scoped enumeration tests.
NOTES: Runs under null services; no UI/gfx dependencies.
*/

#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "launcher_tools_registry.h"

namespace {

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static bool write_file_all(const std::string& path, const std::vector<unsigned char>& bytes) {
    FILE* f = std::fopen(path.c_str(), "wb");
    size_t wrote = 0u;
    if (!f) return false;
    if (!bytes.empty()) {
        wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
    }
    std::fclose(f);
    return wrote == bytes.size();
}

static void remove_file_best_effort(const std::string& path) {
    (void)std::remove(path.c_str());
}

#if defined(_WIN32) || defined(_WIN64)
extern "C" int _mkdir(const char* path);
extern "C" int _rmdir(const char* path);
#else
extern "C" int mkdir(const char* path, unsigned int mode);
extern "C" int rmdir(const char* path);
#endif

static void mkdir_one_best_effort(const std::string& path) {
    if (path.empty()) return;
#if defined(_WIN32) || defined(_WIN64)
    (void)_mkdir(path.c_str());
#else
    (void)mkdir(path.c_str(), 0777u);
#endif
}

static void mkdir_p_best_effort(const std::string& path) {
    std::string p = normalize_seps(path);
    size_t i;
    if (p.empty()) return;
    for (i = 0u; i < p.size(); ++i) {
        if (p[i] == '/') {
            std::string part = p.substr(0u, i);
            if (!part.empty()) mkdir_one_best_effort(part);
        }
    }
    mkdir_one_best_effort(p);
}

static void rmdir_best_effort(const std::string& path) {
#if defined(_WIN32) || defined(_WIN64)
    (void)_rmdir(path.c_str());
#else
    (void)rmdir(path.c_str());
#endif
}

static void u64_to_hex16(u64 v, char out_hex[17]) {
    static const char* hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        out_hex[i] = hex[nib & 0xFu];
    }
    out_hex[16] = '\0';
}

static std::string make_temp_root(const launcher_services_api_v1* services, const char* prefix) {
    void* iface = 0;
    const launcher_time_api_v1* time = 0;
    char hex[17];
    u64 stamp = 0ull;
    if (services && services->query_interface && services->query_interface(LAUNCHER_IID_TIME_V1, &iface) == 0) {
        time = (const launcher_time_api_v1*)iface;
    }
    if (time && time->now_us) {
        stamp = time->now_us();
    }
    u64_to_hex16(stamp, hex);
    return std::string(prefix ? prefix : "tmp") + "_" + std::string(hex);
}

static void test_serialize_parse_roundtrip_is_canonical() {
    dom::launcher_core::LauncherToolsRegistry reg;
    dom::launcher_core::LauncherToolEntry b;
    dom::launcher_core::LauncherToolEntry a;
    std::vector<unsigned char> bytes0;
    std::vector<unsigned char> bytes1;
    dom::launcher_core::LauncherToolsRegistry parsed;

    b.tool_id = "tool.b";
    b.display_name = "B";
    b.description = "desc b";
    b.executable_artifact_hash_bytes.clear();
    b.required_packs.push_back("pack.z");
    b.required_packs.push_back("pack.a");

    a.tool_id = "tool.a";
    a.display_name = "A";
    a.description = "desc a";
    a.ui_entrypoint_metadata.label = "A";
    a.ui_entrypoint_metadata.icon_placeholder = "icon.a";

    reg.tools.push_back(b);
    reg.tools.push_back(a);

    assert(dom::launcher_core::launcher_tools_registry_to_tlv_bytes(reg, bytes0));
    assert(dom::launcher_core::launcher_tools_registry_from_tlv_bytes(bytes0.empty() ? (const unsigned char*)0 : &bytes0[0],
                                                                      bytes0.size(),
                                                                      parsed));
    assert(dom::launcher_core::launcher_tools_registry_to_tlv_bytes(parsed, bytes1));
    assert(bytes0 == bytes1);

    assert(parsed.tools.size() == 2u);
    assert(parsed.tools[0].tool_id == "tool.a");
    assert(parsed.tools[1].tool_id == "tool.b");
}

static void test_load_and_enumerate() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string root = make_temp_root(services, "tmp_tools_registry");
    const std::string data_dir = path_join(root, "data");
    const std::string reg_path = path_join(data_dir, "tools_registry.tlv");
    dom::launcher_core::LauncherToolsRegistry reg;
    dom::launcher_core::LauncherToolEntry t;
    std::vector<unsigned char> bytes;

    mkdir_p_best_effort(data_dir);

    t.tool_id = "tool_manifest_inspector";
    t.display_name = "Manifest Inspector";
    t.description = "Reads handshake and instance manifest";
    t.ui_entrypoint_metadata.label = "Manifest Inspector";
    t.ui_entrypoint_metadata.icon_placeholder = "icon.placeholder";
    reg.tools.push_back(t);

    assert(dom::launcher_core::launcher_tools_registry_to_tlv_bytes(reg, bytes));
    assert(write_file_all(reg_path, bytes));

    {
        dom::launcher_core::LauncherToolsRegistry loaded;
        std::string loaded_path;
        std::string err;
        dom::launcher_core::LauncherToolEntry found;
        bool ok = dom::launcher_core::launcher_tools_registry_load(services, root, loaded, &loaded_path, &err);
        assert(ok);
        assert(normalize_seps(loaded_path) == normalize_seps(reg_path));
        assert(dom::launcher_core::launcher_tools_registry_find(loaded, "tool_manifest_inspector", found));
        assert(found.tool_id == "tool_manifest_inspector");
    }

    {
        dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst0");
        std::vector<dom::launcher_core::LauncherToolEntry> tools;
        dom::launcher_core::launcher_tools_registry_enumerate_for_instance(reg, m, tools);
        assert(tools.size() == 1u);
    }

    {
        dom::launcher_core::LauncherToolsRegistry reg2 = reg;
        reg2.tools[0].required_packs.push_back("pack.x");
        std::vector<dom::launcher_core::LauncherToolEntry> tools;
        dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst1");
        dom::launcher_core::launcher_tools_registry_enumerate_for_instance(reg2, m, tools);
        assert(tools.empty());

        dom::launcher_core::LauncherContentEntry pe;
        pe.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK;
        pe.id = "pack.x";
        pe.version = "1.0.0";
        pe.enabled = 1u;
        pe.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_NEVER;
        pe.hash_bytes.clear();
        m.content_entries.push_back(pe);

        dom::launcher_core::launcher_tools_registry_enumerate_for_instance(reg2, m, tools);
        assert(tools.size() == 1u);
    }

    remove_file_best_effort(reg_path);
    rmdir_best_effort(data_dir);
    rmdir_best_effort(root);
}

} /* namespace */

int main() {
    test_serialize_parse_roundtrip_is_canonical();
    test_load_and_enumerate();
    std::printf("launcher_tools_registry_tests: OK\n");
    return 0;
}

