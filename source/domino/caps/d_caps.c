#include "domino/caps.h"

#include "domino/profile.h"

#include <string.h>
#include <ctype.h>

static dom_backend_desc g_backends[DOM_CAPS_MAX_BACKENDS];
static u32 g_backend_count = 0u;
static u32 g_registry_finalized = 0u;

static int caps_is_ascii_space(char c)
{
    return (c == ' ') || (c == '\t') || (c == '\r') || (c == '\n');
}

static int caps_is_empty(const char* s)
{
    if (!s) {
        return 1;
    }
    while (*s) {
        if (!caps_is_ascii_space(*s)) {
            return 0;
        }
        ++s;
    }
    return 1;
}

static int caps_str_icmp(const char* a, const char* b)
{
    int ca;
    int cb;

    if (!a && !b) return 0;
    if (!a) return -1;
    if (!b) return 1;

    while (*a && *b) {
        ca = (unsigned char)*a;
        cb = (unsigned char)*b;
        ca = tolower(ca);
        cb = tolower(cb);
        if (ca != cb) {
            return (ca < cb) ? -1 : 1;
        }
        ++a;
        ++b;
    }

    if (*a == *b) return 0;
    return (*a < *b) ? -1 : 1;
}

static int caps_backend_key_cmp(const dom_backend_desc* a, const dom_backend_desc* b)
{
    if (a->subsystem_id != b->subsystem_id) {
        return (a->subsystem_id < b->subsystem_id) ? -1 : 1;
    }
    if (a->backend_priority != b->backend_priority) {
        /* Higher priority wins; sort descending. */
        return (a->backend_priority > b->backend_priority) ? -1 : 1;
    }
    return caps_str_icmp(a->backend_name, b->backend_name);
}

static void caps_sort_registry(void)
{
    u32 i;
    for (i = 1u; i < g_backend_count; ++i) {
        dom_backend_desc key;
        u32 j;

        key = g_backends[i];
        j = i;
        while (j > 0u) {
            if (caps_backend_key_cmp(&g_backends[j - 1u], &key) <= 0) {
                break;
            }
            g_backends[j] = g_backends[j - 1u];
            --j;
        }
        g_backends[j] = key;
    }
}

static dom_caps_result caps_validate_desc(const dom_backend_desc* desc)
{
    if (!desc) {
        return DOM_CAPS_ERR_NULL;
    }
    if (desc->abi_version != (u32)DOM_CAPS_ABI_VERSION) {
        return DOM_CAPS_ERR_BAD_DESC;
    }
    if (desc->struct_size != (u32)sizeof(dom_backend_desc)) {
        return DOM_CAPS_ERR_BAD_DESC;
    }
    if (desc->subsystem_id == 0u) {
        return DOM_CAPS_ERR_BAD_DESC;
    }
    if (caps_is_empty(desc->backend_name)) {
        return DOM_CAPS_ERR_BAD_DESC;
    }
    return DOM_CAPS_OK;
}

dom_caps_result dom_caps_register_backend(const dom_backend_desc* desc)
{
    u32 i;
    dom_caps_result vr;

    if (g_registry_finalized) {
        return DOM_CAPS_ERR_FINALIZED;
    }

    vr = caps_validate_desc(desc);
    if (vr != DOM_CAPS_OK) {
        return vr;
    }

    for (i = 0u; i < g_backend_count; ++i) {
        if (g_backends[i].subsystem_id == desc->subsystem_id &&
            caps_str_icmp(g_backends[i].backend_name, desc->backend_name) == 0) {
            return DOM_CAPS_ERR_DUPLICATE;
        }
    }

    if (g_backend_count >= (u32)DOM_CAPS_MAX_BACKENDS) {
        return DOM_CAPS_ERR_TOO_MANY;
    }

    g_backends[g_backend_count] = *desc;
    g_backend_count += 1u;
    return DOM_CAPS_OK;
}

dom_caps_result dom_caps_finalize_registry(void)
{
    if (g_registry_finalized) {
        return DOM_CAPS_ERR_FINALIZED;
    }
    caps_sort_registry();
    g_registry_finalized = 1u;
    return DOM_CAPS_OK;
}

u32 dom_caps_backend_count(void)
{
    return g_backend_count;
}

dom_caps_result dom_caps_backend_get(u32 index, dom_backend_desc* out_desc)
{
    if (!out_desc) {
        return DOM_CAPS_ERR_NULL;
    }
    if (index >= g_backend_count) {
        return DOM_CAPS_ERR;
    }
    *out_desc = g_backends[index];
    return DOM_CAPS_OK;
}

static void caps_sel_zero(dom_selection* out)
{
    u32 i;
    if (!out) {
        return;
    }
    out->result = DOM_CAPS_ERR;
    out->fail_reason = DOM_SEL_FAIL_NONE;
    out->fail_subsystem_id = 0u;
    out->entry_count = 0u;
    for (i = 0u; i < (u32)DOM_CAPS_MAX_SELECTION; ++i) {
        out->entries[i].subsystem_id = 0u;
        out->entries[i].subsystem_name = (const char*)0;
        out->entries[i].backend_name = (const char*)0;
        out->entries[i].determinism = DOM_DET_D2_BEST_EFFORT;
        out->entries[i].perf_class = DOM_CAPS_PERF_BASELINE;
        out->entries[i].backend_priority = 0u;
        out->entries[i].chosen_by_override = 0u;
    }
}

static int caps_backend_hw_ok(const dom_backend_desc* b, const dom_hw_caps* hw)
{
    u32 hw_mask;
    if (!b) {
        return 0;
    }
    if (b->required_hw_flags == 0u) {
        return 1;
    }
    if (!hw) {
        /* Unknown hardware: only allow zero-requirement backends. */
        return 0;
    }
    hw_mask = hw->os_flags | hw->cpu_flags | hw->gpu_flags;
    return ((hw_mask & b->required_hw_flags) == b->required_hw_flags) ? 1 : 0;
}

dom_caps_result dom_caps_select(const struct dom_profile* profile,
                                const dom_hw_caps* hw,
                                dom_selection* out)
{
    u32 i;
    u32 out_count;
    u32 lockstep_strict;
    (void)profile;

    if (!out) {
        return DOM_CAPS_ERR_NULL;
    }

    caps_sel_zero(out);

    if (!g_registry_finalized) {
        out->result = DOM_CAPS_ERR_NOT_FINALIZED;
        out->fail_reason = DOM_SEL_FAIL_REGISTRY_NOT_FINALIZED;
        return out->result;
    }

    lockstep_strict = 0u;
    if (profile) {
        if (profile->abi_version == (u32)DOM_PROFILE_ABI_VERSION &&
            profile->struct_size == (u32)sizeof(dom_profile)) {
            lockstep_strict = profile->lockstep_strict ? 1u : 0u;
        }
    }

    out_count = 0u;
    i = 0u;
    while (i < g_backend_count) {
        dom_subsystem_id sid;
        const dom_backend_desc* chosen;
        const dom_backend_desc* b;
        u32 sub_flags;
        u32 saw_hw_ok;

        sid = g_backends[i].subsystem_id;
        sub_flags = g_backends[i].subsystem_flags;
        saw_hw_ok = 0u;

        /* Select the first eligible backend in the sorted group. */
        chosen = (const dom_backend_desc*)0;
        while (i < g_backend_count && g_backends[i].subsystem_id == sid) {
            b = &g_backends[i];
            if (caps_backend_hw_ok(b, hw)) {
                saw_hw_ok = 1u;
                if (lockstep_strict && ((sub_flags & DOM_CAPS_SUBSYS_LOCKSTEP_RELEVANT) != 0u)) {
                    if (b->determinism != DOM_DET_D0_BIT_EXACT) {
                        i += 1u;
                        continue;
                    }
                }
                chosen = b;
                break;
            }
            i += 1u;
        }

        /* Skip remaining entries in this subsystem group. */
        while (i < g_backend_count && g_backends[i].subsystem_id == sid) {
            i += 1u;
        }

        if (!chosen) {
            out->result = DOM_CAPS_ERR_NO_ELIGIBLE;
            if (lockstep_strict && ((sub_flags & DOM_CAPS_SUBSYS_LOCKSTEP_RELEVANT) != 0u) && saw_hw_ok) {
                out->fail_reason = DOM_SEL_FAIL_LOCKSTEP_REQUIRES_D0;
            } else {
                out->fail_reason = DOM_SEL_FAIL_NO_ELIGIBLE_BACKEND;
            }
            out->fail_subsystem_id = sid;
            return out->result;
        }

        if (out_count >= (u32)DOM_CAPS_MAX_SELECTION) {
            out->result = DOM_CAPS_ERR_TOO_MANY;
            return out->result;
        }

        out->entries[out_count].subsystem_id = chosen->subsystem_id;
        out->entries[out_count].subsystem_name = chosen->subsystem_name;
        out->entries[out_count].backend_name = chosen->backend_name;
        out->entries[out_count].determinism = chosen->determinism;
        out->entries[out_count].perf_class = chosen->perf_class;
        out->entries[out_count].backend_priority = chosen->backend_priority;
        out->entries[out_count].chosen_by_override = 0u;
        out_count += 1u;
    }

    out->entry_count = out_count;
    out->result = DOM_CAPS_OK;
    return out->result;
}

static void caps_append_char(char* buf, u32 cap, u32* io_len, char c)
{
    u32 len;
    if (!buf || !io_len) {
        return;
    }
    len = *io_len;
    if (len + 1u >= cap) {
        return;
    }
    buf[len] = c;
    buf[len + 1u] = '\0';
    *io_len = len + 1u;
}

static void caps_append_str(char* buf, u32 cap, u32* io_len, const char* s)
{
    u32 len;
    u32 slen;
    u32 i;

    if (!buf || !io_len || !s) {
        return;
    }

    len = *io_len;
    slen = (u32)strlen(s);
    if (len + slen >= cap) {
        /* Best-effort partial append (still deterministic). */
        i = 0u;
        while (len + 1u < cap && s[i]) {
            buf[len] = s[i];
            ++i;
            ++len;
        }
        if (cap > 0u) {
            buf[(len < cap) ? len : (cap - 1u)] = '\0';
        }
        *io_len = (len < cap) ? len : (cap - 1u);
        return;
    }

    memcpy(buf + len, s, slen);
    buf[len + slen] = '\0';
    *io_len = len + slen;
}

static void caps_append_u32(char* buf, u32 cap, u32* io_len, u32 v)
{
    char tmp[16];
    u32 n;
    u32 i;

    n = 0u;
    if (v == 0u) {
        tmp[n++] = '0';
    } else {
        while (v != 0u && n < 10u) {
            tmp[n++] = (char)('0' + (v % 10u));
            v /= 10u;
        }
    }

    /* reverse */
    for (i = 0u; i < n / 2u; ++i) {
        char t = tmp[i];
        tmp[i] = tmp[n - 1u - i];
        tmp[n - 1u - i] = t;
    }
    tmp[n] = '\0';
    caps_append_str(buf, cap, io_len, tmp);
}

static const char* caps_det_grade_name(dom_det_grade g)
{
    switch (g) {
    case DOM_DET_D0_BIT_EXACT: return "D0";
    case DOM_DET_D1_TICK_EXACT: return "D1";
    default: break;
    }
    return "D2";
}

static const char* caps_perf_class_name(dom_caps_perf_class c)
{
    switch (c) {
    case DOM_CAPS_PERF_BASELINE: return "baseline";
    case DOM_CAPS_PERF_COMPAT: return "compat";
    case DOM_CAPS_PERF_PERF: return "perf";
    default: break;
    }
    return "baseline";
}

dom_caps_result dom_caps_get_audit_log(const dom_selection* sel,
                                       char* buf,
                                       u32* io_len)
{
    u32 cap;
    u32 len;
    u32 i;

    if (!io_len) {
        return DOM_CAPS_ERR_NULL;
    }

    cap = *io_len;
    if (!buf || cap == 0u) {
        return DOM_CAPS_ERR_NULL;
    }

    buf[0] = '\0';
    len = 0u;

    if (!sel) {
        caps_append_str(buf, cap, &len, "caps: no selection\n");
        *io_len = len;
        return DOM_CAPS_ERR_NULL;
    }

    caps_append_str(buf, cap, &len, "caps: selection\n");
    caps_append_str(buf, cap, &len, "result=");
    caps_append_u32(buf, cap, &len, (u32)(sel->result));
    caps_append_char(buf, cap, &len, '\n');

    if (sel->result != DOM_CAPS_OK) {
        caps_append_str(buf, cap, &len, "fail_reason=");
        caps_append_u32(buf, cap, &len, (u32)(sel->fail_reason));
        caps_append_str(buf, cap, &len, " fail_subsystem_id=");
        caps_append_u32(buf, cap, &len, (u32)(sel->fail_subsystem_id));
        caps_append_char(buf, cap, &len, '\n');
        *io_len = len;
        return sel->result;
    }

    for (i = 0u; i < sel->entry_count; ++i) {
        const dom_selection_entry* e = &sel->entries[i];
        caps_append_str(buf, cap, &len, "- subsystem_id=");
        caps_append_u32(buf, cap, &len, (u32)(e->subsystem_id));
        if (e->subsystem_name && e->subsystem_name[0]) {
            caps_append_str(buf, cap, &len, " (");
            caps_append_str(buf, cap, &len, e->subsystem_name);
            caps_append_str(buf, cap, &len, ")");
        }
        caps_append_str(buf, cap, &len, " backend=");
        caps_append_str(buf, cap, &len, e->backend_name ? e->backend_name : "(null)");
        caps_append_str(buf, cap, &len, " det=");
        caps_append_str(buf, cap, &len, caps_det_grade_name(e->determinism));
        caps_append_str(buf, cap, &len, " perf=");
        caps_append_str(buf, cap, &len, caps_perf_class_name(e->perf_class));
        caps_append_str(buf, cap, &len, " prio=");
        caps_append_u32(buf, cap, &len, e->backend_priority);
        caps_append_char(buf, cap, &len, '\n');
    }

    *io_len = len;
    return DOM_CAPS_OK;
}
