/*
FILE: source/dominium/launcher/launcher_caps_snapshot.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / caps_snapshot
RESPONSIBILITY: Implements deterministic capability snapshot build + TLV/text rendering.
*/

#include "launcher_caps_snapshot.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <sstream>

extern "C" {
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/profile.h"
#include "dominium/product_info.h"
#include "dominium/version.h"
}

#include "core/include/launcher_tlv.h"

#include <limits.h>

#if defined(_WIN32) || defined(_WIN64)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

#if defined(__unix__) || defined(__APPLE__)
#include <sys/utsname.h>
#include <unistd.h>
#endif

namespace dom {

namespace {

static std::string safe_str(const char* s) {
    return (s && s[0]) ? std::string(s) : std::string();
}

static std::string u32_hex8(u32 v) {
    static const char* hex = "0123456789abcdef";
    char buf[9];
    int i;
    for (i = 0; i < 8; ++i) {
        unsigned shift = (unsigned)((7 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & 0xFu);
        buf[i] = hex[nib & 0xFu];
    }
    buf[8] = '\0';
    return std::string(buf);
}

static std::string subsystem_name_or_hex(u32 subsystem_id, const char* name) {
    if (name && name[0]) {
        return std::string(name);
    }
    return std::string("0x") + u32_hex8(subsystem_id);
}

static void parse_major_minor(const char* s, u32& out_major, u32& out_minor) {
    u64 major = 0ull;
    u64 minor = 0ull;
    const char* p = s;
    out_major = 0u;
    out_minor = 0u;
    if (!s || !s[0]) {
        return;
    }
    while (*p >= '0' && *p <= '9') {
        major = (major * 10ull) + (u64)(*p - '0');
        ++p;
    }
    if (*p == '.') {
        ++p;
        while (*p >= '0' && *p <= '9') {
            minor = (minor * 10ull) + (u64)(*p - '0');
            ++p;
        }
    }
    out_major = (u32)((major > 0xFFFFFFFFull) ? 0u : (u32)major);
    out_minor = (u32)((minor > 0xFFFFFFFFull) ? 0u : (u32)minor);
}

static void detect_os_version(u32& out_major, u32& out_minor) {
    out_major = 0u;
    out_minor = 0u;
#if defined(_WIN32) || defined(_WIN64)
    OSVERSIONINFOEXA info;
    std::memset(&info, 0, sizeof(info));
    info.dwOSVersionInfoSize = sizeof(info);
    if (GetVersionExA((OSVERSIONINFOA*)&info)) {
        out_major = (u32)info.dwMajorVersion;
        out_minor = (u32)info.dwMinorVersion;
    }
#elif defined(__unix__) || defined(__APPLE__)
    struct utsname u;
    if (uname(&u) == 0) {
        parse_major_minor(u.release, out_major, out_minor);
    }
#else
    out_major = 0u;
    out_minor = 0u;
#endif
}

static u64 detect_ram_bytes(void) {
#if defined(_WIN32) || defined(_WIN64)
    MEMORYSTATUSEX st;
    std::memset(&st, 0, sizeof(st));
    st.dwLength = sizeof(st);
    if (GlobalMemoryStatusEx(&st)) {
        return (u64)st.ullTotalPhys;
    }
    return 0ull;
#elif defined(__unix__) || defined(__APPLE__)
    long pages = sysconf(_SC_PHYS_PAGES);
    long page_size = sysconf(_SC_PAGESIZE);
    if (pages <= 0 || page_size <= 0) {
        return 0ull;
    }
    return (u64)pages * (u64)page_size;
#else
    return 0ull;
#endif
}

static u32 ram_class_from_bytes(u64 bytes) {
    const u64 gb = 1024ull * 1024ull * 1024ull;
    if (bytes == 0ull) return LAUNCHER_CAPS_RAM_UNKNOWN;
    if (bytes < 4ull * gb) return LAUNCHER_CAPS_RAM_LT_4GB;
    if (bytes < 8ull * gb) return LAUNCHER_CAPS_RAM_4_8GB;
    if (bytes < 16ull * gb) return LAUNCHER_CAPS_RAM_8_16GB;
    if (bytes < 32ull * gb) return LAUNCHER_CAPS_RAM_16_32GB;
    return LAUNCHER_CAPS_RAM_32GB_PLUS;
}

static u32 detect_fs_perm_model(void) {
#if defined(_WIN32) || defined(_WIN64)
    return LAUNCHER_CAPS_FS_PERM_MIXED;
#else
    return LAUNCHER_CAPS_FS_PERM_USER;
#endif
}

static u32 detect_max_path_len(void) {
#if defined(_WIN32) || defined(_WIN64)
    return 260u;
#else
#ifdef PATH_MAX
    return (u32)PATH_MAX;
#else
    return 4096u;
#endif
#endif
}

static bool backend_less(const LauncherCapsBackend& a, const LauncherCapsBackend& b) {
    if (a.subsystem_id != b.subsystem_id) return a.subsystem_id < b.subsystem_id;
    if (a.backend_name != b.backend_name) return a.backend_name < b.backend_name;
    if (a.priority != b.priority) return a.priority < b.priority;
    if (a.determinism != b.determinism) return a.determinism < b.determinism;
    if (a.perf_class != b.perf_class) return a.perf_class < b.perf_class;
    return a.subsystem_name < b.subsystem_name;
}

static bool selection_less(const LauncherCapsSelection& a, const LauncherCapsSelection& b) {
    if (a.subsystem_id != b.subsystem_id) return a.subsystem_id < b.subsystem_id;
    if (a.backend_name != b.backend_name) return a.backend_name < b.backend_name;
    if (a.priority != b.priority) return a.priority < b.priority;
    if (a.determinism != b.determinism) return a.determinism < b.determinism;
    if (a.perf_class != b.perf_class) return a.perf_class < b.perf_class;
    return a.subsystem_name < b.subsystem_name;
}

static std::string det_grade_name(u32 g) {
    switch ((dom_det_grade)g) {
    case DOM_DET_D0_BIT_EXACT: return "D0";
    case DOM_DET_D1_TICK_EXACT: return "D1";
    default: break;
    }
    return "D2";
}

static std::string perf_class_name(u32 c) {
    switch ((dom_caps_perf_class)c) {
    case DOM_CAPS_PERF_BASELINE: return "baseline";
    case DOM_CAPS_PERF_COMPAT: return "compat";
    case DOM_CAPS_PERF_PERF: return "perf";
    default: break;
    }
    return "baseline";
}

static void tlv_add_backend(TlvWriter& w, const LauncherCapsBackend& b) {
    TlvWriter entry;
    entry.add_u32(LAUNCHER_CAPS_BACKEND_TLV_TAG_SUBSYS_ID, b.subsystem_id);
    entry.add_string(LAUNCHER_CAPS_BACKEND_TLV_TAG_SUBSYS_NAME, b.subsystem_name);
    entry.add_string(LAUNCHER_CAPS_BACKEND_TLV_TAG_BACKEND_NAME, b.backend_name);
    entry.add_u32(LAUNCHER_CAPS_BACKEND_TLV_TAG_DET_GRADE, b.determinism);
    entry.add_u32(LAUNCHER_CAPS_BACKEND_TLV_TAG_PERF_CLASS, b.perf_class);
    entry.add_u32(LAUNCHER_CAPS_BACKEND_TLV_TAG_PRIORITY, b.priority);
    w.add_container(LAUNCHER_CAPS_TLV_TAG_BACKEND, entry.bytes());
}

static void tlv_add_selection(TlvWriter& w, const LauncherCapsSelection& s) {
    TlvWriter entry;
    entry.add_u32(LAUNCHER_CAPS_SEL_TLV_TAG_SUBSYS_ID, s.subsystem_id);
    entry.add_string(LAUNCHER_CAPS_SEL_TLV_TAG_SUBSYS_NAME, s.subsystem_name);
    entry.add_string(LAUNCHER_CAPS_SEL_TLV_TAG_BACKEND_NAME, s.backend_name);
    entry.add_u32(LAUNCHER_CAPS_SEL_TLV_TAG_DET_GRADE, s.determinism);
    entry.add_u32(LAUNCHER_CAPS_SEL_TLV_TAG_PERF_CLASS, s.perf_class);
    entry.add_u32(LAUNCHER_CAPS_SEL_TLV_TAG_PRIORITY, s.priority);
    entry.add_u32(LAUNCHER_CAPS_SEL_TLV_TAG_OVERRIDE, s.chosen_by_override ? 1u : 0u);
    w.add_container(LAUNCHER_CAPS_TLV_TAG_SELECTED_BACKEND, entry.bytes());
}

} /* namespace */

LauncherCapsBackend::LauncherCapsBackend()
    : subsystem_id(0u),
      subsystem_name(),
      backend_name(),
      determinism(0u),
      perf_class(0u),
      priority(0u) {
}

LauncherCapsSelection::LauncherCapsSelection()
    : subsystem_id(0u),
      subsystem_name(),
      backend_name(),
      determinism(0u),
      perf_class(0u),
      priority(0u),
      chosen_by_override(0u) {
}

LauncherCapsSnapshot::LauncherCapsSnapshot()
    : schema_version(LAUNCHER_CAPS_TLV_VERSION),
      version_string(),
      build_id(),
      git_hash(),
      os_family(0u),
      os_version_major(0u),
      os_version_minor(0u),
      cpu_arch(0u),
      ram_class(LAUNCHER_CAPS_RAM_UNKNOWN),
      provider_net(0u),
      provider_trust(0u),
      provider_keychain(0u),
      provider_content(0u),
      supports_stdout_capture(0u),
      supports_file_picker(0u),
      supports_open_folder(0u),
      supports_tls(0u),
      fs_perm_model(LAUNCHER_CAPS_FS_PERM_UNKNOWN),
      max_path_len(0u),
      backends(),
      selections() {
}

bool launcher_caps_snapshot_build(const dom_profile* profile,
                                  LauncherCapsSnapshot& out_snapshot,
                                  std::string& out_error) {
    LauncherCapsSnapshot snap;
    dom_backend_desc desc;
    dom_hw_caps hw;
    dom_selection sel;
    dom_caps_result rc;
    dom_profile fallback;
    const dom_profile* used_profile = profile;
    u32 i;

    out_error.clear();

    snap.schema_version = LAUNCHER_CAPS_TLV_VERSION;
    snap.version_string = safe_str(dominium_get_launcher_version_string());
    snap.build_id = safe_str(dom_build_id());
    snap.git_hash = safe_str(dom_git_hash());

    if (snap.version_string.empty()) snap.version_string = "unknown";
    if (snap.build_id.empty()) snap.build_id = "unknown";
    if (snap.git_hash.empty()) snap.git_hash = "unknown";

    snap.os_family = (u32)dominium_detect_os_family();
    snap.cpu_arch = (u32)dominium_detect_arch();
    detect_os_version(snap.os_version_major, snap.os_version_minor);
    snap.ram_class = ram_class_from_bytes(detect_ram_bytes());
    snap.fs_perm_model = detect_fs_perm_model();
    snap.max_path_len = detect_max_path_len();

    snap.provider_net = 0u;
    snap.provider_trust = 0u;
    snap.provider_keychain = 0u;
    snap.provider_content = 0u;

    snap.supports_stdout_capture = 0u;
    snap.supports_file_picker = 0u;
    snap.supports_open_folder = 0u;
    snap.supports_tls = 0u;

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    std::memset(&desc, 0, sizeof(desc));
    for (i = 0u; i < dom_caps_backend_count(); ++i) {
        if (dom_caps_backend_get(i, &desc) != DOM_CAPS_OK) {
            continue;
        }
        {
            LauncherCapsBackend b;
            b.subsystem_id = (u32)desc.subsystem_id;
            b.subsystem_name = subsystem_name_or_hex(b.subsystem_id, desc.subsystem_name);
            b.backend_name = safe_str(desc.backend_name);
            b.determinism = (u32)desc.determinism;
            b.perf_class = (u32)desc.perf_class;
            b.priority = (u32)desc.backend_priority;
            snap.backends.push_back(b);
        }
    }
    std::sort(snap.backends.begin(), snap.backends.end(), backend_less);

    std::memset(&hw, 0, sizeof(hw));
    hw.abi_version = DOM_CAPS_ABI_VERSION;
    hw.struct_size = (u32)sizeof(hw);
    (void)dom_hw_caps_probe_host(&hw);

    std::memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = (u32)sizeof(sel);

    if (!used_profile) {
        std::memset(&fallback, 0, sizeof(fallback));
        fallback.abi_version = DOM_PROFILE_ABI_VERSION;
        fallback.struct_size = (u32)sizeof(fallback);
        fallback.kind = DOM_PROFILE_BASELINE;
        fallback.lockstep_strict = 0u;
        used_profile = &fallback;
    }

    rc = dom_caps_select(used_profile, &hw, &sel);
    if (rc != DOM_CAPS_OK) {
        out_error = "caps_select_failed";
        out_snapshot = snap;
        return false;
    }

    for (i = 0u; i < sel.entry_count; ++i) {
        const dom_selection_entry* e = &sel.entries[i];
        LauncherCapsSelection s;
        if (!e || !e->backend_name) {
            continue;
        }
        s.subsystem_id = (u32)e->subsystem_id;
        s.subsystem_name = subsystem_name_or_hex(s.subsystem_id, e->subsystem_name);
        s.backend_name = safe_str(e->backend_name);
        s.determinism = (u32)e->determinism;
        s.perf_class = (u32)e->perf_class;
        s.priority = (u32)e->backend_priority;
        s.chosen_by_override = e->chosen_by_override ? 1u : 0u;
        snap.selections.push_back(s);
    }
    std::sort(snap.selections.begin(), snap.selections.end(), selection_less);

    out_snapshot = snap;
    return true;
}

bool launcher_caps_snapshot_to_tlv_bytes(const LauncherCapsSnapshot& snapshot,
                                         std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_CAPS_TLV_VERSION);
    w.add_string(LAUNCHER_CAPS_TLV_TAG_VERSION_STRING, snapshot.version_string);
    w.add_string(LAUNCHER_CAPS_TLV_TAG_BUILD_ID, snapshot.build_id);
    w.add_string(LAUNCHER_CAPS_TLV_TAG_GIT_HASH, snapshot.git_hash);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_OS_FAMILY, snapshot.os_family);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_OS_VERSION_MAJOR, snapshot.os_version_major);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_OS_VERSION_MINOR, snapshot.os_version_minor);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_CPU_ARCH, snapshot.cpu_arch);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_RAM_CLASS, snapshot.ram_class);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_PROVIDER_NET, snapshot.provider_net);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_PROVIDER_TRUST, snapshot.provider_trust);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_PROVIDER_KEYCHAIN, snapshot.provider_keychain);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_PROVIDER_CONTENT, snapshot.provider_content);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_SUPPORTS_STDOUT_CAPTURE, snapshot.supports_stdout_capture);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_SUPPORTS_FILE_PICKER, snapshot.supports_file_picker);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_SUPPORTS_OPEN_FOLDER, snapshot.supports_open_folder);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_SUPPORTS_TLS, snapshot.supports_tls);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_FS_PERM_MODEL, snapshot.fs_perm_model);
    w.add_u32(LAUNCHER_CAPS_TLV_TAG_MAX_PATH_LEN, snapshot.max_path_len);

    for (i = 0u; i < snapshot.backends.size(); ++i) {
        tlv_add_backend(w, snapshot.backends[i]);
    }
    for (i = 0u; i < snapshot.selections.size(); ++i) {
        tlv_add_selection(w, snapshot.selections[i]);
    }

    out_bytes = w.bytes();
    return true;
}

std::string launcher_caps_snapshot_to_text(const LauncherCapsSnapshot& snapshot) {
    std::ostringstream oss;
    size_t i;

    oss << "caps.schema_version=" << (u32)LAUNCHER_CAPS_TLV_VERSION << "\n";
    oss << "caps.version_string=" << snapshot.version_string << "\n";
    oss << "caps.build_id=" << snapshot.build_id << "\n";
    oss << "caps.git_hash=" << snapshot.git_hash << "\n";
    oss << "caps.os.family=" << snapshot.os_family << "\n";
    oss << "caps.os.version_major=" << snapshot.os_version_major << "\n";
    oss << "caps.os.version_minor=" << snapshot.os_version_minor << "\n";
    oss << "caps.cpu.arch=" << snapshot.cpu_arch << "\n";
    oss << "caps.ram.class=" << snapshot.ram_class << "\n";
    oss << "caps.provider.net=" << snapshot.provider_net << "\n";
    oss << "caps.provider.trust=" << snapshot.provider_trust << "\n";
    oss << "caps.provider.keychain=" << snapshot.provider_keychain << "\n";
    oss << "caps.provider.content=" << snapshot.provider_content << "\n";
    oss << "caps.supports.stdout_capture=" << snapshot.supports_stdout_capture << "\n";
    oss << "caps.supports.file_picker=" << snapshot.supports_file_picker << "\n";
    oss << "caps.supports.open_folder=" << snapshot.supports_open_folder << "\n";
    oss << "caps.supports.tls=" << snapshot.supports_tls << "\n";
    oss << "caps.fs_perm_model=" << snapshot.fs_perm_model << "\n";
    oss << "caps.max_path_len=" << snapshot.max_path_len << "\n";

    oss << "caps.backends.count=" << (u32)snapshot.backends.size() << "\n";
    for (i = 0u; i < snapshot.backends.size(); ++i) {
        const LauncherCapsBackend& b = snapshot.backends[i];
        oss << "caps.backends[" << (u32)i << "].subsystem_id=" << b.subsystem_id << "\n";
        oss << "caps.backends[" << (u32)i << "].subsystem_name=" << b.subsystem_name << "\n";
        oss << "caps.backends[" << (u32)i << "].backend_name=" << b.backend_name << "\n";
        oss << "caps.backends[" << (u32)i << "].determinism=" << det_grade_name(b.determinism) << "\n";
        oss << "caps.backends[" << (u32)i << "].perf_class=" << perf_class_name(b.perf_class) << "\n";
        oss << "caps.backends[" << (u32)i << "].priority=" << b.priority << "\n";
    }

    oss << "caps.selection.count=" << (u32)snapshot.selections.size() << "\n";
    for (i = 0u; i < snapshot.selections.size(); ++i) {
        const LauncherCapsSelection& s = snapshot.selections[i];
        oss << "caps.selection[" << (u32)i << "].subsystem_id=" << s.subsystem_id << "\n";
        oss << "caps.selection[" << (u32)i << "].subsystem_name=" << s.subsystem_name << "\n";
        oss << "caps.selection[" << (u32)i << "].backend_name=" << s.backend_name << "\n";
        oss << "caps.selection[" << (u32)i << "].determinism=" << det_grade_name(s.determinism) << "\n";
        oss << "caps.selection[" << (u32)i << "].perf_class=" << perf_class_name(s.perf_class) << "\n";
        oss << "caps.selection[" << (u32)i << "].priority=" << s.priority << "\n";
        oss << "caps.selection[" << (u32)i << "].override=" << (s.chosen_by_override ? 1u : 0u) << "\n";
    }

    return oss.str();
}

static bool write_bytes_to_file(const std::string& path, const std::vector<unsigned char>& bytes) {
    FILE* f = std::fopen(path.c_str(), "wb");
    size_t wrote = 0u;
    if (!f) {
        return false;
    }
    if (!bytes.empty()) {
        wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
    }
    std::fclose(f);
    return wrote == bytes.size();
}

bool launcher_caps_snapshot_write_tlv(const LauncherCapsSnapshot& snapshot,
                                      const std::string& path,
                                      std::string& out_error) {
    std::vector<unsigned char> bytes;
    out_error.clear();
    if (!launcher_caps_snapshot_to_tlv_bytes(snapshot, bytes)) {
        out_error = "caps_tlv_encode_failed";
        return false;
    }
    if (!write_bytes_to_file(path, bytes)) {
        out_error = "caps_tlv_write_failed";
        return false;
    }
    return true;
}

bool launcher_caps_snapshot_write_text(const LauncherCapsSnapshot& snapshot,
                                       const std::string& path,
                                       std::string& out_error) {
    std::string txt = launcher_caps_snapshot_to_text(snapshot);
    std::vector<unsigned char> bytes(txt.begin(), txt.end());
    out_error.clear();
    if (!write_bytes_to_file(path, bytes)) {
        out_error = "caps_text_write_failed";
        return false;
    }
    return true;
}

} /* namespace dom */

