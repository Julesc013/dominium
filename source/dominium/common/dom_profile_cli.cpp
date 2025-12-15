#include "dom_profile_cli.h"

#include <cstring>

extern "C" {
#include "domino/caps.h"
#include "domino/build_info.h"
}

namespace dom {

static int str_ieq(const char *a, const char *b) {
    size_t i;
    size_t len_a;
    size_t len_b;
    if (!a || !b) {
        return 0;
    }
    len_a = std::strlen(a);
    len_b = std::strlen(b);
    if (len_a != len_b) {
        return 0;
    }
    for (i = 0u; i < len_a; ++i) {
        char ca = a[i];
        char cb = b[i];
        if (ca >= 'A' && ca <= 'Z') ca = static_cast<char>(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = static_cast<char>(cb - 'A' + 'a');
        if (ca != cb) {
            return 0;
        }
    }
    return 1;
}

static bool copy_cstr_bounded(char *dst, size_t cap, const char *src) {
    size_t n;
    if (!dst || cap == 0u) {
        return false;
    }
    if (!src) {
        dst[0] = '\0';
        return true;
    }
    n = std::strlen(src);
    if (n >= cap) {
        return false;
    }
    std::memcpy(dst, src, n);
    dst[n] = '\0';
    return true;
}

static bool is_language_std_flag(const char *arg) {
    if (!arg) {
        return false;
    }
    if (std::strncmp(arg, "--cstd", 5) == 0) return true;
    if (std::strncmp(arg, "--cppstd", 8) == 0) return true;
    if (std::strncmp(arg, "--cxxstd", 8) == 0) return true;
    if (std::strncmp(arg, "--std=", 6) == 0) return true;
    return false;
}

static bool allow_gfx_backend_name(const char *name) {
    if (!name || !name[0]) {
        return false;
    }
    if (str_ieq(name, "soft")) return true;
    if (str_ieq(name, "dx9")) return true;
    if (str_ieq(name, "dx11")) return true;
    if (str_ieq(name, "gl2")) return true;
    if (str_ieq(name, "vk1")) return true;
    if (str_ieq(name, "metal")) return true;
    if (str_ieq(name, "gdi")) return true;
    if (str_ieq(name, "null")) return true;
    return false;
}

static bool upsert_override(dom_profile &p, const char *subsystem_key, const char *backend_name, std::string &err) {
    unsigned i;
    if (!subsystem_key || !subsystem_key[0] || !backend_name || !backend_name[0]) {
        err = "Invalid override; subsystem/backend must be non-empty.";
        return false;
    }
    for (i = 0u; i < p.override_count; ++i) {
        if (std::strcmp(p.overrides[i].subsystem_key, subsystem_key) == 0) {
            if (!copy_cstr_bounded(p.overrides[i].backend_name, sizeof(p.overrides[i].backend_name), backend_name)) {
                err = "Override backend name too long.";
                return false;
            }
            return true;
        }
    }
    if (p.override_count >= DOM_PROFILE_MAX_OVERRIDES) {
        err = "Too many overrides.";
        return false;
    }
    if (!copy_cstr_bounded(p.overrides[p.override_count].subsystem_key, sizeof(p.overrides[p.override_count].subsystem_key), subsystem_key)) {
        err = "Override subsystem key too long.";
        return false;
    }
    if (!copy_cstr_bounded(p.overrides[p.override_count].backend_name, sizeof(p.overrides[p.override_count].backend_name), backend_name)) {
        err = "Override backend name too long.";
        return false;
    }
    p.override_count += 1u;
    return true;
}

void init_default_profile_cli(ProfileCli &out) {
    std::memset(&out, 0, sizeof(out));
    std::memset(&out.profile, 0, sizeof(out.profile));
    out.profile.abi_version = DOM_PROFILE_ABI_VERSION;
    out.profile.struct_size = static_cast<u32>(sizeof(dom_profile));
    out.profile.kind = DOM_PROFILE_BASELINE;
    out.profile.lockstep_strict = 0u;
    out.profile.preferred_gfx_backend[0] = '\0';
    out.profile.override_count = 0u;
    out.profile.feature_count = 0u;
    out.print_caps = false;
    out.print_selection = false;
}

static bool parse_u32_01(const char *val, u32 &out_v) {
    if (!val) {
        return false;
    }
    if (std::strcmp(val, "0") == 0) {
        out_v = 0u;
        return true;
    }
    if (std::strcmp(val, "1") == 0) {
        out_v = 1u;
        return true;
    }
    return false;
}

bool parse_profile_cli_args(int argc, char **argv, ProfileCli &io, std::string &err) {
    int i;
    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg) {
            continue;
        }

        if (is_language_std_flag(arg)) {
            err = "Runtime language standard selection flags are not supported.";
            return false;
        }

        if (std::strcmp(arg, "--print-caps") == 0) {
            io.print_caps = true;
            continue;
        }
        if (std::strcmp(arg, "--print-selection") == 0) {
            io.print_selection = true;
            continue;
        }

        if (std::strncmp(arg, "--profile=", 10) == 0) {
            const char *val = arg + 10;
            if (str_ieq(val, "compat")) io.profile.kind = DOM_PROFILE_COMPAT;
            else if (str_ieq(val, "baseline")) io.profile.kind = DOM_PROFILE_BASELINE;
            else if (str_ieq(val, "perf")) io.profile.kind = DOM_PROFILE_PERF;
            else {
                err = "Unknown --profile value; expected compat|baseline|perf.";
                return false;
            }
            continue;
        }

        if (std::strncmp(arg, "--lockstep-strict=", 18) == 0) {
            u32 v = 0u;
            if (!parse_u32_01(arg + 18, v)) {
                err = "Invalid --lockstep-strict value; expected 0|1.";
                return false;
            }
            io.profile.lockstep_strict = v;
            continue;
        }

        if (std::strncmp(arg, "--gfx=", 6) == 0) {
            const char *val = arg + 6;
            if (!allow_gfx_backend_name(val)) {
                err = "Unsupported --gfx backend name.";
                return false;
            }
            if (!copy_cstr_bounded(io.profile.preferred_gfx_backend, sizeof(io.profile.preferred_gfx_backend), val)) {
                err = "Preferred gfx backend name too long.";
                return false;
            }
            if (!upsert_override(io.profile, "gfx", val, err)) {
                return false;
            }
            continue;
        }

        if (std::strncmp(arg, "--sys.", 6) == 0) {
            const char *eq = std::strchr(arg, '=');
            size_t klen;
            char key[DOM_PROFILE_SUBSYSTEM_KEY_MAX];
            const char *val;
            if (!eq) {
                continue;
            }
            klen = static_cast<size_t>(eq - (arg + 2)); /* strip leading "--" */
            if (klen == 0u || klen >= sizeof(key)) {
                err = "Invalid --sys.* override key.";
                return false;
            }
            std::memcpy(key, arg + 2, klen);
            key[klen] = '\0';
            val = eq + 1;
            if (!val || !val[0]) {
                err = "Invalid --sys.* override; backend name required.";
                return false;
            }
            if (!upsert_override(io.profile, key, val, err)) {
                return false;
            }
            continue;
        }
    }
    return true;
}

static const char *det_grade_name(dom_det_grade g) {
    switch (g) {
    case DOM_DET_D0_BIT_EXACT: return "D0";
    case DOM_DET_D1_TICK_EXACT: return "D1";
    default: break;
    }
    return "D2";
}

static const char *perf_class_name(dom_caps_perf_class c) {
    switch (c) {
    case DOM_CAPS_PERF_BASELINE: return "baseline";
    case DOM_CAPS_PERF_COMPAT: return "compat";
    case DOM_CAPS_PERF_PERF: return "perf";
    default: break;
    }
    return "baseline";
}

void print_caps(FILE *out) {
    u32 i;
    u32 count;
    dom_backend_desc desc;
    dom_subsystem_id current = 0u;

    if (!out) {
        out = stdout;
    }

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    count = dom_caps_backend_count();
    std::fprintf(out, "caps: available backends (%u)\n", (unsigned)count);

    for (i = 0u; i < count; ++i) {
        if (dom_caps_backend_get(i, &desc) != DOM_CAPS_OK) {
            continue;
        }
        if (i == 0u || desc.subsystem_id != current) {
            current = desc.subsystem_id;
            if (desc.subsystem_name && desc.subsystem_name[0]) {
                std::fprintf(out, "subsystem %u (%s)\n", (unsigned)desc.subsystem_id, desc.subsystem_name);
            } else {
                std::fprintf(out, "subsystem %u\n", (unsigned)desc.subsystem_id);
            }
        }
        std::fprintf(out, "  - %s det=%s perf=%s prio=%u\n",
                     (desc.backend_name ? desc.backend_name : "(null)"),
                     det_grade_name(desc.determinism),
                     perf_class_name(desc.perf_class),
                     (unsigned)desc.backend_priority);
    }
}

int print_selection(const dom_profile &profile, FILE *out, FILE *err) {
    dom_selection sel;
    char logbuf[DOM_CAPS_AUDIT_LOG_MAX_BYTES];
    u32 len;
    dom_caps_result r;

    if (!out) out = stdout;
    if (!err) err = stderr;

    {
        const dom_build_info_v1* bi;
        bi = dom_build_info_v1_get();
        std::fprintf(out, "build: id=%s git=%s\n",
                     (bi && bi->build_id) ? bi->build_id : "unknown",
                     (bi && bi->git_hash) ? bi->git_hash : "unknown");
    }

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    std::memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = static_cast<u32>(sizeof(dom_selection));

    r = dom_caps_select(&profile, NULL, &sel);
    if (r != DOM_CAPS_OK) {
        std::fprintf(err, "caps: selection failed (result=%d fail_reason=%u fail_subsystem_id=%u)\n",
                     (int)sel.result,
                     (unsigned)sel.fail_reason,
                     (unsigned)sel.fail_subsystem_id);
    }

    len = static_cast<u32>(sizeof(logbuf));
    std::memset(logbuf, 0, sizeof(logbuf));
    (void)dom_caps_get_audit_log(&sel, logbuf, &len);
    std::fwrite(logbuf, 1u, static_cast<size_t>(len), out);

    return (r == DOM_CAPS_OK) ? 0 : 1;
}

} // namespace dom
