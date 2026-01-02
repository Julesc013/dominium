/*
FILE: source/dominium/launcher/launcher_caps_solver.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / caps_solver
RESPONSIBILITY: Adapts legacy caps registry to core_caps + core_solver with explainable output.
*/
#include "launcher_caps_solver.h"

#include <algorithm>
#include <cstring>

extern "C" {
#include "domino/caps.h"
#include "dominium/product_info.h"
#include "dominium/provider_registry.h"
}

namespace dom {

namespace {

struct ScoreContext {
    dom_profile_kind profile_kind;
};

struct ComponentStore {
    core_solver_component_desc desc;
    dom_backend_desc backend;
    std::vector<core_cap_entry> provides;
    std::vector<core_solver_constraint> requires;
    std::vector<core_solver_constraint> forbids;
    std::vector<core_solver_constraint> prefers;
    std::vector<const char*> conflicts;
};

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

static int ascii_tolower(int c) {
    if (c >= 'A' && c <= 'Z') {
        return c - 'A' + 'a';
    }
    return c;
}

static bool str_ieq(const char* a, const char* b) {
    if (!a || !b) {
        return false;
    }
    while (*a && *b) {
        int ca = ascii_tolower((unsigned char)*a);
        int cb = ascii_tolower((unsigned char)*b);
        if (ca != cb) {
            return false;
        }
        ++a;
        ++b;
    }
    return (*a == '\0' && *b == '\0');
}

static void profile_remove_override(dom_profile& p, const char* subsystem_key) {
    u32 i;
    u32 out = 0u;
    if (!subsystem_key || !subsystem_key[0]) {
        return;
    }
    for (i = 0u; i < p.override_count && i < (u32)DOM_PROFILE_MAX_OVERRIDES; ++i) {
        dom_profile_override* ov = &p.overrides[i];
        if (str_ieq(ov->subsystem_key, subsystem_key)) {
            continue;
        }
        if (out != i) {
            p.overrides[out] = p.overrides[i];
        }
        ++out;
    }
    p.override_count = out;
    for (; out < (u32)DOM_PROFILE_MAX_OVERRIDES; ++out) {
        std::memset(&p.overrides[out], 0, sizeof(p.overrides[out]));
    }
}

static bool profile_is_valid(const dom_profile* p) {
    if (!p) {
        return false;
    }
    if (p->abi_version != DOM_PROFILE_ABI_VERSION) {
        return false;
    }
    if (p->struct_size != (u32)sizeof(dom_profile)) {
        return false;
    }
    return true;
}

static bool profile_requests_gfx_null(const dom_profile* p) {
    u32 i;
    if (!p) {
        return false;
    }
    if (p->preferred_gfx_backend[0] && str_ieq(p->preferred_gfx_backend, "null")) {
        return true;
    }
    for (i = 0u; i < p->override_count && i < (u32)DOM_PROFILE_MAX_OVERRIDES; ++i) {
        const dom_profile_override* ov = &p->overrides[i];
        if (str_ieq(ov->subsystem_key, "gfx") && ov->backend_name[0] && str_ieq(ov->backend_name, "null")) {
            return true;
        }
    }
    return false;
}

static u32 core_os_family_from_dom(DomOSFamily fam) {
    switch (fam) {
    case DOM_OSFAM_WIN_NT:
    case DOM_OSFAM_WIN_9X:
    case DOM_OSFAM_WIN_3X:
    case DOM_OSFAM_DOS:
        return CORE_CAP_OS_WIN32;
    case DOM_OSFAM_MAC_OS_X:
    case DOM_OSFAM_MAC_CLASSIC:
        return CORE_CAP_OS_APPLE;
    case DOM_OSFAM_LINUX:
    case DOM_OSFAM_ANDROID:
    case DOM_OSFAM_CPM:
        return CORE_CAP_OS_UNIX;
    default:
        break;
    }
    return CORE_CAP_OS_UNKNOWN;
}

static u32 core_arch_from_dom(DomArch arch) {
    switch (arch) {
    case DOM_ARCH_X86_32: return CORE_CAP_ARCH_X86_32;
    case DOM_ARCH_X86_64: return CORE_CAP_ARCH_X86_64;
    case DOM_ARCH_ARM_32: return CORE_CAP_ARCH_ARM_32;
    case DOM_ARCH_ARM_64: return CORE_CAP_ARCH_ARM_64;
    default:
        break;
    }
    return CORE_CAP_ARCH_UNKNOWN;
}

static void build_host_caps(core_caps& out_caps) {
    dom_hw_caps hw;
    const DomOSFamily os_family = dominium_detect_os_family();
    const DomArch arch = dominium_detect_arch();

    core_caps_clear(&out_caps);

    (void)core_caps_set_enum(&out_caps, CORE_CAP_KEY_OS_FAMILY, core_os_family_from_dom(os_family));
    (void)core_caps_set_enum(&out_caps, CORE_CAP_KEY_CPU_ARCH, core_arch_from_dom(arch));

    std::memset(&hw, 0, sizeof(hw));
    hw.abi_version = DOM_CAPS_ABI_VERSION;
    hw.struct_size = (u32)sizeof(hw);
    (void)dom_hw_caps_probe_host(&hw);

    (void)core_caps_set_bool(&out_caps, CORE_CAP_KEY_OS_IS_WIN32, (hw.os_flags & DOM_HW_OS_WIN32) ? 1u : 0u);
    (void)core_caps_set_bool(&out_caps, CORE_CAP_KEY_OS_IS_UNIX, (hw.os_flags & DOM_HW_OS_UNIX) ? 1u : 0u);
    (void)core_caps_set_bool(&out_caps, CORE_CAP_KEY_OS_IS_APPLE, (hw.os_flags & DOM_HW_OS_APPLE) ? 1u : 0u);

#if defined(_WIN32) || defined(_WIN64)
    (void)core_caps_set_enum(&out_caps, CORE_CAP_KEY_FS_PERMISSIONS_MODEL, CORE_CAP_FS_PERM_MIXED);
#else
    (void)core_caps_set_enum(&out_caps, CORE_CAP_KEY_FS_PERMISSIONS_MODEL, CORE_CAP_FS_PERM_USER);
#endif
    (void)core_caps_set_bool(&out_caps, CORE_CAP_KEY_SUPPORTS_CLI, 1u);
}

static u32 category_from_subsystem(dom_subsystem_id sid) {
    if (sid == DOM_SUBSYS_DSYS) return CORE_SOLVER_CAT_PLATFORM;
    if (sid == DOM_SUBSYS_DGFX) return CORE_SOLVER_CAT_RENDERER;
    if (sid == DOM_SUBSYS_DUI) return CORE_SOLVER_CAT_UI;
    return CORE_SOLVER_CAT_NONE;
}

static const char* provider_type_from_category(u32 category_id) {
    switch (category_id) {
    case CORE_SOLVER_CAT_PROVIDER_NET: return "net";
    case CORE_SOLVER_CAT_PROVIDER_TRUST: return "trust";
    case CORE_SOLVER_CAT_PROVIDER_KEYCHAIN: return "keychain";
    case CORE_SOLVER_CAT_PROVIDER_CONTENT: return "content";
    case CORE_SOLVER_CAT_PROVIDER_OS_INTEGRATION: return "os_integration";
    default:
        break;
    }
    return "";
}

static core_cap_entry make_cap_u32(u32 key_id, u32 value) {
    core_cap_entry e;
    std::memset(&e, 0, sizeof(e));
    e.key_id = key_id;
    e.type = (u8)CORE_CAP_U32;
    e.v.u32_value = value;
    return e;
}

static core_cap_entry make_cap_enum(u32 key_id, u32 value) {
    core_cap_entry e;
    std::memset(&e, 0, sizeof(e));
    e.key_id = key_id;
    e.type = (u8)CORE_CAP_ENUM_ID;
    e.v.enum_id = value;
    return e;
}

static u32 det_grade_from_dom(dom_det_grade g) {
    switch (g) {
    case DOM_DET_D0_BIT_EXACT: return CORE_CAP_DET_D0_BIT_EXACT;
    case DOM_DET_D1_TICK_EXACT: return CORE_CAP_DET_D1_TICK_EXACT;
    default:
        break;
    }
    return CORE_CAP_DET_D2_BEST_EFFORT;
}

static u32 perf_class_from_dom(dom_caps_perf_class c) {
    switch (c) {
    case DOM_CAPS_PERF_COMPAT: return CORE_CAP_PERF_COMPAT;
    case DOM_CAPS_PERF_PERF: return CORE_CAP_PERF_PERF;
    default:
        break;
    }
    return CORE_CAP_PERF_BASELINE;
}

static void add_require_bool(std::vector<core_solver_constraint>& out, u32 key_id, u32 value) {
    core_solver_constraint c;
    std::memset(&c, 0, sizeof(c));
    c.key_id = key_id;
    c.op = (u8)CORE_SOLVER_OP_EQ;
    c.type = (u8)CORE_CAP_BOOL;
    c.value.u32_value = value;
    out.push_back(c);
}

static void add_require_enum(std::vector<core_solver_constraint>& out, u32 key_id, u32 value) {
    core_solver_constraint c;
    std::memset(&c, 0, sizeof(c));
    c.key_id = key_id;
    c.op = (u8)CORE_SOLVER_OP_EQ;
    c.type = (u8)CORE_CAP_ENUM_ID;
    c.value.enum_id = value;
    out.push_back(c);
}

static u32 caps_perf_score(dom_profile_kind profile_kind, u32 perf_class) {
    switch (profile_kind) {
    case DOM_PROFILE_COMPAT:
        switch (perf_class) {
        case CORE_CAP_PERF_COMPAT: return 3u;
        case CORE_CAP_PERF_BASELINE: return 2u;
        default: break;
        }
        return 1u;
    case DOM_PROFILE_PERF:
        switch (perf_class) {
        case CORE_CAP_PERF_PERF: return 3u;
        case CORE_CAP_PERF_BASELINE: return 2u;
        default: break;
        }
        return 1u;
    case DOM_PROFILE_BASELINE:
    default:
        break;
    }

    switch (perf_class) {
    case CORE_CAP_PERF_BASELINE: return 3u;
    case CORE_CAP_PERF_COMPAT: return 2u;
    default: break;
    }
    return 1u;
}

static int comp_get_enum(const core_solver_component_desc* comp, u32 key_id, u32& out_value) {
    u32 i;
    if (!comp || !comp->provides) return 0;
    for (i = 0u; i < comp->provides_count; ++i) {
        const core_cap_entry* e = &comp->provides[i];
        if (e->key_id == key_id && e->type == (u8)CORE_CAP_ENUM_ID) {
            out_value = e->v.enum_id;
            return 1;
        }
    }
    return 0;
}

static u32 score_fn(const core_solver_component_desc* comp, void* user) {
    ScoreContext* ctx = (ScoreContext*)user;
    u32 perf_class = CORE_CAP_PERF_BASELINE;
    if (comp && comp_get_enum(comp, CORE_CAP_KEY_PERF_CLASS, perf_class)) {
        return caps_perf_score(ctx ? ctx->profile_kind : DOM_PROFILE_BASELINE, perf_class);
    }
    return caps_perf_score(ctx ? ctx->profile_kind : DOM_PROFILE_BASELINE, perf_class);
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

static void merge_caps_entries(core_caps& dst, const std::vector<core_cap_entry>& entries) {
    size_t i;
    for (i = 0u; i < entries.size(); ++i) {
        const core_cap_entry& e = entries[i];
        switch (e.type) {
        case CORE_CAP_BOOL:
            (void)core_caps_set_bool(&dst, e.key_id, e.v.bool_value);
            break;
        case CORE_CAP_I32:
            (void)core_caps_set_i32(&dst, e.key_id, e.v.i32_value);
            break;
        case CORE_CAP_U32:
            (void)core_caps_set_u32(&dst, e.key_id, e.v.u32_value);
            break;
        case CORE_CAP_I64:
            (void)core_caps_set_i64(&dst, e.key_id, e.v.i64_value);
            break;
        case CORE_CAP_U64:
            (void)core_caps_set_u64(&dst, e.key_id, e.v.u64_value);
            break;
        case CORE_CAP_ENUM_ID:
            (void)core_caps_set_enum(&dst, e.key_id, e.v.enum_id);
            break;
        case CORE_CAP_STRING_ID:
            (void)core_caps_set_string_id(&dst, e.key_id, e.v.string_id);
            break;
        case CORE_CAP_RANGE_U32:
            (void)core_caps_set_range_u32(&dst, e.key_id, e.v.range_u32.min_value, e.v.range_u32.max_value);
            break;
        default:
            break;
        }
    }
}

static void add_override(std::vector<core_solver_override>& out,
                         u32 category_id,
                         const char* component_id) {
    size_t i;
    if (!component_id || !component_id[0]) {
        return;
    }
    for (i = 0u; i < out.size(); ++i) {
        if (out[i].category_id == category_id) {
            out[i].component_id = component_id;
            return;
        }
    }
    {
        core_solver_override ov;
        ov.category_id = category_id;
        ov.component_id = component_id;
        out.push_back(ov);
    }
}

static void build_overrides(const dom_profile* profile,
                            std::vector<core_solver_override>& out) {
    u32 i;
    out.clear();
    if (!profile) {
        return;
    }
    if (profile->preferred_gfx_backend[0]) {
        add_override(out, CORE_SOLVER_CAT_RENDERER, profile->preferred_gfx_backend);
    }
    for (i = 0u; i < profile->override_count && i < (u32)DOM_PROFILE_MAX_OVERRIDES; ++i) {
        const dom_profile_override* ov = &profile->overrides[i];
        if (str_ieq(ov->subsystem_key, "gfx")) {
            add_override(out, CORE_SOLVER_CAT_RENDERER, ov->backend_name);
        } else if (str_ieq(ov->subsystem_key, "ui")) {
            add_override(out, CORE_SOLVER_CAT_UI, ov->backend_name);
        } else if (str_ieq(ov->subsystem_key, "sys") ||
                   (std::strncmp(ov->subsystem_key, "sys.", 4) == 0)) {
            add_override(out, CORE_SOLVER_CAT_PLATFORM, ov->backend_name);
        }
    }
}

static void init_profile_fallback(dom_profile& out) {
    std::memset(&out, 0, sizeof(out));
    out.abi_version = DOM_PROFILE_ABI_VERSION;
    out.struct_size = (u32)sizeof(dom_profile);
    out.kind = DOM_PROFILE_BASELINE;
    out.lockstep_strict = 0u;
}

static bool build_components(const dom_profile* profile,
                             std::vector<ComponentStore>& components,
                             std::vector<LauncherCapsBackend>& backends,
                             std::vector<core_solver_category_desc>& categories) {
    dom_backend_desc desc;
    u32 i;
    bool saw_platform = false;
    bool saw_ui = false;
    bool saw_renderer = false;

    components.clear();
    backends.clear();
    categories.clear();

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
            backends.push_back(b);
        }

        {
            ComponentStore comp;
            u32 category_id = category_from_subsystem(desc.subsystem_id);
            if (category_id == CORE_SOLVER_CAT_NONE) {
                continue;
            }
            std::memset(&comp.desc, 0, sizeof(comp.desc));
            std::memset(&comp.backend, 0, sizeof(comp.backend));
            comp.backend = desc;
            comp.desc.component_id = desc.backend_name;
            comp.desc.category_id = category_id;
            comp.desc.priority = desc.backend_priority;

            comp.provides.push_back(make_cap_u32(CORE_CAP_KEY_SUBSYSTEM_ID, (u32)desc.subsystem_id));
            comp.provides.push_back(make_cap_enum(CORE_CAP_KEY_DETERMINISM_GRADE, det_grade_from_dom(desc.determinism)));
            comp.provides.push_back(make_cap_enum(CORE_CAP_KEY_PERF_CLASS, perf_class_from_dom(desc.perf_class)));
            comp.provides.push_back(make_cap_u32(CORE_CAP_KEY_BACKEND_PRIORITY, desc.backend_priority));

            if (desc.required_hw_flags & DOM_HW_OS_WIN32) {
                add_require_bool(comp.requires, CORE_CAP_KEY_OS_IS_WIN32, 1u);
            }
            if (desc.required_hw_flags & DOM_HW_OS_UNIX) {
                add_require_bool(comp.requires, CORE_CAP_KEY_OS_IS_UNIX, 1u);
            }
            if (desc.required_hw_flags & DOM_HW_OS_APPLE) {
                add_require_bool(comp.requires, CORE_CAP_KEY_OS_IS_APPLE, 1u);
            }
            if (desc.required_hw_flags & DOM_HW_CPU_X86_32) {
                add_require_enum(comp.requires, CORE_CAP_KEY_CPU_ARCH, CORE_CAP_ARCH_X86_32);
            }
            if (desc.required_hw_flags & DOM_HW_CPU_X86_64) {
                add_require_enum(comp.requires, CORE_CAP_KEY_CPU_ARCH, CORE_CAP_ARCH_X86_64);
            }
            if (desc.required_hw_flags & DOM_HW_CPU_ARM_32) {
                add_require_enum(comp.requires, CORE_CAP_KEY_CPU_ARCH, CORE_CAP_ARCH_ARM_32);
            }
            if (desc.required_hw_flags & DOM_HW_CPU_ARM_64) {
                add_require_enum(comp.requires, CORE_CAP_KEY_CPU_ARCH, CORE_CAP_ARCH_ARM_64);
            }
            if (profile && profile->lockstep_strict != 0u &&
                (desc.subsystem_flags & DOM_CAPS_SUBSYS_LOCKSTEP_RELEVANT) != 0u) {
                add_require_enum(comp.requires, CORE_CAP_KEY_DETERMINISM_GRADE, CORE_CAP_DET_D0_BIT_EXACT);
            }

            comp.desc.provides = comp.provides.empty() ? (const core_cap_entry*)0 : &comp.provides[0];
            comp.desc.provides_count = (u32)comp.provides.size();
            comp.desc.requires = comp.requires.empty() ? (const core_solver_constraint*)0 : &comp.requires[0];
            comp.desc.requires_count = (u32)comp.requires.size();
            comp.desc.forbids = comp.forbids.empty() ? (const core_solver_constraint*)0 : &comp.forbids[0];
            comp.desc.forbids_count = (u32)comp.forbids.size();
            comp.desc.prefers = comp.prefers.empty() ? (const core_solver_constraint*)0 : &comp.prefers[0];
            comp.desc.prefers_count = (u32)comp.prefers.size();
            comp.desc.conflicts = comp.conflicts.empty() ? (const char* const*)0 : &comp.conflicts[0];
            comp.desc.conflicts_count = (u32)comp.conflicts.size();

            components.push_back(comp);

            if (category_id == CORE_SOLVER_CAT_PLATFORM) saw_platform = true;
            if (category_id == CORE_SOLVER_CAT_UI) saw_ui = true;
            if (category_id == CORE_SOLVER_CAT_RENDERER) saw_renderer = true;
        }
    }

    if (saw_platform) {
        core_solver_category_desc c;
        c.category_id = CORE_SOLVER_CAT_PLATFORM;
        c.required = 1u;
        categories.push_back(c);
    }
    if (saw_ui) {
        core_solver_category_desc c;
        c.category_id = CORE_SOLVER_CAT_UI;
        c.required = 1u;
        categories.push_back(c);
    }
    if (saw_renderer) {
        core_solver_category_desc c;
        c.category_id = CORE_SOLVER_CAT_RENDERER;
        c.required = 1u;
        categories.push_back(c);
    }

    {
        core_solver_category_desc c;
        c.category_id = CORE_SOLVER_CAT_PROVIDER_NET;
        c.required = 1u;
        categories.push_back(c);
        c.category_id = CORE_SOLVER_CAT_PROVIDER_TRUST;
        categories.push_back(c);
        c.category_id = CORE_SOLVER_CAT_PROVIDER_KEYCHAIN;
        categories.push_back(c);
        c.category_id = CORE_SOLVER_CAT_PROVIDER_CONTENT;
        categories.push_back(c);
        c.category_id = CORE_SOLVER_CAT_PROVIDER_OS_INTEGRATION;
        categories.push_back(c);
    }

    {
        const provider_registry_entry* entries = 0;
        u32 entry_count = 0u;
        u32 j;
        provider_registry_get_entries(&entries, &entry_count);
        for (j = 0u; j < entry_count; ++j) {
            const provider_registry_entry* e = &entries[j];
            ComponentStore comp;
            std::memset(&comp.desc, 0, sizeof(comp.desc));
            std::memset(&comp.backend, 0, sizeof(comp.backend));
            comp.desc.component_id = e->provider_id;
            comp.desc.category_id = e->category_id;
            comp.desc.priority = e->priority;

            if (e->provides && e->provides_count) {
                comp.provides.assign(e->provides, e->provides + e->provides_count);
            }
            if (e->requires && e->requires_count) {
                comp.requires.assign(e->requires, e->requires + e->requires_count);
            }
            if (e->forbids && e->forbids_count) {
                comp.forbids.assign(e->forbids, e->forbids + e->forbids_count);
            }
            if (e->prefers && e->prefers_count) {
                comp.prefers.assign(e->prefers, e->prefers + e->prefers_count);
            }
            if (e->conflicts && e->conflicts_count) {
                comp.conflicts.assign(e->conflicts, e->conflicts + e->conflicts_count);
            }
            components.push_back(comp);
        }
    }

    std::sort(backends.begin(), backends.end(), backend_less);
    return true;
}

static const ComponentStore* find_component(const std::vector<ComponentStore>& comps,
                                            u32 category_id,
                                            const char* component_id) {
    size_t i;
    if (!component_id) {
        return 0;
    }
    for (i = 0u; i < comps.size(); ++i) {
        const ComponentStore& c = comps[i];
        if (c.desc.category_id == category_id && c.desc.component_id &&
            std::strcmp(c.desc.component_id, component_id) == 0) {
            return &c;
        }
    }
    return 0;
}

} /* namespace */

LauncherCapsProviderChoice::LauncherCapsProviderChoice()
    : provider_type(),
      provider_id(),
      why() {
}

LauncherCapsSolveResult::LauncherCapsSolveResult()
    : solver_result(),
      host_caps(),
      effective_caps(),
      backends(),
      selections(),
      platform_backends(),
      renderer_backends(),
      ui_backend(),
      provider_backends(),
      note() {
    core_solver_result_clear(&solver_result);
    core_caps_clear(&host_caps);
    core_caps_clear(&effective_caps);
}

bool launcher_caps_solve(const dom_profile* profile,
                         LauncherCapsSolveResult& out_result,
                         std::string& out_error) {
    dom_profile fallback;
    dom_profile relaxed;
    const dom_profile* used_profile = profile;
    std::vector<ComponentStore> comps;
    std::vector<core_solver_component_desc> comp_descs;
    std::vector<core_solver_category_desc> categories;
    std::vector<core_solver_override> overrides;
    ScoreContext score_ctx;
    core_solver_desc desc;
    core_solver_result result;
    bool requested_gfx_null = false;
    bool relaxed_gfx_null = false;
    size_t i;

    out_error.clear();
    out_result = LauncherCapsSolveResult();

    if (!profile_is_valid(profile)) {
        init_profile_fallback(fallback);
        used_profile = &fallback;
    }

    build_host_caps(out_result.host_caps);

    if (!build_components(used_profile, comps, out_result.backends, categories)) {
        out_error = "caps_select_failed";
        return false;
    }

    comp_descs.reserve(comps.size());
    for (i = 0u; i < comps.size(); ++i) {
        core_solver_component_desc desc_entry = comps[i].desc;
        desc_entry.provides = comps[i].provides.empty() ? (const core_cap_entry*)0 : &comps[i].provides[0];
        desc_entry.provides_count = (u32)comps[i].provides.size();
        desc_entry.requires = comps[i].requires.empty() ? (const core_solver_constraint*)0 : &comps[i].requires[0];
        desc_entry.requires_count = (u32)comps[i].requires.size();
        desc_entry.forbids = comps[i].forbids.empty() ? (const core_solver_constraint*)0 : &comps[i].forbids[0];
        desc_entry.forbids_count = (u32)comps[i].forbids.size();
        desc_entry.prefers = comps[i].prefers.empty() ? (const core_solver_constraint*)0 : &comps[i].prefers[0];
        desc_entry.prefers_count = (u32)comps[i].prefers.size();
        desc_entry.conflicts = comps[i].conflicts.empty()
            ? (const char* const*)0
            : (const char* const*)&comps[i].conflicts[0];
        desc_entry.conflicts_count = (u32)comps[i].conflicts.size();
        comp_descs.push_back(desc_entry);
    }

    build_overrides(used_profile, overrides);

    std::memset(&desc, 0, sizeof(desc));
    desc.categories = categories.empty() ? (const core_solver_category_desc*)0 : &categories[0];
    desc.category_count = (u32)categories.size();
    desc.components = comp_descs.empty() ? (const core_solver_component_desc*)0 : &comp_descs[0];
    desc.component_count = (u32)comp_descs.size();
    desc.host_caps = &out_result.host_caps;
    desc.profile_requires = (const core_solver_constraint*)0;
    desc.profile_requires_count = 0u;
    desc.profile_forbids = (const core_solver_constraint*)0;
    desc.profile_forbids_count = 0u;
    desc.overrides = overrides.empty() ? (const core_solver_override*)0 : &overrides[0];
    desc.override_count = (u32)overrides.size();
    score_ctx.profile_kind = used_profile ? used_profile->kind : DOM_PROFILE_BASELINE;
    desc.score_fn = score_fn;
    desc.score_user = &score_ctx;

    core_solver_result_clear(&result);
    if (core_solver_select(&desc, &result) != 0) {
        if (used_profile && used_profile->lockstep_strict == 0u) {
            requested_gfx_null = profile_requests_gfx_null(used_profile);
        }
        if (requested_gfx_null) {
            relaxed = *used_profile;
            relaxed.preferred_gfx_backend[0] = '\0';
            profile_remove_override(relaxed, "gfx");
            build_overrides(&relaxed, overrides);
            desc.overrides = overrides.empty() ? (const core_solver_override*)0 : &overrides[0];
            desc.override_count = (u32)overrides.size();
            core_solver_result_clear(&result);
            if (core_solver_select(&desc, &result) == 0) {
                relaxed_gfx_null = true;
            }
        }
    }

    if (result.ok == 0u) {
        out_result.solver_result = result;
        out_error = "caps_select_failed";
        return false;
    }

    out_result.solver_result = result;

    if (relaxed_gfx_null) {
        out_result.note = "caps_fallback_gfx_null_unavailable=1";
    }

    core_caps_clear(&out_result.effective_caps);
    (void)core_caps_merge(&out_result.effective_caps, &out_result.host_caps);

    for (i = 0u; i < result.selected_count; ++i) {
        const core_solver_selected* s = &result.selected[i];
        const ComponentStore* comp = find_component(comps, s->category_id, s->component_id);
        if (!comp) {
            continue;
        }
        if (s->category_id == CORE_SOLVER_CAT_PLATFORM ||
            s->category_id == CORE_SOLVER_CAT_RENDERER ||
            s->category_id == CORE_SOLVER_CAT_UI) {
            LauncherCapsSelection sel;
            sel.subsystem_id = (u32)comp->backend.subsystem_id;
            sel.subsystem_name = subsystem_name_or_hex(sel.subsystem_id, comp->backend.subsystem_name);
            sel.backend_name = safe_str(comp->backend.backend_name);
            sel.determinism = (u32)comp->backend.determinism;
            sel.perf_class = (u32)comp->backend.perf_class;
            sel.priority = (u32)comp->backend.backend_priority;
            sel.chosen_by_override = (s->reason == CORE_SOLVER_SELECT_OVERRIDE) ? 1u : 0u;
            out_result.selections.push_back(sel);

            if (s->category_id == CORE_SOLVER_CAT_PLATFORM) {
                out_result.platform_backends.push_back(sel.backend_name);
            } else if (s->category_id == CORE_SOLVER_CAT_RENDERER) {
                out_result.renderer_backends.push_back(sel.backend_name);
            } else if (s->category_id == CORE_SOLVER_CAT_UI) {
                out_result.ui_backend = sel.backend_name;
            }
        } else {
            LauncherCapsProviderChoice pc;
            pc.provider_type = provider_type_from_category(s->category_id);
            pc.provider_id = safe_str(s->component_id);
            pc.why = (s->reason == CORE_SOLVER_SELECT_OVERRIDE) ? "override" : "priority";
            out_result.provider_backends.push_back(pc);
        }

        merge_caps_entries(out_result.effective_caps, comp->provides);
    }

    std::sort(out_result.selections.begin(), out_result.selections.end(), selection_less);
    return true;
}

static dom_abi_result vec_write_caps(void* user, const void* data, u32 len) {
    std::vector<unsigned char>* out = (std::vector<unsigned char>*)user;
    if (!out || (!data && len > 0u)) {
        return (dom_abi_result)-1;
    }
    if (len > 0u) {
        const unsigned char* p = (const unsigned char*)data;
        out->insert(out->end(), p, p + len);
    }
    return 0;
}

bool launcher_caps_write_effective_caps_tlv(const core_caps& caps,
                                            std::vector<unsigned char>& out_bytes) {
    core_caps_write_sink sink;
    out_bytes.clear();
    sink.user = &out_bytes;
    sink.write = vec_write_caps;
    return core_caps_write_tlv(&caps, &sink) == 0;
}

bool launcher_caps_write_explain_tlv(const core_solver_result& result,
                                     std::vector<unsigned char>& out_bytes) {
    core_solver_write_sink sink;
    out_bytes.clear();
    sink.user = &out_bytes;
    sink.write = vec_write_caps;
    return core_solver_explain_write_tlv(&result, &sink) == 0;
}

} /* namespace dom */
