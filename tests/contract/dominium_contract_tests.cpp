#include <cstdio>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

extern "C" {
#include "launcher_core_api.h"
}

#include "dominium/core_err.h"
#include "dominium/core_job.h"
#include "dominium/core_tlv_schema.h"

#include "launcher_artifact_store.h"
#include "launcher_audit.h"
#include "launcher_handshake.h"
#include "launcher_instance.h"
#include "launcher_pack_manifest.h"
#include "launcher_pack_resolver.h"
#include "launcher_selection_summary.h"
#include "launcher_sha256.h"
#include "launcher_tools_registry.h"
#include "launcher_tlv.h"
#include "launcher_tlv_migrations.h"
#include "launcher_tlv_schema_registry.h"

#include "dsk/dsk_contracts.h"
#include "dsk/dsk_tlv_schema_registry.h"

#ifndef DOM_TLV_VECTORS_DIR
#define DOM_TLV_VECTORS_DIR "."
#endif

static int fail(const char* msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') {
            out[i] = '/';
        }
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

static bool read_file_bytes(const std::string& path, std::vector<unsigned char>& out) {
    std::ifstream in(path.c_str(), std::ios::binary);
    if (!in) {
        return false;
    }
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    in.seekg(0, std::ios::beg);
    if (size < 0) {
        return false;
    }
    out.resize((size_t)size);
    if (size > 0) {
        in.read(reinterpret_cast<char*>(&out[0]), size);
    }
    return in.good() || in.eof();
}

static bool read_text_file(const std::string& path, std::string& out) {
    std::ifstream in(path.c_str(), std::ios::binary);
    std::ostringstream oss;
    if (!in) {
        return false;
    }
    oss << in.rdbuf();
    out = oss.str();
    return true;
}

static std::string normalize_text(const std::string& in) {
    std::string out;
    size_t i;
    out.reserve(in.size());
    for (i = 0u; i < in.size(); ++i) {
        char c = in[i];
        if (c == '\r') {
            continue;
        }
        out.push_back(c);
    }
    while (!out.empty() && (out[out.size() - 1u] == '\n' || out[out.size() - 1u] == ' ')) {
        out.erase(out.size() - 1u);
    }
    return out;
}

static std::string hex_u64(u64 v) {
    static const char* hex = "0123456789abcdef";
    char buf[19];
    int i;
    buf[0] = '0';
    buf[1] = 'x';
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        buf[2 + i] = hex[nib & 0xFu];
    }
    buf[18] = '\0';
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

static std::string sha256_hex(const std::vector<unsigned char>& bytes) {
    unsigned char hash[dom::launcher_core::LAUNCHER_SHA256_BYTES];
    std::vector<unsigned char> buf = bytes;
    dom::launcher_core::launcher_sha256_bytes(buf.empty() ? (const unsigned char*)0 : &buf[0],
                                              buf.size(),
                                              hash);
    std::vector<unsigned char> out(hash, hash + dom::launcher_core::LAUNCHER_SHA256_BYTES);
    return bytes_to_hex_lower(out);
}

static bool write_file_all(const std::string& path, const std::vector<unsigned char>& bytes) {
    std::FILE* f = std::fopen(path.c_str(), "wb");
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

struct VectorEntry {
    std::string dir;
    std::string vector;
    std::string summary;
    std::string sha256;
    u32 schema_id;
    u32 version;
};

static bool parse_u32(const std::string& s, u32& out) {
    char* endp = 0;
    unsigned long v = std::strtoul(s.c_str(), &endp, 10);
    if (!endp || *endp != '\0') {
        return false;
    }
    out = (u32)v;
    return true;
}

static bool parse_manifest_dir(const std::string& dir, std::vector<VectorEntry>& out) {
    std::string path = path_join(dir, "manifest.txt");
    std::string text;
    std::istringstream iss;
    std::string line;
    VectorEntry cur;
    bool has_any = false;

    if (!read_text_file(path, text)) {
        return false;
    }
    iss.str(text);
    while (std::getline(iss, line)) {
        if (!line.empty() && line[line.size() - 1u] == '\r') {
            line.erase(line.size() - 1u);
        }
        if (line.empty()) {
            if (!cur.vector.empty()) {
                cur.dir = dir;
                out.push_back(cur);
                cur = VectorEntry();
                has_any = true;
            }
            continue;
        }
        size_t eq = line.find('=');
        if (eq == std::string::npos) {
            continue;
        }
        std::string key = line.substr(0u, eq);
        std::string val = line.substr(eq + 1u);
        if (key == "schema_id") {
            (void)parse_u32(val, cur.schema_id);
        } else if (key == "version") {
            (void)parse_u32(val, cur.version);
        } else if (key == "vector") {
            cur.vector = val;
        } else if (key == "summary") {
            cur.summary = val;
        } else if (key == "sha256") {
            cur.sha256 = val;
        }
    }
    if (!cur.vector.empty()) {
        cur.dir = dir;
        out.push_back(cur);
        has_any = true;
    }
    return has_any;
}

static std::string summarize_instance_manifest(const std::vector<unsigned char>& data) {
    using namespace dom::launcher_core;
    LauncherInstanceManifest m;
    u32 version = 0u;
    size_t unknown_root = 0u;
    size_t unknown_entry = 0u;
    if (!launcher_instance_manifest_from_tlv_bytes(data.empty() ? (const unsigned char*)0 : &data[0], data.size(), m)) {
        return std::string();
    }
    if (!tlv_read_schema_version_or_default(data.empty() ? (const unsigned char*)0,
                                            data.size(),
                                            version,
                                            launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST))) {
        return std::string();
    }
    unknown_root = m.unknown_fields.size();
    for (size_t i = 0u; i < m.content_entries.size(); ++i) {
        unknown_entry += m.content_entries[i].unknown_fields.size();
    }
    std::ostringstream oss;
    oss << "schema_version=" << version << "\n";
    oss << "instance_id=" << m.instance_id << "\n";
    oss << "content_entries=" << (u32)m.content_entries.size() << "\n";
    for (size_t i = 0u; i < m.content_entries.size(); ++i) {
        oss << "content[" << (u32)i << "].id=" << m.content_entries[i].id << "\n";
    }
    oss << "known_good=" << m.known_good << "\n";
    oss << "unknown_root_tags=" << (u32)unknown_root << "\n";
    oss << "unknown_entry_tags=" << (u32)unknown_entry;
    return oss.str();
}

static std::string summarize_pack_manifest(const std::vector<unsigned char>& data) {
    using namespace dom::launcher_core;
    LauncherPackManifest m;
    u32 version = 0u;
    if (!launcher_pack_manifest_from_tlv_bytes(data.empty() ? (const unsigned char*)0 : &data[0], data.size(), m)) {
        return std::string();
    }
    if (!tlv_read_schema_version_or_default(data.empty() ? (const unsigned char*)0,
                                            data.size(),
                                            version,
                                            launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_PACK_MANIFEST))) {
        return std::string();
    }
    std::ostringstream oss;
    oss << "schema_version=" << version << "\n";
    oss << "pack_id=" << m.pack_id << "\n";
    oss << "pack_type=" << m.pack_type << "\n";
    oss << "version=" << m.version << "\n";
    oss << "required_deps=" << (u32)m.required_packs.size() << "\n";
    oss << "conflicts=" << (u32)m.conflicts.size() << "\n";
    oss << "declared_caps=" << (u32)m.declared_capabilities.size() << "\n";
    oss << "sim_flags=" << (u32)m.sim_affecting_flags.size() << "\n";
    oss << "unknown_root_tags=" << (u32)m.unknown_fields.size();
    return oss.str();
}

static std::string summarize_handshake(const std::vector<unsigned char>& data) {
    using namespace dom::launcher_core;
    LauncherHandshake hs;
    u32 version = 0u;
    if (!launcher_handshake_from_tlv_bytes(data.empty() ? (const unsigned char*)0 : &data[0], data.size(), hs)) {
        return std::string();
    }
    if (!tlv_read_schema_version_or_default(data.empty() ? (const unsigned char*)0,
                                            data.size(),
                                            version,
                                            (u32)LAUNCHER_HANDSHAKE_TLV_VERSION)) {
        return std::string();
    }
    std::ostringstream oss;
    oss << "schema_version=" << version << "\n";
    oss << "run_id=" << hex_u64(hs.run_id) << "\n";
    oss << "instance_id=" << hs.instance_id << "\n";
    oss << "resolved_packs=" << (u32)hs.resolved_packs.size() << "\n";
    oss << "selected_ui=" << hs.selected_ui_backend_id;
    return oss.str();
}

static std::string summarize_audit(const std::vector<unsigned char>& data) {
    using namespace dom::launcher_core;
    LauncherAuditLog audit;
    u32 version = 0u;
    if (!launcher_audit_from_tlv_bytes(data.empty() ? (const unsigned char*)0 : &data[0], data.size(), audit)) {
        return std::string();
    }
    if (!tlv_read_schema_version_or_default(data.empty() ? (const unsigned char*)0,
                                            data.size(),
                                            version,
                                            launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_AUDIT_LOG))) {
        return std::string();
    }
    std::ostringstream oss;
    oss << "schema_version=" << version << "\n";
    oss << "run_id=" << hex_u64(audit.run_id) << "\n";
    oss << "inputs=" << (u32)audit.inputs.size() << "\n";
    oss << "selected_profile=" << audit.selected_profile_id << "\n";
    oss << "has_selection_summary=" << (audit.has_selection_summary ? 1u : 0u) << "\n";
    oss << "selected_backends=" << (u32)audit.selected_backends.size();
    return oss.str();
}

static std::string summarize_selection_summary(const std::vector<unsigned char>& data) {
    using namespace dom::launcher_core;
    LauncherSelectionSummary s;
    u32 version = 0u;
    if (!launcher_selection_summary_from_tlv_bytes(data.empty() ? (const unsigned char*)0 : &data[0], data.size(), s)) {
        return std::string();
    }
    if (!tlv_read_schema_version_or_default(data.empty() ? (const unsigned char*)0,
                                            data.size(),
                                            version,
                                            (u32)LAUNCHER_SELECTION_SUMMARY_TLV_VERSION)) {
        return std::string();
    }
    std::ostringstream oss;
    oss << "schema_version=" << version << "\n";
    oss << "run_id=" << hex_u64(s.run_id) << "\n";
    oss << "instance_id=" << s.instance_id << "\n";
    oss << "profile_id=" << s.launcher_profile_id << "\n";
    oss << "determinism_profile_id=" << s.determinism_profile_id << "\n";
    oss << "resolved_packs_count=" << s.resolved_packs_count << "\n";
    oss << "resolved_packs_summary=" << s.resolved_packs_summary;
    return oss.str();
}

static std::string summarize_tools_registry(const std::vector<unsigned char>& data) {
    using namespace dom::launcher_core;
    LauncherToolsRegistry reg;
    u32 version = 0u;
    if (!launcher_tools_registry_from_tlv_bytes(data.empty() ? (const unsigned char*)0 : &data[0], data.size(), reg)) {
        return std::string();
    }
    if (!tlv_read_schema_version_or_default(data.empty() ? (const unsigned char*)0,
                                            data.size(),
                                            version,
                                            (u32)LAUNCHER_TOOLS_REGISTRY_TLV_VERSION)) {
        return std::string();
    }
    std::ostringstream oss;
    oss << "schema_version=" << version << "\n";
    oss << "tools=" << (u32)reg.tools.size() << "\n";
    if (!reg.tools.empty()) {
        oss << "tool[0].id=" << reg.tools[0].tool_id << "\n";
        oss << "tool[0].required_packs=" << (u32)reg.tools[0].required_packs.size();
    } else {
        oss << "tool[0].id=\n";
        oss << "tool[0].required_packs=0";
    }
    return oss.str();
}

static std::string summarize_caps_snapshot(const std::vector<unsigned char>& data) {
    using namespace dom::launcher_core;
    TlvReader r(data.empty() ? (const unsigned char*)0 : &data[0], data.size());
    TlvRecord rec;
    u32 schema = 0u;
    u32 os_family = 0u;
    u32 cpu_arch = 0u;
    u32 ram_class = 0u;
    u32 backends = 0u;
    u32 selections = 0u;
    while (r.next(rec)) {
        if (rec.tag == 1u) {
            (void)tlv_read_u32_le(rec.payload, rec.len, schema);
        } else if (rec.tag == 5u) {
            (void)tlv_read_u32_le(rec.payload, rec.len, os_family);
        } else if (rec.tag == 8u) {
            (void)tlv_read_u32_le(rec.payload, rec.len, cpu_arch);
        } else if (rec.tag == 9u) {
            (void)tlv_read_u32_le(rec.payload, rec.len, ram_class);
        } else if (rec.tag == 10u) {
            backends += 1u;
        } else if (rec.tag == 11u) {
            selections += 1u;
        }
    }
    std::ostringstream oss;
    oss << "schema_version=" << schema << "\n";
    oss << "os_family=" << os_family << "\n";
    oss << "cpu_arch=" << cpu_arch << "\n";
    oss << "ram_class=" << ram_class << "\n";
    oss << "backends=" << backends << "\n";
    oss << "selections=" << selections;
    return oss.str();
}

static std::string summarize_bundle_meta(const std::vector<unsigned char>& data) {
    using namespace dom::launcher_core;
    TlvReader r(data.empty() ? (const unsigned char*)0 : &data[0], data.size());
    TlvRecord rec;
    u32 schema = 0u;
    u32 bundle_version = 0u;
    u32 audit_count = 0u;
    u32 run_count = 0u;
    std::string mode;
    std::string instance_id;
    while (r.next(rec)) {
        if (rec.tag == 1u) {
            (void)tlv_read_u32_le(rec.payload, rec.len, schema);
        } else if (rec.tag == 2u) {
            (void)tlv_read_u32_le(rec.payload, rec.len, bundle_version);
        } else if (rec.tag == 3u) {
            mode = tlv_read_string(rec.payload, rec.len);
        } else if (rec.tag == 4u) {
            instance_id = tlv_read_string(rec.payload, rec.len);
        } else if (rec.tag == 8u) {
            (void)tlv_read_u32_le(rec.payload, rec.len, audit_count);
        } else if (rec.tag == 9u) {
            (void)tlv_read_u32_le(rec.payload, rec.len, run_count);
        }
    }
    std::ostringstream oss;
    oss << "schema_version=" << schema << "\n";
    oss << "bundle_version=" << bundle_version << "\n";
    oss << "mode=" << mode << "\n";
    oss << "instance_id=" << instance_id << "\n";
    oss << "audit_count=" << audit_count << "\n";
    oss << "run_count=" << run_count;
    return oss.str();
}

static std::string summarize_bundle_index(const std::vector<unsigned char>& data) {
    using namespace dom::launcher_core;
    TlvReader r(data.empty() ? (const unsigned char*)0 : &data[0], data.size());
    TlvRecord rec;
    u32 schema = 0u;
    u32 entries = 0u;
    std::string first_path;
    while (r.next(rec)) {
        if (rec.tag == 1u) {
            (void)tlv_read_u32_le(rec.payload, rec.len, schema);
        } else if (rec.tag == 2u) {
            entries += 1u;
            if (entries == 1u) {
                TlvReader er(rec.payload, (size_t)rec.len);
                TlvRecord e;
                while (er.next(e)) {
                    if (e.tag == 1u) {
                        first_path = tlv_read_string(e.payload, e.len);
                    }
                }
            }
        }
    }
    std::ostringstream oss;
    oss << "schema_version=" << schema << "\n";
    oss << "entries=" << entries << "\n";
    oss << "entry[0].path=" << first_path;
    return oss.str();
}

static std::string summarize_installed_state(const std::vector<unsigned char>& data) {
    dsk_installed_state_t state;
    dsk_status_t st = dsk_installed_state_parse(data.empty() ? (const dsk_u8*)0 : &data[0],
                                                (dsk_u32)data.size(),
                                                &state);
    if (!dsk_error_is_ok(st)) {
        return std::string();
    }
    std::ostringstream oss;
    oss << "product_id=" << state.product_id << "\n";
    oss << "installed_version=" << state.installed_version << "\n";
    oss << "selected_splat=" << state.selected_splat << "\n";
    oss << "components=" << (u32)state.installed_components.size() << "\n";
    oss << "install_roots=" << (u32)state.install_roots.size() << "\n";
    oss << "artifacts=" << (u32)state.artifacts.size() << "\n";
    oss << "registrations=" << (u32)state.registrations.size();
    return oss.str();
}

static std::string summarize_job_def(const std::vector<unsigned char>& data) {
    core_job_def def;
    if (core_job_def_read_tlv(data.empty() ? (const unsigned char*)0 : &data[0],
                              (u32)data.size(),
                              &def) != 0) {
        return std::string();
    }
    std::ostringstream oss;
    oss << "schema_version=" << def.schema_version << "\n";
    oss << "job_type=" << def.job_type << "\n";
    oss << "step_count=" << def.step_count << "\n";
    oss << "steps=" << def.step_count;
    return oss.str();
}

static std::string summarize_job_state(const std::vector<unsigned char>& data) {
    core_job_state st;
    if (core_job_state_read_tlv(data.empty() ? (const unsigned char*)0 : &data[0],
                                (u32)data.size(),
                                &st) != 0) {
        return std::string();
    }
    std::ostringstream oss;
    oss << "schema_version=" << (u32)CORE_JOB_STATE_TLV_VERSION << "\n";
    oss << "job_id=" << hex_u64(st.job_id) << "\n";
    oss << "job_type=" << st.job_type << "\n";
    oss << "current_step=" << st.current_step << "\n";
    oss << "completed_bitset=" << st.completed_steps_bitset << "\n";
    oss << "outcome=" << st.outcome;
    return oss.str();
}

static std::string summarize_vector(const VectorEntry& entry, const std::vector<unsigned char>& data) {
    switch (entry.schema_id) {
    case CORE_TLV_SCHEMA_LAUNCHER_INSTANCE_MANIFEST:
        return summarize_instance_manifest(data);
    case CORE_TLV_SCHEMA_LAUNCHER_PACK_MANIFEST:
        return summarize_pack_manifest(data);
    case CORE_TLV_SCHEMA_LAUNCHER_HANDSHAKE:
        return summarize_handshake(data);
    case CORE_TLV_SCHEMA_LAUNCHER_AUDIT_LOG:
        return summarize_audit(data);
    case CORE_TLV_SCHEMA_LAUNCHER_SELECTION_SUMMARY:
        return summarize_selection_summary(data);
    case CORE_TLV_SCHEMA_LAUNCHER_TOOLS_REGISTRY:
        return summarize_tools_registry(data);
    case CORE_TLV_SCHEMA_LAUNCHER_CAPS_SNAPSHOT:
        return summarize_caps_snapshot(data);
    case CORE_TLV_SCHEMA_DIAG_BUNDLE_META:
        return summarize_bundle_meta(data);
    case CORE_TLV_SCHEMA_DIAG_BUNDLE_INDEX:
        return summarize_bundle_index(data);
    case CORE_TLV_SCHEMA_SETUP_INSTALLED_STATE:
        return summarize_installed_state(data);
    case CORE_TLV_SCHEMA_CORE_JOB_DEF:
        return summarize_job_def(data);
    case CORE_TLV_SCHEMA_CORE_JOB_STATE:
        return summarize_job_state(data);
    default:
        return std::string();
    }
}

static int test_schema_vectors(void) {
    const char* dirs[] = {
        "instance_manifest",
        "pack_manifest",
        "launcher_audit",
        "launcher_handshake",
        "selection_summary",
        "tools_registry",
        "caps_snapshot",
        "diag_bundle_meta",
        "diag_bundle_index",
        "installed_state",
        "core_job_def",
        "core_job_state"
    };
    size_t i;
    core_tlv_schema_reset_registry();
    if (!dom::launcher_core::launcher_register_tlv_schemas()) {
        return fail("launcher_register_tlv_schemas failed");
    }
    if (!dsk_register_tlv_schemas()) {
        return fail("dsk_register_tlv_schemas failed");
    }
    if (!core_job_register_tlv_schemas()) {
        return fail("core_job_register_tlv_schemas failed");
    }

    for (i = 0u; i < sizeof(dirs) / sizeof(dirs[0]); ++i) {
        std::string dir = path_join(DOM_TLV_VECTORS_DIR, dirs[i]);
        std::vector<VectorEntry> entries;
        if (!parse_manifest_dir(dir, entries)) {
            return fail("failed to parse manifest");
        }
        for (size_t j = 0u; j < entries.size(); ++j) {
            const VectorEntry& e = entries[j];
            std::vector<unsigned char> bytes;
            u32 version = 0u;
            err_t err;
            std::string expected_sha;
            std::string expected_summary;
            std::string summary;
            std::string got_sha;

            if (!read_file_bytes(path_join(e.dir, e.vector), bytes)) {
                return fail("failed to read vector bytes");
            }
            if (!read_text_file(path_join(e.dir, e.sha256), expected_sha)) {
                return fail("failed to read sha256");
            }
            if (!read_text_file(path_join(e.dir, e.summary), expected_summary)) {
                return fail("failed to read summary");
            }

            got_sha = sha256_hex(bytes);
            if (normalize_text(expected_sha) != normalize_text(got_sha)) {
                return fail("sha256 mismatch");
            }

            err = core_tlv_schema_validate(e.schema_id,
                                           bytes.empty() ? (const unsigned char*)0 : &bytes[0],
                                           (u32)bytes.size(),
                                           &version);
            if (!err_is_ok(&err)) {
                return fail("schema validation failed");
            }
            if (version != e.version) {
                return fail("schema version mismatch");
            }

            summary = summarize_vector(e, bytes);
            if (summary.empty()) {
                return fail("summary failed");
            }
            if (normalize_text(expected_summary) != normalize_text(summary)) {
                return fail("summary mismatch");
            }
        }
    }
    return 0;
}

struct CreatedArtifact {
    dom::launcher_core::LauncherContentEntry entry;
    std::string hash_hex;
};

static CreatedArtifact create_pack_artifact(const std::string& state_root,
                                            const std::vector<unsigned char>& payload,
                                            const std::string& pack_id,
                                            const std::string& version) {
    using namespace dom::launcher_core;
    CreatedArtifact out;
    unsigned char hash_raw[LAUNCHER_SHA256_BYTES];
    std::vector<unsigned char> hash_bytes;
    std::string dir;
    std::string meta_path;
    std::string payload_path;
    LauncherArtifactMetadata meta;
    std::vector<unsigned char> meta_bytes;

    std::memset(hash_raw, 0, sizeof(hash_raw));
    launcher_sha256_bytes(payload.empty() ? (const unsigned char*)0 : &payload[0], payload.size(), hash_raw);
    hash_bytes.assign(hash_raw, hash_raw + (size_t)LAUNCHER_SHA256_BYTES);

    (void)launcher_artifact_store_paths(state_root, hash_bytes, dir, meta_path, payload_path);
    mkdir_p_best_effort(path_join(dir, "payload"));
    (void)write_file_all(payload_path, payload);

    meta.hash_bytes = hash_bytes;
    meta.size_bytes = (u64)payload.size();
    meta.content_type = (u32)LAUNCHER_CONTENT_PACK;
    meta.timestamp_us = 0ull;
    meta.verification_status = (u32)LAUNCHER_ARTIFACT_VERIFY_VERIFIED;
    meta.source.clear();
    (void)launcher_artifact_metadata_to_tlv_bytes(meta, meta_bytes);
    (void)write_file_all(meta_path, meta_bytes);

    out.entry = LauncherContentEntry();
    out.entry.type = (u32)LAUNCHER_CONTENT_PACK;
    out.entry.id = pack_id;
    out.entry.version = version;
    out.entry.hash_bytes = hash_bytes;
    out.entry.enabled = 1u;
    out.entry.update_policy = (u32)LAUNCHER_UPDATE_PROMPT;
    out.hash_hex = bytes_to_hex_lower(hash_bytes);
    return out;
}

static void cleanup_artifacts_best_effort(const std::string& state_root,
                                          const std::vector<std::string>& artifact_hexes) {
    size_t i;
    for (i = 0u; i < artifact_hexes.size(); ++i) {
        const std::string dir = path_join(path_join(path_join(state_root, "artifacts"), "sha256"), artifact_hexes[i]);
        remove_file_best_effort(path_join(dir, "artifact.tlv"));
        remove_file_best_effort(path_join(path_join(dir, "payload"),
                                          dom::launcher_core::launcher_artifact_store_payload_filename()));
        rmdir_best_effort(path_join(dir, "payload"));
        rmdir_best_effort(dir);
    }
    rmdir_best_effort(path_join(path_join(state_root, "artifacts"), "sha256"));
    rmdir_best_effort(path_join(state_root, "artifacts"));
}

static void cleanup_state_root_best_effort(const std::string& state_root) {
    rmdir_best_effort(state_root);
}

static int test_installed_state_contract(void) {
    std::string path = path_join(DOM_TLV_VECTORS_DIR, "installed_state/installed_state_v1.tlv");
    std::vector<unsigned char> bytes;
    dsk_installed_state_t state;
    dsk_status_t st;

    if (!read_file_bytes(path, bytes)) {
        return fail("installed_state vector read failed");
    }
    st = dsk_installed_state_parse(bytes.empty() ? (const dsk_u8*)0 : &bytes[0], (dsk_u32)bytes.size(), &state);
    if (!dsk_error_is_ok(st)) {
        return fail("installed_state parse failed");
    }
    if (state.product_id != "dominium") {
        return fail("installed_state product mismatch");
    }
    if (state.installed_components.size() != 2u) {
        return fail("installed_state component count mismatch");
    }
    if (state.install_roots.size() != 2u) {
        return fail("installed_state root count mismatch");
    }
    return 0;
}

static int test_handshake_contract(void) {
    using namespace dom::launcher_core;
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = std::string("tests/temp/contract_state");
    std::vector<std::string> artifact_hexes;

    std::vector<unsigned char> pack_base_bytes;
    std::vector<unsigned char> pack_core_bytes;
    std::vector<unsigned char> inst_bytes;
    std::vector<unsigned char> hs_bytes;
    LauncherInstanceManifest manifest;
    LauncherHandshake hs;

    mkdir_p_best_effort(state_root);

    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "pack_manifest/pack_base_v1.tlv"), pack_base_bytes)) {
        return fail("pack base vector read failed");
    }
    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "pack_manifest/pack_core_v1.tlv"), pack_core_bytes)) {
        return fail("pack core vector read failed");
    }
    {
        CreatedArtifact art = create_pack_artifact(state_root, pack_base_bytes, "pack.base", "1.0.0");
        artifact_hexes.push_back(art.hash_hex);
    }
    {
        CreatedArtifact art = create_pack_artifact(state_root, pack_core_bytes, "pack.core", "1.1.0");
        artifact_hexes.push_back(art.hash_hex);
    }

    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "instance_manifest/instance_v2_basic.tlv"), inst_bytes)) {
        cleanup_artifacts_best_effort(state_root, artifact_hexes);
        cleanup_state_root_best_effort(state_root);
        return fail("instance manifest read failed");
    }
    if (!launcher_instance_manifest_from_tlv_bytes(inst_bytes.empty() ? (const unsigned char*)0 : &inst_bytes[0],
                                                   inst_bytes.size(),
                                                   manifest)) {
        cleanup_artifacts_best_effort(state_root, artifact_hexes);
        cleanup_state_root_best_effort(state_root);
        return fail("instance manifest parse failed");
    }

    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "launcher_handshake/handshake_v1_basic.tlv"), hs_bytes)) {
        cleanup_artifacts_best_effort(state_root, artifact_hexes);
        cleanup_state_root_best_effort(state_root);
        return fail("handshake vector read failed");
    }
    if (!launcher_handshake_from_tlv_bytes(hs_bytes.empty() ? (const unsigned char*)0 : &hs_bytes[0],
                                           hs_bytes.size(),
                                           hs)) {
        cleanup_artifacts_best_effort(state_root, artifact_hexes);
        cleanup_state_root_best_effort(state_root);
        return fail("handshake parse failed");
    }

    if (launcher_handshake_validate(services, hs, manifest, state_root, 0) != LAUNCHER_HANDSHAKE_REFUSAL_OK) {
        cleanup_artifacts_best_effort(state_root, artifact_hexes);
        cleanup_state_root_best_effort(state_root);
        return fail("handshake validate expected OK");
    }

    {
        LauncherHandshake bad = hs;
        bad.instance_manifest_hash_bytes[0] ^= 0xFFu;
        if (launcher_handshake_validate(services, bad, manifest, state_root, 0) !=
            LAUNCHER_HANDSHAKE_REFUSAL_MANIFEST_HASH_MISMATCH) {
            cleanup_artifacts_best_effort(state_root, artifact_hexes);
            cleanup_state_root_best_effort(state_root);
            return fail("handshake hash mismatch expected");
        }
    }
    {
        LauncherHandshake bad = hs;
        if (!bad.resolved_packs.empty()) {
            bad.resolved_packs[0].sim_affecting_flags.clear();
        }
        if (launcher_handshake_validate(services, bad, manifest, state_root, 0) !=
            LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS) {
            cleanup_artifacts_best_effort(state_root, artifact_hexes);
            cleanup_state_root_best_effort(state_root);
            return fail("handshake sim flag refusal expected");
        }
    }

    cleanup_artifacts_best_effort(state_root, artifact_hexes);
    cleanup_state_root_best_effort(state_root);
    return 0;
}

static int test_pack_manifest_resolver_contract(void) {
    using namespace dom::launcher_core;
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = std::string("tests/temp/contract_packs");
    std::vector<std::string> artifact_hexes;

    std::vector<unsigned char> pack_base_bytes;
    std::vector<unsigned char> pack_core_bytes;
    std::vector<unsigned char> pack_conflict_bytes;
    LauncherInstanceManifest manifest;
    std::vector<LauncherResolvedPack> ordered;
    std::string err;

    mkdir_p_best_effort(state_root);

    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "pack_manifest/pack_base_v1.tlv"), pack_base_bytes)) {
        return fail("pack base vector read failed");
    }
    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "pack_manifest/pack_core_v1.tlv"), pack_core_bytes)) {
        return fail("pack core vector read failed");
    }
    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "pack_manifest/pack_conflict_v1.tlv"), pack_conflict_bytes)) {
        return fail("pack conflict vector read failed");
    }
    {
        CreatedArtifact art = create_pack_artifact(state_root, pack_base_bytes, "pack.base", "1.0.0");
        artifact_hexes.push_back(art.hash_hex);
    }
    {
        CreatedArtifact art = create_pack_artifact(state_root, pack_core_bytes, "pack.core", "1.1.0");
        artifact_hexes.push_back(art.hash_hex);
    }
    {
        CreatedArtifact art = create_pack_artifact(state_root, pack_conflict_bytes, "pack.conflict", "9.9.0");
        artifact_hexes.push_back(art.hash_hex);
    }

    {
        std::vector<unsigned char> inst_bytes;
        if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "instance_manifest/instance_v2_basic.tlv"), inst_bytes)) {
            cleanup_artifacts_best_effort(state_root, artifact_hexes);
            cleanup_state_root_best_effort(state_root);
            return fail("instance manifest read failed");
        }
        if (!launcher_instance_manifest_from_tlv_bytes(inst_bytes.empty() ? (const unsigned char*)0 : &inst_bytes[0],
                                                       inst_bytes.size(),
                                                       manifest)) {
            cleanup_artifacts_best_effort(state_root, artifact_hexes);
            cleanup_state_root_best_effort(state_root);
            return fail("instance manifest parse failed");
        }
    }

    if (!launcher_pack_resolve_enabled(services, manifest, state_root, ordered, &err)) {
        cleanup_artifacts_best_effort(state_root, artifact_hexes);
        cleanup_state_root_best_effort(state_root);
        return fail("pack resolve failed");
    }
    if (launcher_pack_resolved_order_summary(ordered) != "pack.base,pack.core") {
        cleanup_artifacts_best_effort(state_root, artifact_hexes);
        cleanup_state_root_best_effort(state_root);
        return fail("pack resolve order mismatch");
    }

    {
        LauncherInstanceManifest conflict = launcher_instance_manifest_make_empty("inst_conflict");
        CreatedArtifact base_art = create_pack_artifact(state_root, pack_base_bytes, "pack.base", "1.0.0");
        CreatedArtifact bad_art = create_pack_artifact(state_root, pack_conflict_bytes, "pack.conflict", "9.9.0");
        conflict.content_entries.clear();
        conflict.content_entries.push_back(base_art.entry);
        conflict.content_entries.push_back(bad_art.entry);
        ordered.clear();
        err.clear();
        if (launcher_pack_resolve_enabled(services, conflict, state_root, ordered, &err)) {
            cleanup_artifacts_best_effort(state_root, artifact_hexes);
            cleanup_state_root_best_effort(state_root);
            return fail("pack resolve expected conflict");
        }
        if (err.find("conflict_violation") == std::string::npos) {
            cleanup_artifacts_best_effort(state_root, artifact_hexes);
            cleanup_state_root_best_effort(state_root);
            return fail("pack conflict error text mismatch");
        }
    }

    cleanup_artifacts_best_effort(state_root, artifact_hexes);
    cleanup_state_root_best_effort(state_root);
    return 0;
}

static int test_selection_summary_audit_contract(void) {
    using namespace dom::launcher_core;
    std::vector<unsigned char> sel_bytes;
    std::vector<unsigned char> audit_bytes;
    LauncherSelectionSummary sel;
    LauncherAuditLog audit;

    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "selection_summary/selection_v1_basic.tlv"), sel_bytes)) {
        return fail("selection summary read failed");
    }
    if (!launcher_selection_summary_from_tlv_bytes(sel_bytes.empty() ? (const unsigned char*)0 : &sel_bytes[0],
                                                   sel_bytes.size(),
                                                   sel)) {
        return fail("selection summary parse failed");
    }
    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "launcher_audit/audit_v1_basic.tlv"), audit_bytes)) {
        return fail("audit vector read failed");
    }
    if (!launcher_audit_from_tlv_bytes(audit_bytes.empty() ? (const unsigned char*)0 : &audit_bytes[0],
                                       audit_bytes.size(),
                                       audit)) {
        return fail("audit parse failed");
    }
    if (!audit.has_selection_summary) {
        return fail("audit missing selection summary");
    }
    if (audit.selection_summary_tlv != sel_bytes) {
        return fail("audit selection summary bytes mismatch");
    }
    return 0;
}

static int test_job_journal_contract(void) {
    std::vector<unsigned char> def_bytes;
    std::vector<unsigned char> st_bytes;
    core_job_def def;
    core_job_state st;
    u32 next_idx = 0u;

    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "core_job_def/job_def_v1.tlv"), def_bytes)) {
        return fail("job def vector read failed");
    }
    if (!read_file_bytes(path_join(DOM_TLV_VECTORS_DIR, "core_job_state/job_state_v1.tlv"), st_bytes)) {
        return fail("job state vector read failed");
    }
    if (core_job_def_read_tlv(def_bytes.empty() ? (const unsigned char*)0 : &def_bytes[0],
                              (u32)def_bytes.size(),
                              &def) != 0) {
        return fail("job def parse failed");
    }
    if (core_job_state_read_tlv(st_bytes.empty() ? (const unsigned char*)0 : &st_bytes[0],
                                (u32)st_bytes.size(),
                                &st) != 0) {
        return fail("job state parse failed");
    }
    if (!core_job_def_validate(&def)) {
        return fail("job def validate failed");
    }
    if (!core_job_next_step_index(&def, &st, &next_idx)) {
        return fail("job next step failed");
    }
    if (next_idx != 1u) {
        return fail("job next step mismatch");
    }
    return 0;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: dominium_contract_tests <test>\n");
        return 1;
    }
    if (std::strcmp(argv[1], "schema_vectors") == 0) {
        return test_schema_vectors();
    }
    if (std::strcmp(argv[1], "installed_state_contract") == 0) {
        return test_installed_state_contract();
    }
    if (std::strcmp(argv[1], "handshake_contract") == 0) {
        return test_handshake_contract();
    }
    if (std::strcmp(argv[1], "pack_resolver_contract") == 0) {
        return test_pack_manifest_resolver_contract();
    }
    if (std::strcmp(argv[1], "selection_audit_contract") == 0) {
        return test_selection_summary_audit_contract();
    }
    if (std::strcmp(argv[1], "job_journal_contract") == 0) {
        return test_job_journal_contract();
    }
    std::fprintf(stderr, "unknown test: %s\n", argv[1]);
    return 1;
}
