/*
FILE: source/dominium/launcher/core/src/selection/launcher_selection_summary.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / selection_summary
RESPONSIBILITY: Implements selection summary TLV persistence and stable text rendering.
*/

#include "launcher_selection_summary.h"

#include <sstream>
#include <cstring>
#include <algorithm>

#include "launcher_tlv.h"
#include "dominium/core_caps.h"
#include "dominium/core_solver.h"

namespace dom {
namespace launcher_core {

namespace {
enum {
    TAG_RUN_ID = 2u,
    TAG_INSTANCE_ID = 3u,
    TAG_LAUNCHER_PROFILE_ID = 4u,
    TAG_DETERMINISM_PROFILE_ID = 5u,
    TAG_OFFLINE_MODE = 6u,
    TAG_SAFE_MODE = 7u,
    TAG_MANIFEST_HASH64 = 8u,
    TAG_MANIFEST_HASH_BYTES = 9u,
    TAG_UI_BACKEND = 10u,
    TAG_PLATFORM_BACKEND = 11u,
    TAG_RENDERER_BACKEND = 12u,
    TAG_RESOLVED_PACKS_COUNT = 13u,
    TAG_RESOLVED_PACKS_SUMMARY = 14u,
    TAG_PROVIDER_BACKEND = 15u,
    TAG_EFFECTIVE_CAPS_TLV = 16u,
    TAG_EXPLANATION_TLV = 17u
};

enum {
    TAG_B_BACKEND_ID = 1u,
    TAG_B_WHY = 2u
};

enum {
    TAG_P_TYPE = 1u,
    TAG_P_ID = 2u,
    TAG_P_WHY = 3u
};

static std::string hex_lower(const unsigned char* p, size_t n) {
    static const char* hex = "0123456789abcdef";
    std::string out;
    size_t i;
    out.reserve(n * 2u);
    for (i = 0u; i < n; ++i) {
        const unsigned char b = p[i];
        out.push_back(hex[(b >> 4u) & 0xFu]);
        out.push_back(hex[b & 0xFu]);
    }
    return out;
}

static std::string u64_hex16_string(u64 v) {
    static const char* hex = "0123456789abcdef";
    char buf[17];
    int i;
    for (i = 0; i < 16; ++i) {
        const unsigned shift = (unsigned)((15 - i) * 4);
        const unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        buf[i] = hex[nib & 0xFu];
    }
    buf[16] = '\0';
    return std::string(buf);
}

static std::string cap_value_to_string(u32 key_id, u8 type, const core_cap_value& v) {
    std::ostringstream oss;
    switch (type) {
    case CORE_CAP_BOOL:
        oss << (v.bool_value ? 1u : 0u);
        break;
    case CORE_CAP_U32:
        oss << v.u32_value;
        break;
    case CORE_CAP_I32:
        oss << v.i32_value;
        break;
    case CORE_CAP_U64:
        oss << v.u64_value;
        break;
    case CORE_CAP_I64:
        oss << v.i64_value;
        break;
    case CORE_CAP_STRING_ID:
        oss << v.string_id;
        break;
    case CORE_CAP_ENUM_ID: {
        const char* tok = core_caps_enum_token(key_id, v.enum_id);
        if (tok && std::strcmp(tok, "unknown") != 0) {
            oss << tok;
        } else {
            oss << v.enum_id;
        }
        break;
    }
    case CORE_CAP_RANGE_U32:
        oss << v.range_u32.min_value << ".." << v.range_u32.max_value;
        break;
    default:
        break;
    }
    return oss.str();
}

static bool solver_selected_less(const core_solver_selected& a, const core_solver_selected& b) {
    if (a.category_id != b.category_id) {
        return a.category_id < b.category_id;
    }
    return std::strcmp(a.component_id, b.component_id) < 0;
}

static bool solver_reject_less(const core_solver_reject& a, const core_solver_reject& b) {
    if (a.category_id != b.category_id) {
        return a.category_id < b.category_id;
    }
    return std::strcmp(a.component_id, b.component_id) < 0;
}

static void tlv_add_choice(TlvWriter& w, u32 tag, const LauncherSelectionBackendChoice& c) {
    TlvWriter entry;
    entry.add_string(TAG_B_BACKEND_ID, c.backend_id);
    entry.add_string(TAG_B_WHY, c.why);
    w.add_container(tag, entry.bytes());
}

static void tlv_read_choice(const unsigned char* data, size_t size, LauncherSelectionBackendChoice& out_c) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherSelectionBackendChoice c;
    while (r.next(rec)) {
        if (rec.tag == TAG_B_BACKEND_ID) {
            c.backend_id = tlv_read_string(rec.payload, rec.len);
        } else if (rec.tag == TAG_B_WHY) {
            c.why = tlv_read_string(rec.payload, rec.len);
        } else {
            /* skip unknown */
        }
    }
    out_c = c;
}

static void tlv_add_provider(TlvWriter& w, u32 tag, const LauncherSelectionProviderChoice& c) {
    TlvWriter entry;
    entry.add_string(TAG_P_TYPE, c.provider_type);
    entry.add_string(TAG_P_ID, c.provider_id);
    entry.add_string(TAG_P_WHY, c.why);
    w.add_container(tag, entry.bytes());
}

static void tlv_read_provider(const unsigned char* data, size_t size, LauncherSelectionProviderChoice& out_c) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherSelectionProviderChoice c;
    while (r.next(rec)) {
        if (rec.tag == TAG_P_TYPE) {
            c.provider_type = tlv_read_string(rec.payload, rec.len);
        } else if (rec.tag == TAG_P_ID) {
            c.provider_id = tlv_read_string(rec.payload, rec.len);
        } else if (rec.tag == TAG_P_WHY) {
            c.why = tlv_read_string(rec.payload, rec.len);
        } else {
            /* skip unknown */
        }
    }
    out_c = c;
}
}

LauncherSelectionBackendChoice::LauncherSelectionBackendChoice()
    : backend_id(),
      why() {
}

LauncherSelectionProviderChoice::LauncherSelectionProviderChoice()
    : provider_type(),
      provider_id(),
      why() {
}

LauncherSelectionSummary::LauncherSelectionSummary()
    : schema_version(LAUNCHER_SELECTION_SUMMARY_TLV_VERSION),
      run_id(0ull),
      instance_id(),
      launcher_profile_id(),
      determinism_profile_id(),
      offline_mode(0u),
      safe_mode(0u),
      manifest_hash64(0ull),
      manifest_hash_bytes(),
      ui_backend(),
      platform_backends(),
      renderer_backends(),
      provider_backends(),
      resolved_packs_count(0u),
      resolved_packs_summary(),
      effective_caps_tlv(),
      explanation_tlv() {
}

bool launcher_selection_summary_to_tlv_bytes(const LauncherSelectionSummary& s,
                                             std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_SELECTION_SUMMARY_TLV_VERSION);
    w.add_u64(TAG_RUN_ID, s.run_id);
    w.add_string(TAG_INSTANCE_ID, s.instance_id);
    w.add_string(TAG_LAUNCHER_PROFILE_ID, s.launcher_profile_id);
    w.add_string(TAG_DETERMINISM_PROFILE_ID, s.determinism_profile_id);
    w.add_u32(TAG_OFFLINE_MODE, s.offline_mode ? 1u : 0u);
    w.add_u32(TAG_SAFE_MODE, s.safe_mode ? 1u : 0u);
    w.add_u64(TAG_MANIFEST_HASH64, s.manifest_hash64);
    if (!s.manifest_hash_bytes.empty()) {
        w.add_bytes(TAG_MANIFEST_HASH_BYTES, &s.manifest_hash_bytes[0], (u32)s.manifest_hash_bytes.size());
    }

    tlv_add_choice(w, TAG_UI_BACKEND, s.ui_backend);
    for (i = 0u; i < s.platform_backends.size(); ++i) {
        tlv_add_choice(w, TAG_PLATFORM_BACKEND, s.platform_backends[i]);
    }
    for (i = 0u; i < s.renderer_backends.size(); ++i) {
        tlv_add_choice(w, TAG_RENDERER_BACKEND, s.renderer_backends[i]);
    }
    for (i = 0u; i < s.provider_backends.size(); ++i) {
        tlv_add_provider(w, TAG_PROVIDER_BACKEND, s.provider_backends[i]);
    }

    w.add_u32(TAG_RESOLVED_PACKS_COUNT, s.resolved_packs_count);
    w.add_string(TAG_RESOLVED_PACKS_SUMMARY, s.resolved_packs_summary);
    if (!s.effective_caps_tlv.empty()) {
        w.add_bytes(TAG_EFFECTIVE_CAPS_TLV, &s.effective_caps_tlv[0], (u32)s.effective_caps_tlv.size());
    }
    if (!s.explanation_tlv.empty()) {
        w.add_bytes(TAG_EXPLANATION_TLV, &s.explanation_tlv[0], (u32)s.explanation_tlv.size());
    }

    out_bytes = w.bytes();
    return true;
}

bool launcher_selection_summary_from_tlv_bytes(const unsigned char* data,
                                               size_t size,
                                               LauncherSelectionSummary& out_s) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;

    out_s = LauncherSelectionSummary();
    if (!tlv_read_schema_version_or_default(data, size, version, LAUNCHER_SELECTION_SUMMARY_TLV_VERSION)) {
        return false;
    }
    if (version != LAUNCHER_SELECTION_SUMMARY_TLV_VERSION) {
        return false;
    }

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case TAG_RUN_ID: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) out_s.run_id = v;
            break;
        }
        case TAG_INSTANCE_ID:
            out_s.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_LAUNCHER_PROFILE_ID:
            out_s.launcher_profile_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_DETERMINISM_PROFILE_ID:
            out_s.determinism_profile_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_OFFLINE_MODE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.offline_mode = v ? 1u : 0u;
            break;
        }
        case TAG_SAFE_MODE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.safe_mode = v ? 1u : 0u;
            break;
        }
        case TAG_MANIFEST_HASH64: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) out_s.manifest_hash64 = v;
            break;
        }
        case TAG_MANIFEST_HASH_BYTES:
            out_s.manifest_hash_bytes.assign(rec.payload, rec.payload + (size_t)rec.len);
            break;
        case TAG_UI_BACKEND: {
            LauncherSelectionBackendChoice c;
            tlv_read_choice(rec.payload, (size_t)rec.len, c);
            out_s.ui_backend = c;
            break;
        }
        case TAG_PLATFORM_BACKEND: {
            LauncherSelectionBackendChoice c;
            tlv_read_choice(rec.payload, (size_t)rec.len, c);
            out_s.platform_backends.push_back(c);
            break;
        }
        case TAG_RENDERER_BACKEND: {
            LauncherSelectionBackendChoice c;
            tlv_read_choice(rec.payload, (size_t)rec.len, c);
            out_s.renderer_backends.push_back(c);
            break;
        }
        case TAG_PROVIDER_BACKEND: {
            LauncherSelectionProviderChoice c;
            tlv_read_provider(rec.payload, (size_t)rec.len, c);
            out_s.provider_backends.push_back(c);
            break;
        }
        case TAG_RESOLVED_PACKS_COUNT: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) out_s.resolved_packs_count = v;
            break;
        }
        case TAG_RESOLVED_PACKS_SUMMARY:
            out_s.resolved_packs_summary = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_EFFECTIVE_CAPS_TLV:
            out_s.effective_caps_tlv.assign(rec.payload, rec.payload + (size_t)rec.len);
            break;
        case TAG_EXPLANATION_TLV:
            out_s.explanation_tlv.assign(rec.payload, rec.payload + (size_t)rec.len);
            break;
        default:
            /* skip unknown */
            break;
        }
    }
    return true;
}

std::string launcher_selection_summary_to_text(const LauncherSelectionSummary& s) {
    std::ostringstream oss;
    size_t i;

    oss << "selection_summary.schema_version=" << (u32)LAUNCHER_SELECTION_SUMMARY_TLV_VERSION << "\n";
    oss << "selection_summary.run_id=0x" << u64_hex16_string(s.run_id) << "\n";
    oss << "selection_summary.instance_id=" << s.instance_id << "\n";

    oss << "selection_summary.profile_id=" << s.launcher_profile_id << "\n";
    oss << "selection_summary.determinism_profile_id=" << s.determinism_profile_id << "\n";

    oss << "selection_summary.offline_mode=" << (s.offline_mode ? "1" : "0") << "\n";
    oss << "selection_summary.safe_mode=" << (s.safe_mode ? "1" : "0") << "\n";

    if (s.manifest_hash64 != 0ull) {
        const std::string full = u64_hex16_string(s.manifest_hash64);
        oss << "selection_summary.manifest_hash64=0x" << full << "\n";
        oss << "selection_summary.manifest_hash64_short=0x" << full.substr(0u, 8u) << "\n";
    } else {
        oss << "selection_summary.manifest_hash64=0x0000000000000000\n";
        oss << "selection_summary.manifest_hash64_short=0x00000000\n";
    }

    if (!s.manifest_hash_bytes.empty()) {
        const std::string hex = hex_lower(&s.manifest_hash_bytes[0], s.manifest_hash_bytes.size());
        oss << "selection_summary.manifest_sha256_hex=" << hex << "\n";
        oss << "selection_summary.manifest_sha256_short=" << hex.substr(0u, 8u) << "\n";
    } else {
        oss << "selection_summary.manifest_sha256_hex=\n";
        oss << "selection_summary.manifest_sha256_short=\n";
    }

    oss << "selection_summary.backends.ui.id=" << s.ui_backend.backend_id << "\n";
    oss << "selection_summary.backends.ui.why=" << s.ui_backend.why << "\n";

    oss << "selection_summary.backends.platform.count=" << (u32)s.platform_backends.size() << "\n";
    for (i = 0u; i < s.platform_backends.size(); ++i) {
        oss << "selection_summary.backends.platform[" << (u32)i << "].id=" << s.platform_backends[i].backend_id << "\n";
        oss << "selection_summary.backends.platform[" << (u32)i << "].why=" << s.platform_backends[i].why << "\n";
    }

    oss << "selection_summary.backends.renderer.count=" << (u32)s.renderer_backends.size() << "\n";
    for (i = 0u; i < s.renderer_backends.size(); ++i) {
        oss << "selection_summary.backends.renderer[" << (u32)i << "].id=" << s.renderer_backends[i].backend_id << "\n";
        oss << "selection_summary.backends.renderer[" << (u32)i << "].why=" << s.renderer_backends[i].why << "\n";
    }

    oss << "selection_summary.providers.count=" << (u32)s.provider_backends.size() << "\n";
    for (i = 0u; i < s.provider_backends.size(); ++i) {
        oss << "selection_summary.providers[" << (u32)i << "].type=" << s.provider_backends[i].provider_type << "\n";
        oss << "selection_summary.providers[" << (u32)i << "].id=" << s.provider_backends[i].provider_id << "\n";
        oss << "selection_summary.providers[" << (u32)i << "].why=" << s.provider_backends[i].why << "\n";
    }

    oss << "selection_summary.packs.resolved.count=" << s.resolved_packs_count << "\n";
    oss << "selection_summary.packs.resolved.order=" << s.resolved_packs_summary << "\n";

    if (s.effective_caps_tlv.empty()) {
        oss << "selection_summary.effective_caps.count=0\n";
    } else {
        core_caps caps;
        u32 used = 0u;
        if (core_caps_read_tlv(s.effective_caps_tlv.empty() ? (const unsigned char*)0 : &s.effective_caps_tlv[0],
                               (u32)s.effective_caps_tlv.size(),
                               &caps,
                               &used) != 0) {
            oss << "selection_summary.effective_caps.decode_failed=1\n";
            oss << "selection_summary.effective_caps.count=0\n";
        } else {
            oss << "selection_summary.effective_caps.count=" << caps.count << "\n";
            for (i = 0u; i < caps.count; ++i) {
                const core_cap_entry& e = caps.entries[i];
                oss << "selection_summary.effective_caps[" << (u32)i << "].key=" << core_caps_key_token(e.key_id) << "\n";
                oss << "selection_summary.effective_caps[" << (u32)i << "].type=" << core_caps_type_token(e.type) << "\n";
                oss << "selection_summary.effective_caps[" << (u32)i << "].value=" << cap_value_to_string(e.key_id, e.type, e.v) << "\n";
            }
        }
    }

    if (s.explanation_tlv.empty()) {
        oss << "selection_summary.explain.ok=0\n";
        oss << "selection_summary.explain.selected.count=0\n";
        oss << "selection_summary.explain.rejected.count=0\n";
    } else {
        core_solver_result explain;
        u32 used = 0u;
        if (core_solver_explain_read_tlv(s.explanation_tlv.empty() ? (const unsigned char*)0 : &s.explanation_tlv[0],
                                         (u32)s.explanation_tlv.size(),
                                         &explain,
                                         &used) != 0) {
            oss << "selection_summary.explain.decode_failed=1\n";
            oss << "selection_summary.explain.ok=0\n";
            oss << "selection_summary.explain.selected.count=0\n";
            oss << "selection_summary.explain.rejected.count=0\n";
        } else {
            std::vector<core_solver_selected> selected;
            std::vector<core_solver_reject> rejected;
            selected.assign(explain.selected, explain.selected + explain.selected_count);
            rejected.assign(explain.rejected, explain.rejected + explain.rejected_count);
            std::sort(selected.begin(), selected.end(), solver_selected_less);
            std::sort(rejected.begin(), rejected.end(), solver_reject_less);

            oss << "selection_summary.explain.ok=" << (explain.ok ? "1" : "0") << "\n";
            oss << "selection_summary.explain.fail_reason=" << core_solver_fail_reason_token(explain.fail_reason) << "\n";
            oss << "selection_summary.explain.fail_category=" << core_solver_category_token(explain.fail_category) << "\n";
            oss << "selection_summary.explain.selected.count=" << (u32)selected.size() << "\n";
            for (i = 0u; i < selected.size(); ++i) {
                const core_solver_selected& ssel = selected[i];
                oss << "selection_summary.explain.selected[" << (u32)i << "].category=" << core_solver_category_token(ssel.category_id) << "\n";
                oss << "selection_summary.explain.selected[" << (u32)i << "].component=" << ssel.component_id << "\n";
                oss << "selection_summary.explain.selected[" << (u32)i << "].reason=" << core_solver_select_reason_token(ssel.reason) << "\n";
                oss << "selection_summary.explain.selected[" << (u32)i << "].score=" << ssel.score << "\n";
                oss << "selection_summary.explain.selected[" << (u32)i << "].priority=" << ssel.priority << "\n";
                oss << "selection_summary.explain.selected[" << (u32)i << "].prefers_satisfied=" << ssel.prefers_satisfied << "\n";
            }

            oss << "selection_summary.explain.rejected.count=" << (u32)rejected.size() << "\n";
            for (i = 0u; i < rejected.size(); ++i) {
                const core_solver_reject& rj = rejected[i];
                oss << "selection_summary.explain.rejected[" << (u32)i << "].category=" << core_solver_category_token(rj.category_id) << "\n";
                oss << "selection_summary.explain.rejected[" << (u32)i << "].component=" << rj.component_id << "\n";
                oss << "selection_summary.explain.rejected[" << (u32)i << "].reason=" << core_solver_reject_reason_token(rj.reason) << "\n";
                if (rj.constraint.key_id != 0u) {
                    oss << "selection_summary.explain.rejected[" << (u32)i << "].constraint.key=" << core_caps_key_token(rj.constraint.key_id) << "\n";
                    oss << "selection_summary.explain.rejected[" << (u32)i << "].constraint.op=" << core_solver_op_token(rj.constraint.op) << "\n";
                    oss << "selection_summary.explain.rejected[" << (u32)i << "].constraint.type=" << core_caps_type_token(rj.constraint.type) << "\n";
                    oss << "selection_summary.explain.rejected[" << (u32)i << "].constraint.value=" << cap_value_to_string(rj.constraint.key_id, rj.constraint.type, rj.constraint.value) << "\n";
                }
                if (rj.actual_present) {
                    oss << "selection_summary.explain.rejected[" << (u32)i << "].actual.type=" << core_caps_type_token(rj.actual_type) << "\n";
                    oss << "selection_summary.explain.rejected[" << (u32)i << "].actual.value=" << cap_value_to_string(rj.constraint.key_id, rj.actual_type, rj.actual_value) << "\n";
                }
                if (rj.conflict_component_id[0]) {
                    oss << "selection_summary.explain.rejected[" << (u32)i << "].conflict=" << rj.conflict_component_id << "\n";
                }
            }
        }
    }

    return oss.str();
}

std::string launcher_selection_summary_to_compact_line(const LauncherSelectionSummary& s) {
    std::ostringstream oss;

    oss << "profile=" << s.launcher_profile_id;
    oss << " det=" << s.determinism_profile_id;
    oss << " ui=" << s.ui_backend.backend_id;
    oss << " gfx=";
    if (!s.renderer_backends.empty()) {
        oss << s.renderer_backends[0].backend_id;
    } else {
        oss << "null";
    }
    oss << " offline=" << (s.offline_mode ? "1" : "0");
    oss << " safe=" << (s.safe_mode ? "1" : "0");
    if (s.manifest_hash64 != 0ull) {
        oss << " manifest=" << u64_hex16_string(s.manifest_hash64).substr(0u, 8u);
    } else {
        oss << " manifest=00000000";
    }
    if (!s.resolved_packs_summary.empty()) {
        oss << " packs=" << s.resolved_packs_summary;
    } else {
        oss << " packs=";
    }
    return oss.str();
}

} /* namespace launcher_core */
} /* namespace dom */

