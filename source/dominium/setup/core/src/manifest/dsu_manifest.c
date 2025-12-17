/*
FILE: source/dominium/setup/core/src/manifest/dsu_manifest.c
MODULE: Dominium Setup
PURPOSE: TLV manifest v2 loader/writer/validator (Plan S-2).
*/
#include "../../include/dsu/dsu_manifest.h"
#include "../../include/dsu/dsu_log.h"

#include "../dsu_ctx_internal.h"
#include "../log/dsu_events.h"
#include "../util/dsu_util_internal.h"

#include <string.h>

#define DSU_TLV_MANIFEST_ROOT 0x0001u

#define DSU_TLV_ROOT_VERSION 0x0002u /* u32 */

#define DSU_TLV_PRODUCT_ID 0x0010u          /* string (ascii id) */
#define DSU_TLV_PRODUCT_VERSION 0x0011u     /* string (semver-ish) */
#define DSU_TLV_BUILD_CHANNEL 0x0012u       /* string */
#define DSU_TLV_PLATFORM_TARGET 0x0020u     /* string (platform triple), repeatable */

#define DSU_TLV_DEFAULT_INSTALL_ROOT 0x0030u /* container */
#define DSU_TLV_INSTALL_ROOT_VERSION 0x0031u /* u32 */
#define DSU_TLV_INSTALL_SCOPE 0x0032u        /* u8 enum */
#define DSU_TLV_INSTALL_PLATFORM 0x0033u     /* string (platform triple) */
#define DSU_TLV_INSTALL_PATH 0x0034u         /* string (path, canonical /) */

#define DSU_TLV_COMPONENT 0x0040u            /* container */
#define DSU_TLV_COMPONENT_VERSION 0x0041u    /* u32 */
#define DSU_TLV_COMPONENT_ID 0x0042u         /* string (ascii id) */
#define DSU_TLV_COMPONENT_VERSTR 0x0043u     /* string, optional */
#define DSU_TLV_COMPONENT_KIND 0x0044u       /* u8 enum */
#define DSU_TLV_COMPONENT_FLAGS 0x0045u      /* u32 */

#define DSU_TLV_DEPENDENCY 0x0046u           /* container */
#define DSU_TLV_DEP_VERSION 0x0047u          /* u32 */
#define DSU_TLV_DEP_COMPONENT_ID 0x0048u     /* string (ascii id) */
#define DSU_TLV_DEP_CONSTRAINT_KIND 0x0049u  /* u8 enum */
#define DSU_TLV_DEP_CONSTRAINT_VERSION 0x004Au /* string */

#define DSU_TLV_CONFLICT 0x004Bu             /* string (ascii id), repeatable */

#define DSU_TLV_PAYLOAD 0x004Cu              /* container */
#define DSU_TLV_PAYLOAD_VERSION 0x004Du      /* u32 */
#define DSU_TLV_PAYLOAD_KIND 0x004Eu         /* u8 enum */
#define DSU_TLV_PAYLOAD_PATH 0x004Fu         /* string (path, canonical /) */
#define DSU_TLV_PAYLOAD_SHA256 0x0050u       /* bytes[32] */
#define DSU_TLV_PAYLOAD_SIZE 0x0051u         /* u64 */

#define DSU_TLV_ACTION 0x0052u               /* container */
#define DSU_TLV_ACTION_VERSION 0x0053u       /* u32 */
#define DSU_TLV_ACTION_KIND 0x0054u          /* u8 enum */

/* Action fields (by kind) */
#define DSU_TLV_ACTION_APP_ID 0x0055u        /* string (ascii id) */
#define DSU_TLV_ACTION_DISPLAY_NAME 0x0056u  /* string (utf-8) */
#define DSU_TLV_ACTION_EXEC_RELPATH 0x0057u  /* string (path) */
#define DSU_TLV_ACTION_ARGUMENTS 0x0058u     /* string (utf-8) */
#define DSU_TLV_ACTION_ICON_RELPATH 0x0059u  /* string (path) */
#define DSU_TLV_ACTION_EXTENSION 0x005Au     /* string */
#define DSU_TLV_ACTION_PROTOCOL 0x005Bu      /* string */
#define DSU_TLV_ACTION_MARKER_RELPATH 0x005Cu /* string (path) */
#define DSU_TLV_ACTION_CAPABILITY_ID 0x005Du /* string (ascii id) */
#define DSU_TLV_ACTION_CAPABILITY_VALUE 0x005Eu /* string (utf-8) */
#define DSU_TLV_ACTION_PUBLISHER 0x005Fu     /* string (utf-8) */

#define DSU_TLV_UNINSTALL_POLICY 0x0060u     /* container */
#define DSU_TLV_POLICY_VERSION 0x0061u       /* u32 */
#define DSU_TLV_POLICY_REMOVE_OWNED 0x0062u  /* u8 bool */
#define DSU_TLV_POLICY_PRESERVE_USER_DATA 0x0063u /* u8 bool */
#define DSU_TLV_POLICY_PRESERVE_CACHE 0x0064u /* u8 bool */

typedef struct dsu_manifest_install_root_t {
    dsu_u8 scope;
    char *platform;
    char *path;
} dsu_manifest_install_root_t;

typedef struct dsu_manifest_dependency_t {
    char *id;
    dsu_u8 constraint_kind;
    char *constraint_version; /* optional */
} dsu_manifest_dependency_t;

typedef struct dsu_manifest_payload_t {
    dsu_u8 kind;
    char *path; /* optional for blobs */
    dsu_u8 sha256[32];
    dsu_u8 has_sha256;
    dsu_u8 has_size;
    dsu_u64 size;
} dsu_manifest_payload_t;

typedef struct dsu_manifest_action_t {
    dsu_u8 kind;
    char *app_id;
    char *display_name;
    char *exec_relpath;
    char *arguments;
    char *icon_relpath;
    char *extension;
    char *protocol;
    char *marker_relpath;
    char *capability_id;
    char *capability_value;
    char *publisher;
} dsu_manifest_action_t;

typedef struct dsu_manifest_component_t {
    char *id;
    char *version; /* optional (NULL => inherits product) */
    dsu_u8 kind;
    dsu_u32 flags;

    dsu_u32 dep_count;
    dsu_u32 dep_cap;
    dsu_manifest_dependency_t *deps;

    dsu_u32 conflict_count;
    dsu_u32 conflict_cap;
    char **conflicts;

    dsu_u32 payload_count;
    dsu_u32 payload_cap;
    dsu_manifest_payload_t *payloads;

    dsu_u32 action_count;
    dsu_u32 action_cap;
    dsu_manifest_action_t *actions;
} dsu_manifest_component_t;

typedef struct dsu_manifest_uninstall_policy_t {
    dsu_u8 remove_owned_files;
    dsu_u8 preserve_user_data;
    dsu_u8 preserve_cache;
    dsu_u8 present;
} dsu_manifest_uninstall_policy_t;

struct dsu_manifest {
    dsu_u32 root_version;
    char *product_id;
    char *product_version;
    char *build_channel;

    dsu_u32 platform_target_count;
    char **platform_targets;
    dsu_u32 platform_target_cap;

    dsu_u32 install_root_count;
    dsu_u32 install_root_cap;
    dsu_manifest_install_root_t *install_roots;

    dsu_u32 component_count;
    dsu_u32 component_cap;
    dsu_manifest_component_t *components;

    dsu_manifest_uninstall_policy_t uninstall_policy;

    dsu_u32 content_digest32;
    dsu_u64 content_digest64;
};

static int dsu__bytes_contains_nul(const dsu_u8 *bytes, dsu_u32 len) {
    dsu_u32 i;
    if (!bytes) {
        return 0;
    }
    for (i = 0u; i < len; ++i) {
        if (bytes[i] == 0u) {
            return 1;
        }
    }
    return 0;
}

static dsu_status_t dsu__dup_bytes_cstr(const dsu_u8 *bytes, dsu_u32 len, char **out_str) {
    char *s;
    if (!out_str) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_str = NULL;
    if (!bytes && len != 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (dsu__bytes_contains_nul(bytes, len)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    s = (char *)dsu__malloc(len + 1u);
    if (!s) {
        return DSU_STATUS_IO_ERROR;
    }
    if (len) {
        memcpy(s, bytes, (size_t)len);
    }
    s[len] = '\0';
    *out_str = s;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__read_tlv_u8(const dsu_u8 *v, dsu_u32 len, dsu_u8 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (len != 1u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    return dsu__read_u8(v, len, &off, out);
}

static dsu_status_t dsu__read_tlv_u32(const dsu_u8 *v, dsu_u32 len, dsu_u32 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (len != 4u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    return dsu__read_u32le(v, len, &off, out);
}

static dsu_status_t dsu__read_tlv_u64(const dsu_u8 *v, dsu_u32 len, dsu_u64 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (len != 8u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    return dsu__read_u64le(v, len, &off, out);
}

static dsu_status_t dsu__read_tlv_string(const dsu_u8 *v, dsu_u32 len, char **out_str) {
    return dsu__dup_bytes_cstr(v, len, out_str);
}

static dsu_status_t dsu__normalize_id_inplace(char *s) {
    dsu_status_t st;
    if (!s) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu__ascii_to_lower_inplace(s);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (!dsu__is_ascii_id(s)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static void dsu__normalize_path_inplace(char *s) {
    unsigned char *p;
    unsigned char c;
    if (!s) {
        return;
    }
    p = (unsigned char *)s;
    while ((c = *p) != 0u) {
        if (c == '\\') {
            *p = (unsigned char)'/';
        }
        ++p;
    }
}

static int dsu__is_platform_triple(const char *s) {
    const char *dash;
    dsu_u32 os_len;
    const char *arch;

    if (!s || s[0] == '\0') {
        return 0;
    }
    if (!dsu__is_ascii_id(s)) {
        return 0;
    }
    dash = strchr(s, '-');
    if (!dash) {
        return 0;
    }
    if (strchr(dash + 1, '-') != NULL) {
        return 0;
    }
    os_len = (dsu_u32)(dash - s);
    arch = dash + 1;
    if (arch[0] == '\0') {
        return 0;
    }

    if (!((os_len == 5u && memcmp(s, "win32", 5u) == 0) ||
          (os_len == 5u && memcmp(s, "win64", 5u) == 0) ||
          (os_len == 5u && memcmp(s, "linux", 5u) == 0) ||
          (os_len == 5u && memcmp(s, "macos", 5u) == 0) ||
          (os_len == 3u && memcmp(s, "any", 3u) == 0))) {
        return 0;
    }
    if (!(dsu__streq(arch, "x86") || dsu__streq(arch, "x64") || dsu__streq(arch, "arm64") || dsu__streq(arch, "any"))) {
        return 0;
    }
    return 1;
}

static int dsu__is_semverish(const char *s) {
    const unsigned char *p;
    dsu_u32 digits;
    if (!s || s[0] == '\0') {
        return 0;
    }
    if (!dsu__is_ascii_printable(s)) {
        return 0;
    }
    p = (const unsigned char *)s;

    digits = 0u;
    while (*p >= '0' && *p <= '9') {
        ++p;
        ++digits;
    }
    if (digits == 0u || *p != '.') return 0;
    ++p;
    digits = 0u;
    while (*p >= '0' && *p <= '9') {
        ++p;
        ++digits;
    }
    if (digits == 0u || *p != '.') return 0;
    ++p;
    digits = 0u;
    while (*p >= '0' && *p <= '9') {
        ++p;
        ++digits;
    }
    if (digits == 0u) return 0;
    if (*p == '\0') return 1;
    if (*p != '-') return 0;
    ++p;
    if (*p == '\0') return 0;
    while (*p) {
        unsigned char c = *p++;
        if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '.' || c == '_' || c == '-') {
            continue;
        }
        return 0;
    }
    return 1;
}

static int dsu__is_external_component_id(const char *id) {
    if (!id) {
        return 0;
    }
    if (strncmp(id, "external.", 9) == 0) {
        return 1;
    }
    if (strncmp(id, "ext.", 4) == 0) {
        return 1;
    }
    return 0;
}

static void dsu__manifest_component_free(dsu_manifest_component_t *c) {
    dsu_u32 i;
    if (!c) {
        return;
    }
    dsu__free(c->id);
    dsu__free(c->version);
    for (i = 0u; i < c->dep_count; ++i) {
        dsu__free(c->deps[i].id);
        dsu__free(c->deps[i].constraint_version);
    }
    dsu__free(c->deps);
    for (i = 0u; i < c->conflict_count; ++i) {
        dsu__free(c->conflicts[i]);
    }
    dsu__free(c->conflicts);
    for (i = 0u; i < c->payload_count; ++i) {
        dsu__free(c->payloads[i].path);
    }
    dsu__free(c->payloads);
    for (i = 0u; i < c->action_count; ++i) {
        dsu_manifest_action_t *a = &c->actions[i];
        dsu__free(a->app_id);
        dsu__free(a->display_name);
        dsu__free(a->exec_relpath);
        dsu__free(a->arguments);
        dsu__free(a->icon_relpath);
        dsu__free(a->extension);
        dsu__free(a->protocol);
        dsu__free(a->marker_relpath);
        dsu__free(a->capability_id);
        dsu__free(a->capability_value);
        dsu__free(a->publisher);
    }
    dsu__free(c->actions);
    memset(c, 0, sizeof(*c));
}

static void dsu__manifest_free(dsu_manifest_t *m) {
    dsu_u32 i;
    if (!m) {
        return;
    }
    dsu__free(m->product_id);
    dsu__free(m->product_version);
    dsu__free(m->build_channel);
    for (i = 0u; i < m->platform_target_count; ++i) {
        dsu__free(m->platform_targets[i]);
    }
    dsu__free(m->platform_targets);
    for (i = 0u; i < m->install_root_count; ++i) {
        dsu__free(m->install_roots[i].platform);
        dsu__free(m->install_roots[i].path);
    }
    dsu__free(m->install_roots);
    for (i = 0u; i < m->component_count; ++i) {
        dsu__manifest_component_free(&m->components[i]);
    }
    dsu__free(m->components);
    memset(m, 0, sizeof(*m));
}

static dsu_status_t dsu__str_list_push(char ***items, dsu_u32 *io_count, dsu_u32 *io_cap, char *owned) {
    dsu_u32 count;
    dsu_u32 cap;
    char **p;

    if (!items || !io_count || !io_cap || !owned) {
        return DSU_STATUS_INVALID_ARGS;
    }
    count = *io_count;
    cap = *io_cap;

    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (char **)dsu__realloc(*items, new_cap * (dsu_u32)sizeof(**items));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        *items = p;
        *io_cap = new_cap;
    }

    (*items)[count] = owned;
    *io_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__install_root_push(dsu_manifest_t *m, const dsu_manifest_install_root_t *src) {
    dsu_manifest_install_root_t *p;
    dsu_u32 count;
    dsu_u32 cap;
    if (!m || !src) {
        return DSU_STATUS_INVALID_ARGS;
    }
    count = m->install_root_count;
    cap = m->install_root_cap;
    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_manifest_install_root_t *)dsu__realloc(m->install_roots,
                                                       new_cap * (dsu_u32)sizeof(*m->install_roots));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        m->install_roots = p;
        m->install_root_cap = new_cap;
    }
    m->install_roots[count] = *src;
    m->install_root_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__component_push(dsu_manifest_t *m, const dsu_manifest_component_t *src) {
    dsu_manifest_component_t *p;
    dsu_u32 count;
    dsu_u32 cap;
    if (!m || !src) {
        return DSU_STATUS_INVALID_ARGS;
    }
    count = m->component_count;
    cap = m->component_cap;
    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_manifest_component_t *)dsu__realloc(m->components,
                                                    new_cap * (dsu_u32)sizeof(*m->components));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        m->components = p;
        m->component_cap = new_cap;
    }
    m->components[count] = *src;
    m->component_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__component_dep_push(dsu_manifest_component_t *c, const dsu_manifest_dependency_t *src) {
    dsu_manifest_dependency_t *p;
    dsu_u32 count;
    dsu_u32 cap;
    if (!c || !src) {
        return DSU_STATUS_INVALID_ARGS;
    }
    count = c->dep_count;
    cap = c->dep_cap;
    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_manifest_dependency_t *)dsu__realloc(c->deps, new_cap * (dsu_u32)sizeof(*c->deps));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        c->deps = p;
        c->dep_cap = new_cap;
    }
    c->deps[count] = *src;
    c->dep_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__component_conflict_push(dsu_manifest_component_t *c, char *owned_id) {
    return dsu__str_list_push(&c->conflicts, &c->conflict_count, &c->conflict_cap, owned_id);
}

static dsu_status_t dsu__component_payload_push(dsu_manifest_component_t *c, const dsu_manifest_payload_t *src) {
    dsu_manifest_payload_t *p;
    dsu_u32 count;
    dsu_u32 cap;
    if (!c || !src) {
        return DSU_STATUS_INVALID_ARGS;
    }
    count = c->payload_count;
    cap = c->payload_cap;
    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_manifest_payload_t *)dsu__realloc(c->payloads, new_cap * (dsu_u32)sizeof(*c->payloads));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        c->payloads = p;
        c->payload_cap = new_cap;
    }
    c->payloads[count] = *src;
    c->payload_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__component_action_push(dsu_manifest_component_t *c, const dsu_manifest_action_t *src) {
    dsu_manifest_action_t *p;
    dsu_u32 count;
    dsu_u32 cap;
    if (!c || !src) {
        return DSU_STATUS_INVALID_ARGS;
    }
    count = c->action_count;
    cap = c->action_cap;
    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_manifest_action_t *)dsu__realloc(c->actions, new_cap * (dsu_u32)sizeof(*c->actions));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        c->actions = p;
        c->action_cap = new_cap;
    }
    c->actions[count] = *src;
    c->action_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__parse_install_root_container(const dsu_u8 *buf,
                                                     dsu_u32 len,
                                                     dsu_manifest_install_root_t *out_root) {
    dsu_u32 off = 0u;
    dsu_u32 version = 0u;
    dsu_u8 scope = 0u;
    char *platform = NULL;
    char *path = NULL;
    int have_version = 0;
    int have_scope = 0;
    int have_platform = 0;
    int have_path = 0;
    dsu_status_t st;

    if (!buf || !out_root) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(out_root, 0, sizeof(*out_root));

    while (off < len) {
        dsu_u16 t;
        dsu_u32 n;
        dsu_u32 start;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        start = off;

        if (t == (dsu_u16)DSU_TLV_INSTALL_ROOT_VERSION) {
            if (have_version) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_u32(buf + start, n, &version);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_version = 1;
        } else if (t == (dsu_u16)DSU_TLV_INSTALL_SCOPE) {
            if (have_scope) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_u8(buf + start, n, &scope);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_scope = 1;
        } else if (t == (dsu_u16)DSU_TLV_INSTALL_PLATFORM) {
            if (have_platform) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_string(buf + start, n, &platform);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_platform = 1;
        } else if (t == (dsu_u16)DSU_TLV_INSTALL_PATH) {
            if (have_path) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_string(buf + start, n, &path);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_path = 1;
        }

        off = start + n;
    }

    if (!have_version || version != 1u) {
        st = DSU_STATUS_UNSUPPORTED_VERSION;
        goto fail;
    }
    if (!have_scope || !have_platform || !have_path) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }
    if (scope > (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }

    out_root->scope = scope;
    out_root->platform = platform;
    out_root->path = path;
    return DSU_STATUS_SUCCESS;

fail:
    dsu__free(platform);
    dsu__free(path);
    return st;
}

static dsu_status_t dsu__parse_dependency_container(const dsu_u8 *buf,
                                                   dsu_u32 len,
                                                   dsu_manifest_dependency_t *out_dep) {
    dsu_u32 off = 0u;
    dsu_u32 version = 0u;
    char *id = NULL;
    dsu_u8 kind = 0u;
    char *ver = NULL;
    int have_version = 0;
    int have_id = 0;
    int have_kind = 0;
    dsu_status_t st;

    if (!buf || !out_dep) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(out_dep, 0, sizeof(*out_dep));

    while (off < len) {
        dsu_u16 t;
        dsu_u32 n;
        dsu_u32 start;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        start = off;

        if (t == (dsu_u16)DSU_TLV_DEP_VERSION) {
            if (have_version) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_u32(buf + start, n, &version);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_version = 1;
        } else if (t == (dsu_u16)DSU_TLV_DEP_COMPONENT_ID) {
            if (have_id) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_string(buf + start, n, &id);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_id = 1;
        } else if (t == (dsu_u16)DSU_TLV_DEP_CONSTRAINT_KIND) {
            if (have_kind) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_u8(buf + start, n, &kind);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_kind = 1;
        } else if (t == (dsu_u16)DSU_TLV_DEP_CONSTRAINT_VERSION) {
            if (ver) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_string(buf + start, n, &ver);
            if (st != DSU_STATUS_SUCCESS) goto fail;
        }

        off = start + n;
    }

    if (!have_version || version != 1u) {
        st = DSU_STATUS_UNSUPPORTED_VERSION;
        goto fail;
    }
    if (!have_id || !have_kind) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }
    if (kind > (dsu_u8)DSU_MANIFEST_VERSION_CONSTRAINT_AT_LEAST) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }
    if (kind == (dsu_u8)DSU_MANIFEST_VERSION_CONSTRAINT_ANY) {
        dsu__free(ver);
        ver = NULL;
    } else {
        if (!ver || !dsu__is_semverish(ver)) {
            st = DSU_STATUS_PARSE_ERROR;
            goto fail;
        }
    }

    out_dep->id = id;
    out_dep->constraint_kind = kind;
    out_dep->constraint_version = ver;
    return DSU_STATUS_SUCCESS;

fail:
    dsu__free(id);
    dsu__free(ver);
    return st;
}

static dsu_status_t dsu__parse_payload_container(const dsu_u8 *buf,
                                                dsu_u32 len,
                                                dsu_manifest_payload_t *out_p) {
    dsu_u32 off = 0u;
    dsu_u32 version = 0u;
    dsu_u8 kind = 0u;
    char *path = NULL;
    dsu_u8 sha256[32];
    dsu_u8 have_sha = 0u;
    dsu_u64 size = 0u;
    dsu_u8 have_size = 0u;
    int have_version = 0;
    int have_kind = 0;
    dsu_status_t st;

    if (!buf || !out_p) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(out_p, 0, sizeof(*out_p));
    memset(sha256, 0, sizeof(sha256));

    while (off < len) {
        dsu_u16 t;
        dsu_u32 n;
        dsu_u32 start;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        start = off;

        if (t == (dsu_u16)DSU_TLV_PAYLOAD_VERSION) {
            if (have_version) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_u32(buf + start, n, &version);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_version = 1;
        } else if (t == (dsu_u16)DSU_TLV_PAYLOAD_KIND) {
            if (have_kind) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_u8(buf + start, n, &kind);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_kind = 1;
        } else if (t == (dsu_u16)DSU_TLV_PAYLOAD_PATH) {
            if (path) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_string(buf + start, n, &path);
            if (st != DSU_STATUS_SUCCESS) goto fail;
        } else if (t == (dsu_u16)DSU_TLV_PAYLOAD_SHA256) {
            if (have_sha) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            if (n != 32u) {
                st = DSU_STATUS_INTEGRITY_ERROR;
                goto fail;
            }
            memcpy(sha256, buf + start, 32u);
            have_sha = 1u;
        } else if (t == (dsu_u16)DSU_TLV_PAYLOAD_SIZE) {
            if (have_size) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_u64(buf + start, n, &size);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_size = 1u;
        }

        off = start + n;
    }

    if (!have_version || version != 1u) {
        st = DSU_STATUS_UNSUPPORTED_VERSION;
        goto fail;
    }
    if (!have_kind) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }
    if (kind > (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_BLOB) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }
    if (!have_sha) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }
    if ((kind == (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_FILESET ||
         kind == (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_ARCHIVE) &&
        (!path || path[0] == '\0')) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }
    if (path) {
        dsu__normalize_path_inplace(path);
    }

    out_p->kind = kind;
    out_p->path = path;
    memcpy(out_p->sha256, sha256, 32u);
    out_p->has_sha256 = 1u;
    out_p->has_size = have_size;
    out_p->size = size;
    return DSU_STATUS_SUCCESS;

fail:
    dsu__free(path);
    return st;
}

static void dsu__action_free_fields(dsu_manifest_action_t *a) {
    if (!a) {
        return;
    }
    dsu__free(a->app_id);
    dsu__free(a->display_name);
    dsu__free(a->exec_relpath);
    dsu__free(a->arguments);
    dsu__free(a->icon_relpath);
    dsu__free(a->extension);
    dsu__free(a->protocol);
    dsu__free(a->marker_relpath);
    dsu__free(a->capability_id);
    dsu__free(a->capability_value);
    dsu__free(a->publisher);
    memset(a, 0, sizeof(*a));
}

static dsu_status_t dsu__parse_action_container(const dsu_u8 *buf,
                                               dsu_u32 len,
                                               dsu_manifest_action_t *out_a) {
    dsu_u32 off = 0u;
    dsu_u32 version = 0u;
    dsu_u8 kind = 0u;
    int have_version = 0;
    int have_kind = 0;
    dsu_manifest_action_t a;
    dsu_status_t st;

    if (!buf || !out_a) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(&a, 0, sizeof(a));

    while (off < len) {
        dsu_u16 t;
        dsu_u32 n;
        dsu_u32 start;
        char **target_str = NULL;

        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__action_free_fields(&a);
            return st;
        }
        start = off;

        if (t == (dsu_u16)DSU_TLV_ACTION_VERSION) {
            if (have_version) {
                dsu__action_free_fields(&a);
                return DSU_STATUS_PARSE_ERROR;
            }
            st = dsu__read_tlv_u32(buf + start, n, &version);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__action_free_fields(&a);
                return st;
            }
            have_version = 1;
        } else if (t == (dsu_u16)DSU_TLV_ACTION_KIND) {
            if (have_kind) {
                dsu__action_free_fields(&a);
                return DSU_STATUS_PARSE_ERROR;
            }
            st = dsu__read_tlv_u8(buf + start, n, &kind);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__action_free_fields(&a);
                return st;
            }
            have_kind = 1;
        } else {
            if (t == (dsu_u16)DSU_TLV_ACTION_APP_ID) target_str = &a.app_id;
            else if (t == (dsu_u16)DSU_TLV_ACTION_DISPLAY_NAME) target_str = &a.display_name;
            else if (t == (dsu_u16)DSU_TLV_ACTION_EXEC_RELPATH) target_str = &a.exec_relpath;
            else if (t == (dsu_u16)DSU_TLV_ACTION_ARGUMENTS) target_str = &a.arguments;
            else if (t == (dsu_u16)DSU_TLV_ACTION_ICON_RELPATH) target_str = &a.icon_relpath;
            else if (t == (dsu_u16)DSU_TLV_ACTION_EXTENSION) target_str = &a.extension;
            else if (t == (dsu_u16)DSU_TLV_ACTION_PROTOCOL) target_str = &a.protocol;
            else if (t == (dsu_u16)DSU_TLV_ACTION_MARKER_RELPATH) target_str = &a.marker_relpath;
            else if (t == (dsu_u16)DSU_TLV_ACTION_CAPABILITY_ID) target_str = &a.capability_id;
            else if (t == (dsu_u16)DSU_TLV_ACTION_CAPABILITY_VALUE) target_str = &a.capability_value;
            else if (t == (dsu_u16)DSU_TLV_ACTION_PUBLISHER) target_str = &a.publisher;

            if (target_str) {
                if (*target_str) {
                    dsu__action_free_fields(&a);
                    return DSU_STATUS_PARSE_ERROR;
                }
                st = dsu__read_tlv_string(buf + start, n, target_str);
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__action_free_fields(&a);
                    return st;
                }
            }
        }

        off = start + n;
    }

    if (!have_version || version != 1u) {
        dsu__action_free_fields(&a);
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }
    if (!have_kind) {
        dsu__action_free_fields(&a);
        return DSU_STATUS_PARSE_ERROR;
    }
    if (kind > (dsu_u8)DSU_MANIFEST_ACTION_DECLARE_CAPABILITY) {
        dsu__action_free_fields(&a);
        return DSU_STATUS_PARSE_ERROR;
    }
    a.kind = kind;

    /* Minimal kind-specific validation + canonicalization for id/path-like fields. */
    if (kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_APP_ENTRY) {
        if (!a.app_id || !a.display_name || !a.exec_relpath) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
        if (dsu__normalize_id_inplace(a.app_id) != DSU_STATUS_SUCCESS) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
        dsu__normalize_path_inplace(a.exec_relpath);
        dsu__normalize_path_inplace(a.icon_relpath);
    } else if (kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_FILE_ASSOC) {
        if (!a.extension || !a.app_id) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
        if (dsu__normalize_id_inplace(a.app_id) != DSU_STATUS_SUCCESS) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
        (void)dsu__ascii_to_lower_inplace(a.extension);
        if (a.extension[0] != '.') {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
    } else if (kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_URL_HANDLER) {
        if (!a.protocol || !a.app_id) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
        if (dsu__normalize_id_inplace(a.app_id) != DSU_STATUS_SUCCESS) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
        (void)dsu__ascii_to_lower_inplace(a.protocol);
        if (!dsu__is_ascii_id(a.protocol)) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
    } else if (kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_UNINSTALL_ENTRY) {
        if (!a.display_name) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
    } else if (kind == (dsu_u8)DSU_MANIFEST_ACTION_WRITE_FIRST_RUN_MARKER) {
        if (!a.marker_relpath) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
        dsu__normalize_path_inplace(a.marker_relpath);
    } else if (kind == (dsu_u8)DSU_MANIFEST_ACTION_DECLARE_CAPABILITY) {
        if (!a.capability_id || !a.capability_value) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
        if (dsu__normalize_id_inplace(a.capability_id) != DSU_STATUS_SUCCESS) {
            dsu__action_free_fields(&a);
            return DSU_STATUS_PARSE_ERROR;
        }
    }

    *out_a = a;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__parse_component_container(const dsu_u8 *buf,
                                                  dsu_u32 len,
                                                  dsu_manifest_component_t *out_c) {
    dsu_u32 off = 0u;
    dsu_u32 version = 0u;
    char *id = NULL;
    char *verstr = NULL;
    dsu_u8 kind = 0u;
    dsu_u32 flags = 0u;
    int have_version = 0;
    int have_id = 0;
    int have_kind = 0;
    dsu_manifest_component_t c;
    dsu_status_t st;

    if (!buf || !out_c) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(&c, 0, sizeof(c));

    while (off < len) {
        dsu_u16 t;
        dsu_u32 n;
        dsu_u32 start;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        start = off;

        if (t == (dsu_u16)DSU_TLV_COMPONENT_VERSION) {
            if (have_version) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_u32(buf + start, n, &version);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_version = 1;
        } else if (t == (dsu_u16)DSU_TLV_COMPONENT_ID) {
            if (have_id) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_string(buf + start, n, &id);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_id = 1;
        } else if (t == (dsu_u16)DSU_TLV_COMPONENT_VERSTR) {
            if (verstr) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_string(buf + start, n, &verstr);
            if (st != DSU_STATUS_SUCCESS) goto fail;
        } else if (t == (dsu_u16)DSU_TLV_COMPONENT_KIND) {
            if (have_kind) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__read_tlv_u8(buf + start, n, &kind);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            have_kind = 1;
        } else if (t == (dsu_u16)DSU_TLV_COMPONENT_FLAGS) {
            st = dsu__read_tlv_u32(buf + start, n, &flags);
            if (st != DSU_STATUS_SUCCESS) goto fail;
        } else if (t == (dsu_u16)DSU_TLV_DEPENDENCY) {
            dsu_manifest_dependency_t dep;
            memset(&dep, 0, sizeof(dep));
            st = dsu__parse_dependency_container(buf + start, n, &dep);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            st = dsu__component_dep_push(&c, &dep);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(dep.id);
                dsu__free(dep.constraint_version);
                goto fail;
            }
        } else if (t == (dsu_u16)DSU_TLV_CONFLICT) {
            char *cid = NULL;
            st = dsu__read_tlv_string(buf + start, n, &cid);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            st = dsu__component_conflict_push(&c, cid);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(cid);
                goto fail;
            }
        } else if (t == (dsu_u16)DSU_TLV_PAYLOAD) {
            dsu_manifest_payload_t p;
            memset(&p, 0, sizeof(p));
            st = dsu__parse_payload_container(buf + start, n, &p);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            st = dsu__component_payload_push(&c, &p);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(p.path);
                goto fail;
            }
        } else if (t == (dsu_u16)DSU_TLV_ACTION) {
            dsu_manifest_action_t a;
            memset(&a, 0, sizeof(a));
            st = dsu__parse_action_container(buf + start, n, &a);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            st = dsu__component_action_push(&c, &a);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__action_free_fields(&a);
                goto fail;
            }
        }

        off = start + n;
    }

    if (!have_version || version != 1u) {
        st = DSU_STATUS_UNSUPPORTED_VERSION;
        goto fail;
    }
    if (!have_id || !have_kind) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }
    if (kind > (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }
    if (verstr && verstr[0] == '\0') {
        dsu__free(verstr);
        verstr = NULL;
    }
    if (verstr && !dsu__is_semverish(verstr)) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }

    c.id = id;
    c.version = verstr;
    c.kind = kind;
    c.flags = flags;
    *out_c = c;
    return DSU_STATUS_SUCCESS;

fail:
    dsu__free(id);
    dsu__free(verstr);
    dsu__manifest_component_free(&c);
    return st;
}

static dsu_status_t dsu__parse_uninstall_policy_container(const dsu_u8 *buf,
                                                         dsu_u32 len,
                                                         dsu_manifest_uninstall_policy_t *out_p) {
    dsu_u32 off = 0u;
    dsu_u32 version = 0u;
    dsu_u8 remove_owned = 0u;
    dsu_u8 preserve_user = 1u;
    dsu_u8 preserve_cache = 1u;
    int have_version = 0;
    int have_remove_owned = 0;
    int have_preserve_user = 0;
    int have_preserve_cache = 0;
    dsu_status_t st;

    if (!buf || !out_p) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(out_p, 0, sizeof(*out_p));

    while (off < len) {
        dsu_u16 t;
        dsu_u32 n;
        dsu_u32 start;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) return st;
        start = off;
        if (t == (dsu_u16)DSU_TLV_POLICY_VERSION) {
            if (have_version) return DSU_STATUS_PARSE_ERROR;
            st = dsu__read_tlv_u32(buf + start, n, &version);
            if (st != DSU_STATUS_SUCCESS) return st;
            have_version = 1;
        } else if (t == (dsu_u16)DSU_TLV_POLICY_REMOVE_OWNED) {
            if (have_remove_owned) return DSU_STATUS_PARSE_ERROR;
            st = dsu__read_tlv_u8(buf + start, n, &remove_owned);
            if (st != DSU_STATUS_SUCCESS) return st;
            have_remove_owned = 1;
        } else if (t == (dsu_u16)DSU_TLV_POLICY_PRESERVE_USER_DATA) {
            if (have_preserve_user) return DSU_STATUS_PARSE_ERROR;
            st = dsu__read_tlv_u8(buf + start, n, &preserve_user);
            if (st != DSU_STATUS_SUCCESS) return st;
            have_preserve_user = 1;
        } else if (t == (dsu_u16)DSU_TLV_POLICY_PRESERVE_CACHE) {
            if (have_preserve_cache) return DSU_STATUS_PARSE_ERROR;
            st = dsu__read_tlv_u8(buf + start, n, &preserve_cache);
            if (st != DSU_STATUS_SUCCESS) return st;
            have_preserve_cache = 1;
        }
        off = start + n;
    }

    if (!have_version || version != 1u) {
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }
    if (!have_remove_owned || !have_preserve_user || !have_preserve_cache) {
        return DSU_STATUS_PARSE_ERROR;
    }

    out_p->remove_owned_files = (remove_owned != 0u) ? 1u : 0u;
    out_p->preserve_user_data = (preserve_user != 0u) ? 1u : 0u;
    out_p->preserve_cache = (preserve_cache != 0u) ? 1u : 0u;
    out_p->present = 1u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__manifest_parse_root(dsu_manifest_t *m, const dsu_u8 *buf, dsu_u32 len) {
    dsu_u32 off = 0u;
    dsu_status_t st;

    if (!m || !buf) {
        return DSU_STATUS_INVALID_ARGS;
    }

    while (off < len) {
        dsu_u16 t;
        dsu_u32 n;
        dsu_u32 start;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        start = off;

        if (t == (dsu_u16)DSU_TLV_ROOT_VERSION) {
            if (m->root_version != 0u) {
                return DSU_STATUS_PARSE_ERROR;
            }
            st = dsu__read_tlv_u32(buf + start, n, &m->root_version);
            if (st != DSU_STATUS_SUCCESS) return st;
            if (m->root_version != DSU_MANIFEST_ROOT_SCHEMA_VERSION) {
                return DSU_STATUS_UNSUPPORTED_VERSION;
            }
        } else if (t == (dsu_u16)DSU_TLV_PRODUCT_ID) {
            if (m->product_id) {
                return DSU_STATUS_PARSE_ERROR;
            }
            st = dsu__read_tlv_string(buf + start, n, &m->product_id);
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (t == (dsu_u16)DSU_TLV_PRODUCT_VERSION) {
            if (m->product_version) {
                return DSU_STATUS_PARSE_ERROR;
            }
            st = dsu__read_tlv_string(buf + start, n, &m->product_version);
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (t == (dsu_u16)DSU_TLV_BUILD_CHANNEL) {
            if (m->build_channel) {
                return DSU_STATUS_PARSE_ERROR;
            }
            st = dsu__read_tlv_string(buf + start, n, &m->build_channel);
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (t == (dsu_u16)DSU_TLV_PLATFORM_TARGET) {
            char *tmp = NULL;
            st = dsu__read_tlv_string(buf + start, n, &tmp);
            if (st != DSU_STATUS_SUCCESS) return st;
            st = dsu__str_list_push(&m->platform_targets,
                                    &m->platform_target_count,
                                    &m->platform_target_cap,
                                    tmp);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(tmp);
                return st;
            }
        } else if (t == (dsu_u16)DSU_TLV_DEFAULT_INSTALL_ROOT) {
            dsu_manifest_install_root_t r;
            memset(&r, 0, sizeof(r));
            st = dsu__parse_install_root_container(buf + start, n, &r);
            if (st != DSU_STATUS_SUCCESS) {
                return st;
            }
            st = dsu__install_root_push(m, &r);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(r.platform);
                dsu__free(r.path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_TLV_COMPONENT) {
            dsu_manifest_component_t c;
            memset(&c, 0, sizeof(c));
            st = dsu__parse_component_container(buf + start, n, &c);
            if (st != DSU_STATUS_SUCCESS) {
                return st;
            }
            st = dsu__component_push(m, &c);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__manifest_component_free(&c);
                return st;
            }
        } else if (t == (dsu_u16)DSU_TLV_UNINSTALL_POLICY) {
            if (m->uninstall_policy.present) {
                return DSU_STATUS_PARSE_ERROR;
            }
            st = dsu__parse_uninstall_policy_container(buf + start, n, &m->uninstall_policy);
            if (st != DSU_STATUS_SUCCESS) {
                return st;
            }
        }

        off = start + n;
    }

    return DSU_STATUS_SUCCESS;
}

static int dsu__install_root_cmp(const dsu_manifest_install_root_t *a, const dsu_manifest_install_root_t *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    c = dsu__strcmp_bytes(a->platform, b->platform);
    if (c != 0) return c;
    if (a->scope != b->scope) return (a->scope < b->scope) ? -1 : 1;
    return dsu__strcmp_bytes(a->path, b->path);
}

static void dsu__sort_install_roots(dsu_manifest_install_root_t *items, dsu_u32 count) {
    dsu_u32 i;
    if (!items || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dsu_manifest_install_root_t key = items[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__install_root_cmp(&items[j - 1u], &key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

static int dsu__component_cmp(const dsu_manifest_component_t *a, const dsu_manifest_component_t *b) {
    return dsu__strcmp_bytes(a ? a->id : NULL, b ? b->id : NULL);
}

static void dsu__sort_components(dsu_manifest_component_t *items, dsu_u32 count) {
    dsu_u32 i;
    if (!items || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dsu_manifest_component_t key = items[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__component_cmp(&items[j - 1u], &key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

static int dsu__dep_cmp(const dsu_manifest_dependency_t *a, const dsu_manifest_dependency_t *b) {
    int c;
    c = dsu__strcmp_bytes(a ? a->id : NULL, b ? b->id : NULL);
    if (c != 0) return c;
    if (a->constraint_kind != b->constraint_kind) return (a->constraint_kind < b->constraint_kind) ? -1 : 1;
    return dsu__strcmp_bytes(a->constraint_version, b->constraint_version);
}

static void dsu__sort_deps(dsu_manifest_dependency_t *items, dsu_u32 count) {
    dsu_u32 i;
    if (!items || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dsu_manifest_dependency_t key = items[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__dep_cmp(&items[j - 1u], &key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

static int dsu__payload_cmp(const dsu_manifest_payload_t *a, const dsu_manifest_payload_t *b) {
    int c;
    if (a->kind != b->kind) return (a->kind < b->kind) ? -1 : 1;
    c = dsu__strcmp_bytes(a->path, b->path);
    if (c != 0) return c;
    return memcmp(a->sha256, b->sha256, 32u);
}

static void dsu__sort_payloads(dsu_manifest_payload_t *items, dsu_u32 count) {
    dsu_u32 i;
    if (!items || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dsu_manifest_payload_t key = items[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__payload_cmp(&items[j - 1u], &key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

static int dsu__action_cmp(const dsu_manifest_action_t *a, const dsu_manifest_action_t *b) {
    int c;
    if (a->kind != b->kind) return (a->kind < b->kind) ? -1 : 1;
    if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_APP_ENTRY) {
        c = dsu__strcmp_bytes(a->app_id, b->app_id);
        if (c != 0) return c;
        return dsu__strcmp_bytes(a->exec_relpath, b->exec_relpath);
    }
    if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_FILE_ASSOC) {
        c = dsu__strcmp_bytes(a->extension, b->extension);
        if (c != 0) return c;
        return dsu__strcmp_bytes(a->app_id, b->app_id);
    }
    if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_URL_HANDLER) {
        c = dsu__strcmp_bytes(a->protocol, b->protocol);
        if (c != 0) return c;
        return dsu__strcmp_bytes(a->app_id, b->app_id);
    }
    if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_UNINSTALL_ENTRY) {
        c = dsu__strcmp_bytes(a->display_name, b->display_name);
        if (c != 0) return c;
        return dsu__strcmp_bytes(a->publisher, b->publisher);
    }
    if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_WRITE_FIRST_RUN_MARKER) {
        return dsu__strcmp_bytes(a->marker_relpath, b->marker_relpath);
    }
    if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_DECLARE_CAPABILITY) {
        c = dsu__strcmp_bytes(a->capability_id, b->capability_id);
        if (c != 0) return c;
        return dsu__strcmp_bytes(a->capability_value, b->capability_value);
    }
    return 0;
}

static void dsu__sort_actions(dsu_manifest_action_t *items, dsu_u32 count) {
    dsu_u32 i;
    if (!items || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dsu_manifest_action_t key = items[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__action_cmp(&items[j - 1u], &key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

dsu_status_t dsu_manifest_canonicalize(dsu_manifest_t *m) {
    dsu_u32 i;
    dsu_u32 j;

    if (!m) {
        return DSU_STATUS_INVALID_ARGS;
    }

    if (m->product_id) {
        if (dsu__normalize_id_inplace(m->product_id) != DSU_STATUS_SUCCESS) {
            return DSU_STATUS_PARSE_ERROR;
        }
    }
    if (m->product_version) {
        (void)dsu__ascii_to_lower_inplace(m->product_version);
    }
    if (m->build_channel) {
        if (dsu__normalize_id_inplace(m->build_channel) != DSU_STATUS_SUCCESS) {
            return DSU_STATUS_PARSE_ERROR;
        }
    }

    for (i = 0u; i < m->platform_target_count; ++i) {
        if (!m->platform_targets[i]) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (dsu__normalize_id_inplace(m->platform_targets[i]) != DSU_STATUS_SUCCESS) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (!dsu__is_platform_triple(m->platform_targets[i])) {
            return DSU_STATUS_PARSE_ERROR;
        }
    }
    dsu__sort_str_ptrs(m->platform_targets, m->platform_target_count);
    /* Unique platform targets. */
    {
        dsu_u32 w = 0u;
        for (i = 0u; i < m->platform_target_count; ++i) {
            if (w == 0u || dsu__strcmp_bytes(m->platform_targets[w - 1u], m->platform_targets[i]) != 0) {
                m->platform_targets[w++] = m->platform_targets[i];
            } else {
                dsu__free(m->platform_targets[i]);
            }
        }
        m->platform_target_count = w;
    }

    for (i = 0u; i < m->install_root_count; ++i) {
        dsu_manifest_install_root_t *r = &m->install_roots[i];
        if (!r->platform || !r->path) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (dsu__normalize_id_inplace(r->platform) != DSU_STATUS_SUCCESS) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (!dsu__is_platform_triple(r->platform)) {
            return DSU_STATUS_PARSE_ERROR;
        }
        dsu__normalize_path_inplace(r->path);
    }
    dsu__sort_install_roots(m->install_roots, m->install_root_count);
    /* Unique install roots. */
    {
        dsu_u32 w = 0u;
        for (i = 0u; i < m->install_root_count; ++i) {
            if (w == 0u || dsu__install_root_cmp(&m->install_roots[w - 1u], &m->install_roots[i]) != 0) {
                m->install_roots[w++] = m->install_roots[i];
            } else {
                dsu__free(m->install_roots[i].platform);
                dsu__free(m->install_roots[i].path);
            }
        }
        m->install_root_count = w;
    }

    for (i = 0u; i < m->component_count; ++i) {
        dsu_manifest_component_t *c = &m->components[i];
        if (!c->id) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (dsu__normalize_id_inplace(c->id) != DSU_STATUS_SUCCESS) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (c->version) {
            (void)dsu__ascii_to_lower_inplace(c->version);
        }
        for (j = 0u; j < c->dep_count; ++j) {
            if (!c->deps[j].id || dsu__normalize_id_inplace(c->deps[j].id) != DSU_STATUS_SUCCESS) {
                return DSU_STATUS_PARSE_ERROR;
            }
            if (c->deps[j].constraint_version) {
                (void)dsu__ascii_to_lower_inplace(c->deps[j].constraint_version);
            }
        }
        for (j = 0u; j < c->conflict_count; ++j) {
            if (!c->conflicts[j] || dsu__normalize_id_inplace(c->conflicts[j]) != DSU_STATUS_SUCCESS) {
                return DSU_STATUS_PARSE_ERROR;
            }
        }
        for (j = 0u; j < c->payload_count; ++j) {
            dsu__normalize_path_inplace(c->payloads[j].path);
        }
        for (j = 0u; j < c->action_count; ++j) {
            if (c->actions[j].app_id) (void)dsu__normalize_id_inplace(c->actions[j].app_id);
            if (c->actions[j].capability_id) (void)dsu__normalize_id_inplace(c->actions[j].capability_id);
            dsu__normalize_path_inplace(c->actions[j].exec_relpath);
            dsu__normalize_path_inplace(c->actions[j].icon_relpath);
            dsu__normalize_path_inplace(c->actions[j].marker_relpath);
        }
    }

    dsu__sort_components(m->components, m->component_count);
    for (i = 0u; i < m->component_count; ++i) {
        dsu_manifest_component_t *c = &m->components[i];
        dsu__sort_deps(c->deps, c->dep_count);
        dsu__sort_str_ptrs(c->conflicts, c->conflict_count);
        dsu__sort_payloads(c->payloads, c->payload_count);
        dsu__sort_actions(c->actions, c->action_count);

        /* Unique conflicts */
        {
            dsu_u32 w = 0u;
            for (j = 0u; j < c->conflict_count; ++j) {
                if (w == 0u || dsu__strcmp_bytes(c->conflicts[w - 1u], c->conflicts[j]) != 0) {
                    c->conflicts[w++] = c->conflicts[j];
                } else {
                    dsu__free(c->conflicts[j]);
                }
            }
            c->conflict_count = w;
        }
        /* Unique deps */
        {
            dsu_u32 w = 0u;
            for (j = 0u; j < c->dep_count; ++j) {
                if (w == 0u || dsu__dep_cmp(&c->deps[w - 1u], &c->deps[j]) != 0) {
                    c->deps[w++] = c->deps[j];
                } else {
                    dsu__free(c->deps[j].id);
                    dsu__free(c->deps[j].constraint_version);
                }
            }
            c->dep_count = w;
        }
        /* Unique payloads */
        {
            dsu_u32 w = 0u;
            for (j = 0u; j < c->payload_count; ++j) {
                if (w == 0u || dsu__payload_cmp(&c->payloads[w - 1u], &c->payloads[j]) != 0) {
                    c->payloads[w++] = c->payloads[j];
                } else {
                    dsu__free(c->payloads[j].path);
                }
            }
            c->payload_count = w;
        }
        /* Unique actions */
        {
            dsu_u32 w = 0u;
            for (j = 0u; j < c->action_count; ++j) {
                if (w == 0u || dsu__action_cmp(&c->actions[w - 1u], &c->actions[j]) != 0) {
                    c->actions[w++] = c->actions[j];
                } else {
                    dsu__action_free_fields(&c->actions[j]);
                }
            }
            c->action_count = w;
        }
    }

    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_manifest_validate(const dsu_manifest_t *m) {
    dsu_u32 i;
    dsu_u32 j;

    if (!m) {
        return DSU_STATUS_INVALID_ARGS;
    }

    if (m->root_version == 0u) {
        return DSU_STATUS_PARSE_ERROR;
    }
    if (m->root_version != DSU_MANIFEST_ROOT_SCHEMA_VERSION) {
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }
    if (!m->product_id || !dsu__is_ascii_id(m->product_id)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    if (!m->product_version || !dsu__is_semverish(m->product_version)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    if (!m->build_channel || !dsu__is_ascii_id(m->build_channel)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    if (!(dsu__streq(m->build_channel, "stable") || dsu__streq(m->build_channel, "beta") ||
          dsu__streq(m->build_channel, "dev") || dsu__streq(m->build_channel, "nightly"))) {
        return DSU_STATUS_PARSE_ERROR;
    }
    if (m->platform_target_count == 0u) {
        return DSU_STATUS_PARSE_ERROR;
    }
    for (i = 0u; i < m->platform_target_count; ++i) {
        if (!m->platform_targets[i] || !dsu__is_platform_triple(m->platform_targets[i])) {
            return DSU_STATUS_PARSE_ERROR;
        }
    }
    if (m->install_root_count == 0u) {
        return DSU_STATUS_PARSE_ERROR;
    }
    for (i = 0u; i < m->platform_target_count; ++i) {
        const char *plat = m->platform_targets[i];
        int found = 0;
        for (j = 0u; j < m->install_root_count; ++j) {
            if (dsu__streq(m->install_roots[j].platform, plat)) {
                found = 1;
                break;
            }
        }
        if (!found) {
            return DSU_STATUS_PARSE_ERROR;
        }
    }

    if (m->component_count == 0u) {
        return DSU_STATUS_PARSE_ERROR;
    }
    for (i = 0u; i < m->component_count; ++i) {
        const dsu_manifest_component_t *c = &m->components[i];
        if (!c->id || !dsu__is_ascii_id(c->id)) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (i > 0u && dsu__streq(m->components[i - 1u].id, c->id)) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (c->version && !dsu__is_semverish(c->version)) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (c->kind > (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER) {
            return DSU_STATUS_PARSE_ERROR;
        }
        for (j = 0u; j < c->dep_count; ++j) {
            const char *dep_id = c->deps[j].id;
            dsu_u32 k;
            int found = 0;
            if (!dep_id || !dsu__is_ascii_id(dep_id)) {
                return DSU_STATUS_PARSE_ERROR;
            }
            for (k = 0u; k < m->component_count; ++k) {
                if (dsu__streq(m->components[k].id, dep_id)) {
                    found = 1;
                    break;
                }
            }
            if (!found && !dsu__is_external_component_id(dep_id)) {
                return DSU_STATUS_PARSE_ERROR;
            }
            if (c->deps[j].constraint_kind != (dsu_u8)DSU_MANIFEST_VERSION_CONSTRAINT_ANY &&
                (!c->deps[j].constraint_version || !dsu__is_semverish(c->deps[j].constraint_version))) {
                return DSU_STATUS_PARSE_ERROR;
            }
        }
        for (j = 0u; j < c->conflict_count; ++j) {
            const char *cid = c->conflicts[j];
            dsu_u32 k;
            int found = 0;
            if (!cid || !dsu__is_ascii_id(cid)) {
                return DSU_STATUS_PARSE_ERROR;
            }
            for (k = 0u; k < m->component_count; ++k) {
                if (dsu__streq(m->components[k].id, cid)) {
                    found = 1;
                    break;
                }
            }
            if (!found) {
                return DSU_STATUS_PARSE_ERROR;
            }
        }
        for (j = 0u; j < c->payload_count; ++j) {
            const dsu_manifest_payload_t *p = &c->payloads[j];
            if (p->kind > (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_BLOB) {
                return DSU_STATUS_PARSE_ERROR;
            }
            if (!p->has_sha256) {
                return DSU_STATUS_PARSE_ERROR;
            }
            if ((p->kind == (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_FILESET ||
                 p->kind == (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_ARCHIVE) &&
                (!p->path || p->path[0] == '\0')) {
                return DSU_STATUS_PARSE_ERROR;
            }
        }
        for (j = 0u; j < c->action_count; ++j) {
            const dsu_manifest_action_t *a = &c->actions[j];
            if (a->kind > (dsu_u8)DSU_MANIFEST_ACTION_DECLARE_CAPABILITY) {
                return DSU_STATUS_PARSE_ERROR;
            }
            if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_APP_ENTRY) {
                if (!a->app_id || !a->display_name || !a->exec_relpath) return DSU_STATUS_PARSE_ERROR;
            } else if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_FILE_ASSOC) {
                if (!a->extension || !a->app_id) return DSU_STATUS_PARSE_ERROR;
            } else if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_URL_HANDLER) {
                if (!a->protocol || !a->app_id) return DSU_STATUS_PARSE_ERROR;
            } else if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_UNINSTALL_ENTRY) {
                if (!a->display_name) return DSU_STATUS_PARSE_ERROR;
            } else if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_WRITE_FIRST_RUN_MARKER) {
                if (!a->marker_relpath) return DSU_STATUS_PARSE_ERROR;
            } else if (a->kind == (dsu_u8)DSU_MANIFEST_ACTION_DECLARE_CAPABILITY) {
                if (!a->capability_id || !a->capability_value) return DSU_STATUS_PARSE_ERROR;
            }
        }
    }

    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__blob_put_tlv_u8(dsu_blob_t *b, dsu_u16 t, dsu_u8 v) {
    return dsu__blob_put_tlv(b, t, &v, 1u);
}

static dsu_status_t dsu__blob_put_tlv_u32(dsu_blob_t *b, dsu_u16 t, dsu_u32 v) {
    dsu_u8 tmp[4];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    return dsu__blob_put_tlv(b, t, tmp, 4u);
}

static dsu_status_t dsu__blob_put_tlv_u64(dsu_blob_t *b, dsu_u16 t, dsu_u64 v) {
    dsu_u8 tmp[8];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    tmp[4] = (dsu_u8)((v >> 32) & 0xFFu);
    tmp[5] = (dsu_u8)((v >> 40) & 0xFFu);
    tmp[6] = (dsu_u8)((v >> 48) & 0xFFu);
    tmp[7] = (dsu_u8)((v >> 56) & 0xFFu);
    return dsu__blob_put_tlv(b, t, tmp, 8u);
}

static dsu_status_t dsu__blob_put_tlv_cstr(dsu_blob_t *b, dsu_u16 t, const char *s) {
    dsu_u32 n;
    if (!b || !s) {
        return DSU_STATUS_INVALID_ARGS;
    }
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INTERNAL_ERROR;
    }
    return dsu__blob_put_tlv(b, t, s, n);
}

static dsu_status_t dsu__manifest_serialize_payload(const dsu_manifest_t *m, dsu_blob_t *out_payload) {
    dsu_blob_t root;
    dsu_u32 i;
    dsu_u32 j;
    dsu_status_t st;

    if (!m || !out_payload) {
        return DSU_STATUS_INVALID_ARGS;
    }

    dsu__blob_init(&root);
    dsu__blob_init(out_payload);

    st = dsu__blob_put_tlv_u32(&root, (dsu_u16)DSU_TLV_ROOT_VERSION, DSU_MANIFEST_ROOT_SCHEMA_VERSION);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    st = dsu__blob_put_tlv_cstr(&root, (dsu_u16)DSU_TLV_PRODUCT_ID, m->product_id ? m->product_id : "");
    if (st != DSU_STATUS_SUCCESS) goto fail;
    st = dsu__blob_put_tlv_cstr(&root, (dsu_u16)DSU_TLV_PRODUCT_VERSION, m->product_version ? m->product_version : "");
    if (st != DSU_STATUS_SUCCESS) goto fail;
    st = dsu__blob_put_tlv_cstr(&root, (dsu_u16)DSU_TLV_BUILD_CHANNEL, m->build_channel ? m->build_channel : "");
    if (st != DSU_STATUS_SUCCESS) goto fail;

    for (i = 0u; i < m->platform_target_count; ++i) {
        st = dsu__blob_put_tlv_cstr(&root, (dsu_u16)DSU_TLV_PLATFORM_TARGET, m->platform_targets[i]);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }
    for (i = 0u; i < m->install_root_count; ++i) {
        dsu_blob_t b;
        const dsu_manifest_install_root_t *r = &m->install_roots[i];
        dsu__blob_init(&b);
        st = dsu__blob_put_tlv_u32(&b, (dsu_u16)DSU_TLV_INSTALL_ROOT_VERSION, 1u);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&b, (dsu_u16)DSU_TLV_INSTALL_SCOPE, r->scope);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_cstr(&b, (dsu_u16)DSU_TLV_INSTALL_PLATFORM, r->platform);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_cstr(&b, (dsu_u16)DSU_TLV_INSTALL_PATH, r->path);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&root, (dsu_u16)DSU_TLV_DEFAULT_INSTALL_ROOT, b.data, b.size);
        dsu__blob_free(&b);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }

    for (i = 0u; i < m->component_count; ++i) {
        const dsu_manifest_component_t *c = &m->components[i];
        dsu_blob_t cb;
        dsu__blob_init(&cb);
        st = dsu__blob_put_tlv_u32(&cb, (dsu_u16)DSU_TLV_COMPONENT_VERSION, 1u);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_cstr(&cb, (dsu_u16)DSU_TLV_COMPONENT_ID, c->id);
        if (st == DSU_STATUS_SUCCESS && c->version) st = dsu__blob_put_tlv_cstr(&cb, (dsu_u16)DSU_TLV_COMPONENT_VERSTR, c->version);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&cb, (dsu_u16)DSU_TLV_COMPONENT_KIND, c->kind);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u32(&cb, (dsu_u16)DSU_TLV_COMPONENT_FLAGS, c->flags);

        for (j = 0u; j < c->dep_count && st == DSU_STATUS_SUCCESS; ++j) {
            const dsu_manifest_dependency_t *d = &c->deps[j];
            dsu_blob_t db;
            dsu__blob_init(&db);
            st = dsu__blob_put_tlv_u32(&db, (dsu_u16)DSU_TLV_DEP_VERSION, 1u);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_cstr(&db, (dsu_u16)DSU_TLV_DEP_COMPONENT_ID, d->id);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&db, (dsu_u16)DSU_TLV_DEP_CONSTRAINT_KIND, d->constraint_kind);
            if (st == DSU_STATUS_SUCCESS && d->constraint_version) {
                st = dsu__blob_put_tlv_cstr(&db, (dsu_u16)DSU_TLV_DEP_CONSTRAINT_VERSION, d->constraint_version);
            }
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&cb, (dsu_u16)DSU_TLV_DEPENDENCY, db.data, db.size);
            dsu__blob_free(&db);
        }

        for (j = 0u; j < c->conflict_count && st == DSU_STATUS_SUCCESS; ++j) {
            st = dsu__blob_put_tlv_cstr(&cb, (dsu_u16)DSU_TLV_CONFLICT, c->conflicts[j]);
        }

        for (j = 0u; j < c->payload_count && st == DSU_STATUS_SUCCESS; ++j) {
            const dsu_manifest_payload_t *p = &c->payloads[j];
            dsu_blob_t pb;
            dsu__blob_init(&pb);
            st = dsu__blob_put_tlv_u32(&pb, (dsu_u16)DSU_TLV_PAYLOAD_VERSION, 1u);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&pb, (dsu_u16)DSU_TLV_PAYLOAD_KIND, p->kind);
            if (st == DSU_STATUS_SUCCESS && p->path) st = dsu__blob_put_tlv_cstr(&pb, (dsu_u16)DSU_TLV_PAYLOAD_PATH, p->path);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&pb, (dsu_u16)DSU_TLV_PAYLOAD_SHA256, p->sha256, 32u);
            if (st == DSU_STATUS_SUCCESS && p->has_size) st = dsu__blob_put_tlv_u64(&pb, (dsu_u16)DSU_TLV_PAYLOAD_SIZE, p->size);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&cb, (dsu_u16)DSU_TLV_PAYLOAD, pb.data, pb.size);
            dsu__blob_free(&pb);
        }

        for (j = 0u; j < c->action_count && st == DSU_STATUS_SUCCESS; ++j) {
            const dsu_manifest_action_t *a = &c->actions[j];
            dsu_blob_t ab;
            dsu__blob_init(&ab);
            st = dsu__blob_put_tlv_u32(&ab, (dsu_u16)DSU_TLV_ACTION_VERSION, 1u);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&ab, (dsu_u16)DSU_TLV_ACTION_KIND, a->kind);
            if (st == DSU_STATUS_SUCCESS && a->app_id) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_APP_ID, a->app_id);
            if (st == DSU_STATUS_SUCCESS && a->display_name) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_DISPLAY_NAME, a->display_name);
            if (st == DSU_STATUS_SUCCESS && a->exec_relpath) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_EXEC_RELPATH, a->exec_relpath);
            if (st == DSU_STATUS_SUCCESS && a->arguments) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_ARGUMENTS, a->arguments);
            if (st == DSU_STATUS_SUCCESS && a->icon_relpath) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_ICON_RELPATH, a->icon_relpath);
            if (st == DSU_STATUS_SUCCESS && a->extension) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_EXTENSION, a->extension);
            if (st == DSU_STATUS_SUCCESS && a->protocol) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_PROTOCOL, a->protocol);
            if (st == DSU_STATUS_SUCCESS && a->marker_relpath) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_MARKER_RELPATH, a->marker_relpath);
            if (st == DSU_STATUS_SUCCESS && a->capability_id) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_CAPABILITY_ID, a->capability_id);
            if (st == DSU_STATUS_SUCCESS && a->capability_value) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_CAPABILITY_VALUE, a->capability_value);
            if (st == DSU_STATUS_SUCCESS && a->publisher) st = dsu__blob_put_tlv_cstr(&ab, (dsu_u16)DSU_TLV_ACTION_PUBLISHER, a->publisher);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&cb, (dsu_u16)DSU_TLV_ACTION, ab.data, ab.size);
            dsu__blob_free(&ab);
        }

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&root, (dsu_u16)DSU_TLV_COMPONENT, cb.data, cb.size);
        dsu__blob_free(&cb);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }

    if (m->uninstall_policy.present) {
        dsu_blob_t ub;
        dsu__blob_init(&ub);
        st = dsu__blob_put_tlv_u32(&ub, (dsu_u16)DSU_TLV_POLICY_VERSION, 1u);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&ub, (dsu_u16)DSU_TLV_POLICY_REMOVE_OWNED, m->uninstall_policy.remove_owned_files);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&ub, (dsu_u16)DSU_TLV_POLICY_PRESERVE_USER_DATA, m->uninstall_policy.preserve_user_data);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&ub, (dsu_u16)DSU_TLV_POLICY_PRESERVE_CACHE, m->uninstall_policy.preserve_cache);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&root, (dsu_u16)DSU_TLV_UNINSTALL_POLICY, ub.data, ub.size);
        dsu__blob_free(&ub);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }

    st = dsu__blob_put_tlv(out_payload, (dsu_u16)DSU_TLV_MANIFEST_ROOT, root.data, root.size);
    if (st != DSU_STATUS_SUCCESS) goto fail;

    dsu__blob_free(&root);
    return DSU_STATUS_SUCCESS;

fail:
    dsu__blob_free(&root);
    dsu__blob_free(out_payload);
    return st;
}

dsu_status_t dsu_manifest_write_file(dsu_ctx_t *ctx, const dsu_manifest_t *manifest, const char *path) {
    dsu_u8 magic[4];
    dsu_blob_t payload;
    dsu_blob_t file_bytes;
    dsu_status_t st;

    if (!ctx || !manifest || !path) {
        return DSU_STATUS_INVALID_ARGS;
    }

    magic[0] = (dsu_u8)DSU_MANIFEST_MAGIC_0;
    magic[1] = (dsu_u8)DSU_MANIFEST_MAGIC_1;
    magic[2] = (dsu_u8)DSU_MANIFEST_MAGIC_2;
    magic[3] = (dsu_u8)DSU_MANIFEST_MAGIC_3;

    st = dsu__manifest_serialize_payload(manifest, &payload);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu__file_wrap_payload(magic,
                                (dsu_u16)DSU_MANIFEST_FORMAT_VERSION,
                                payload.data,
                                payload.size,
                                &file_bytes);
    dsu__blob_free(&payload);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu__fs_write_all(path, file_bytes.data, file_bytes.size);
    dsu__blob_free(&file_bytes);
    return st;
}

static dsu_status_t dsu__json_blob_append(dsu_blob_t *b, const char *s) {
    dsu_u32 n;
    if (!b || !s) {
        return DSU_STATUS_INVALID_ARGS;
    }
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INTERNAL_ERROR;
    }
    return dsu__blob_append(b, s, n);
}

static dsu_status_t dsu__json_put_u32(dsu_blob_t *b, dsu_u32 v) {
    char buf[16];
    char *p = buf + sizeof(buf);
    *--p = '\0';
    if (v == 0u) {
        *--p = '0';
    } else {
        while (v != 0u && p > buf) {
            *--p = (char)('0' + (v % 10u));
            v /= 10u;
        }
    }
    return dsu__json_blob_append(b, p);
}

static void dsu__u64_to_hex16(dsu_u64 v, char out[17]) {
    static const char hex[] = "0123456789abcdef";
    int i;
    for (i = 15; i >= 0; --i) {
        out[i] = hex[(unsigned int)(v & 0xFu)];
        v >>= 4;
    }
    out[16] = '\0';
}

static dsu_status_t dsu__json_put_u64_hex_string(dsu_blob_t *b, dsu_u64 v) {
    char hex16[17];
    dsu_status_t st;
    dsu__u64_to_hex16(v, hex16);
    st = dsu__json_blob_append(b, "\"0x");
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu__json_blob_append(b, hex16);
    if (st != DSU_STATUS_SUCCESS) return st;
    return dsu__json_blob_append(b, "\"");
}

static dsu_status_t dsu__json_put_escaped(dsu_blob_t *b, const char *s) {
    const unsigned char *p = (const unsigned char *)(s ? s : "");
    unsigned char c;
    dsu_status_t st;
    st = dsu__json_blob_append(b, "\"");
    if (st != DSU_STATUS_SUCCESS) return st;
    while ((c = *p++) != 0u) {
        if (c == '\\' || c == '"') {
            char two[2];
            two[0] = '\\';
            two[1] = (char)c;
            st = dsu__blob_append(b, two, 2u);
        } else if (c == '\b') {
            st = dsu__json_blob_append(b, "\\b");
        } else if (c == '\f') {
            st = dsu__json_blob_append(b, "\\f");
        } else if (c == '\n') {
            st = dsu__json_blob_append(b, "\\n");
        } else if (c == '\r') {
            st = dsu__json_blob_append(b, "\\r");
        } else if (c == '\t') {
            st = dsu__json_blob_append(b, "\\t");
        } else if (c < 0x20u) {
            static const char hex[] = "0123456789abcdef";
            char esc[6];
            esc[0] = '\\';
            esc[1] = 'u';
            esc[2] = '0';
            esc[3] = '0';
            esc[4] = hex[(c >> 4) & 0xFu];
            esc[5] = hex[c & 0xFu];
            st = dsu__blob_append(b, esc, 6u);
        } else {
            st = dsu__blob_append(b, (const char *)&c, 1u);
        }
        if (st != DSU_STATUS_SUCCESS) return st;
    }
    return dsu__json_blob_append(b, "\"");
}

static dsu_status_t dsu__json_put_sha256_hex(dsu_blob_t *b, const dsu_u8 sha256[32]) {
    static const char hex[] = "0123456789abcdef";
    char out[65];
    dsu_u32 i;
    for (i = 0u; i < 32u; ++i) {
        dsu_u8 v = sha256[i];
        out[i * 2u] = hex[(v >> 4) & 0xFu];
        out[i * 2u + 1u] = hex[v & 0xFu];
    }
    out[64] = '\0';
    return dsu__json_put_escaped(b, out);
}

static const char *dsu__scope_name(dsu_u8 scope) {
    if (scope == (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE) return "portable";
    if (scope == (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_USER) return "user";
    if (scope == (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) return "system";
    return "unknown";
}

static const char *dsu__component_kind_name(dsu_u8 kind) {
    if (kind == (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_LAUNCHER) return "launcher";
    if (kind == (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_RUNTIME) return "runtime";
    if (kind == (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_TOOLS) return "tools";
    if (kind == (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_PACK) return "pack";
    if (kind == (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_DRIVER) return "driver";
    return "other";
}

static const char *dsu__constraint_kind_name(dsu_u8 kind) {
    if (kind == (dsu_u8)DSU_MANIFEST_VERSION_CONSTRAINT_EXACT) return "exact";
    if (kind == (dsu_u8)DSU_MANIFEST_VERSION_CONSTRAINT_AT_LEAST) return "at_least";
    return "any";
}

static const char *dsu__payload_kind_name(dsu_u8 kind) {
    if (kind == (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_ARCHIVE) return "archive";
    if (kind == (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_BLOB) return "blob";
    return "fileset";
}

static const char *dsu__action_kind_name(dsu_u8 kind) {
    if (kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_APP_ENTRY) return "REGISTER_APP_ENTRY";
    if (kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_FILE_ASSOC) return "REGISTER_FILE_ASSOC";
    if (kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_URL_HANDLER) return "REGISTER_URL_HANDLER";
    if (kind == (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_UNINSTALL_ENTRY) return "REGISTER_UNINSTALL_ENTRY";
    if (kind == (dsu_u8)DSU_MANIFEST_ACTION_WRITE_FIRST_RUN_MARKER) return "WRITE_FIRST_RUN_MARKER";
    return "DECLARE_CAPABILITY";
}

dsu_status_t dsu_manifest_write_json_file(dsu_ctx_t *ctx, const dsu_manifest_t *m, const char *path) {
    dsu_blob_t b;
    dsu_status_t st;
    dsu_u32 i;
    dsu_u32 j;

    if (!ctx || !m || !path) {
        return DSU_STATUS_INVALID_ARGS;
    }

    dsu__blob_init(&b);

    st = dsu__json_blob_append(&b, "{\n");
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu__json_blob_append(&b, "  \"format_version\":");
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_u32(&b, DSU_MANIFEST_FORMAT_VERSION);
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"schema_version\":");
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_u32(&b, m->root_version);
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"product_id\":");
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, m->product_id ? m->product_id : "");
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"product_version\":");
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, m->product_version ? m->product_version : "");
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"build_channel\":");
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, m->build_channel ? m->build_channel : "");

    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"platform_targets\":[");
    for (i = 0u; i < m->platform_target_count && st == DSU_STATUS_SUCCESS; ++i) {
        if (i != 0u) st = dsu__json_blob_append(&b, ",");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, m->platform_targets[i]);
    }
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "]");

    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"default_install_roots\":[");
    for (i = 0u; i < m->install_root_count && st == DSU_STATUS_SUCCESS; ++i) {
        const dsu_manifest_install_root_t *r = &m->install_roots[i];
        if (i != 0u) st = dsu__json_blob_append(&b, ",");
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__json_blob_append(&b, "\n    {\"scope\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, dsu__scope_name(r->scope));
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"platform\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, r->platform ? r->platform : "");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"path\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, r->path ? r->path : "");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "}");
    }
    if (st == DSU_STATUS_SUCCESS && m->install_root_count) st = dsu__json_blob_append(&b, "\n  ]");
    else if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "]");

    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"components\":[");
    for (i = 0u; i < m->component_count && st == DSU_STATUS_SUCCESS; ++i) {
        const dsu_manifest_component_t *c = &m->components[i];
        if (i != 0u) st = dsu__json_blob_append(&b, ",");
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__json_blob_append(&b, "\n    {\"component_id\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, c->id ? c->id : "");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"component_version\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, c->version ? c->version : "");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"component_kind\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, dsu__component_kind_name(c->kind));
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"flags\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_u32(&b, c->flags);

        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"dependencies\":[");
        for (j = 0u; j < c->dep_count && st == DSU_STATUS_SUCCESS; ++j) {
            const dsu_manifest_dependency_t *d = &c->deps[j];
            if (j != 0u) st = dsu__json_blob_append(&b, ",");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_blob_append(&b, "{\"id\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, d->id ? d->id : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"constraint\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, dsu__constraint_kind_name(d->constraint_kind));
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"version\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, d->constraint_version ? d->constraint_version : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "}");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "]");

        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"conflicts\":[");
        for (j = 0u; j < c->conflict_count && st == DSU_STATUS_SUCCESS; ++j) {
            if (j != 0u) st = dsu__json_blob_append(&b, ",");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, c->conflicts[j]);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "]");

        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"payloads\":[");
        for (j = 0u; j < c->payload_count && st == DSU_STATUS_SUCCESS; ++j) {
            const dsu_manifest_payload_t *p = &c->payloads[j];
            if (j != 0u) st = dsu__json_blob_append(&b, ",");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_blob_append(&b, "{\"kind\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, dsu__payload_kind_name(p->kind));
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"path\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, p->path ? p->path : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"sha256\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_sha256_hex(&b, p->sha256);
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"size\":");
            if (st == DSU_STATUS_SUCCESS) {
                if (p->has_size) st = dsu__json_put_u64_hex_string(&b, p->size);
                else st = dsu__json_put_escaped(&b, "");
            }
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "}");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "]");

        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"actions\":[");
        for (j = 0u; j < c->action_count && st == DSU_STATUS_SUCCESS; ++j) {
            const dsu_manifest_action_t *a = &c->actions[j];
            if (j != 0u) st = dsu__json_blob_append(&b, ",");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_blob_append(&b, "{\"kind\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, dsu__action_kind_name(a->kind));
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"app_id\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->app_id ? a->app_id : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"display_name\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->display_name ? a->display_name : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"exec_relpath\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->exec_relpath ? a->exec_relpath : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"arguments\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->arguments ? a->arguments : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"icon_relpath\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->icon_relpath ? a->icon_relpath : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"extension\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->extension ? a->extension : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"protocol\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->protocol ? a->protocol : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"marker_relpath\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->marker_relpath ? a->marker_relpath : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"capability_id\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->capability_id ? a->capability_id : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"capability_value\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->capability_value ? a->capability_value : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"publisher\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, a->publisher ? a->publisher : "");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "}");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "]");

        if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "}");
    }
    if (st == DSU_STATUS_SUCCESS && m->component_count) st = dsu__json_blob_append(&b, "\n  ]");
    else if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "]");

    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"uninstall_policy\":");
    if (st == DSU_STATUS_SUCCESS) {
        if (!m->uninstall_policy.present) {
            st = dsu__json_blob_append(&b, "null");
        } else {
            st = dsu__json_blob_append(&b, "{\"remove_owned_files\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_u32(&b, (dsu_u32)m->uninstall_policy.remove_owned_files);
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"preserve_user_data\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_u32(&b, (dsu_u32)m->uninstall_policy.preserve_user_data);
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\"preserve_cache\":");
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_u32(&b, (dsu_u32)m->uninstall_policy.preserve_cache);
            if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "}");
        }
    }

    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"content_digest32\":");
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_u32(&b, m->content_digest32);
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, ",\n  \"content_digest64\":");
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_u64_hex_string(&b, m->content_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__json_blob_append(&b, "\n}\n");

done:
    if (st == DSU_STATUS_SUCCESS) {
        st = dsu__fs_write_all(path, b.data, b.size);
    }
    dsu__blob_free(&b);
    return st;
}

#if defined(DSU_MANIFEST_ENABLE_LEGACY_INI)
static char *dsu__legacy_trim(char *s) {
    char *end;
    unsigned char c;
    if (!s) {
        return s;
    }
    while ((c = (unsigned char)*s) != 0u) {
        if (c != ' ' && c != '\t') {
            break;
        }
        ++s;
    }
    end = s + strlen(s);
    while (end > s) {
        c = (unsigned char)end[-1];
        if (c != ' ' && c != '\t') {
            break;
        }
        end[-1] = '\0';
        --end;
    }
    return s;
}

static int dsu__legacy_is_comment_or_empty(const char *s) {
    unsigned char c;
    if (!s) {
        return 1;
    }
    while ((c = (unsigned char)*s) != 0u) {
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            ++s;
            continue;
        }
        if (c == '#' || c == ';') {
            return 1;
        }
        return 0;
    }
    return 1;
}

static dsu_status_t dsu__legacy_parse_string_value(const char *value, char **out_str) {
    const char *p;
    const char *q;
    dsu_u32 n;
    char *out;

    if (!value || !out_str) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_str = NULL;

    p = value;
    while (*p == ' ' || *p == '\t') {
        ++p;
    }
    if (*p == '"') {
        ++p;
        q = p;
        while (*q && *q != '"') {
            unsigned char c = (unsigned char)*q;
            if (c < 0x20u || c > 0x7Eu) {
                return DSU_STATUS_PARSE_ERROR;
            }
            ++q;
        }
        if (*q != '"') {
            return DSU_STATUS_PARSE_ERROR;
        }
        n = (dsu_u32)(q - p);
        ++q;
        while (*q == ' ' || *q == '\t') {
            ++q;
        }
        if (*q != '\0') {
            return DSU_STATUS_PARSE_ERROR;
        }
        out = (char *)dsu__malloc(n + 1u);
        if (!out) {
            return DSU_STATUS_IO_ERROR;
        }
        if (n) {
            memcpy(out, p, (size_t)n);
        }
        out[n] = '\0';
        *out_str = out;
        return DSU_STATUS_SUCCESS;
    }

    q = p;
    while (*q) {
        unsigned char c = (unsigned char)*q;
        if (c < 0x21u || c > 0x7Eu) {
            return DSU_STATUS_PARSE_ERROR;
        }
        ++q;
    }
    if (q == p) {
        return DSU_STATUS_PARSE_ERROR;
    }
    n = (dsu_u32)(q - p);
    out = (char *)dsu__malloc(n + 1u);
    if (!out) {
        return DSU_STATUS_IO_ERROR;
    }
    memcpy(out, p, (size_t)n);
    out[n] = '\0';
    *out_str = out;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__legacy_parse_components_value(const char *value,
                                                      char ***out_items,
                                                      dsu_u32 *out_count,
                                                      dsu_u32 *out_cap) {
    const char *p;
    dsu_status_t st;

    if (!value || !out_items || !out_count || !out_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_items = NULL;
    *out_count = 0u;
    *out_cap = 0u;

    p = value;
    while (*p == ' ' || *p == '\t') {
        ++p;
    }
    if (*p != '[') {
        return DSU_STATUS_PARSE_ERROR;
    }
    ++p;

    for (;;) {
        const char *start;
        const char *end;
        char *tmp = NULL;

        while (*p == ' ' || *p == '\t') {
            ++p;
        }
        if (*p == ']') {
            ++p;
            break;
        }

        if (*p == '"') {
            ++p;
            start = p;
            while (*p && *p != '"') {
                unsigned char c = (unsigned char)*p;
                if (c < 0x20u || c > 0x7Eu) {
                    return DSU_STATUS_PARSE_ERROR;
                }
                ++p;
            }
            if (*p != '"') {
                return DSU_STATUS_PARSE_ERROR;
            }
            end = p;
            ++p;
        } else {
            start = p;
            while (*p && *p != ',' && *p != ']') {
                unsigned char c = (unsigned char)*p;
                if (c < 0x21u || c > 0x7Eu) {
                    return DSU_STATUS_PARSE_ERROR;
                }
                ++p;
            }
            end = p;
        }

        while (end > start && (end[-1] == ' ' || end[-1] == '\t')) {
            --end;
        }
        if (end == start) {
            return DSU_STATUS_PARSE_ERROR;
        }
        st = dsu__dup_bytes_cstr((const dsu_u8 *)start, (dsu_u32)(end - start), &tmp);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        st = dsu__normalize_id_inplace(tmp);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(tmp);
            return DSU_STATUS_PARSE_ERROR;
        }
        st = dsu__str_list_push(out_items, out_count, out_cap, tmp);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(tmp);
            return st;
        }

        while (*p == ' ' || *p == '\t') {
            ++p;
        }
        if (*p == ',') {
            ++p;
            continue;
        }
        if (*p == ']') {
            ++p;
            break;
        }
        return DSU_STATUS_PARSE_ERROR;
    }

    while (*p == ' ' || *p == '\t') {
        ++p;
    }
    if (*p != '\0') {
        return DSU_STATUS_PARSE_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__manifest_load_legacy_ini_from_bytes(dsu_ctx_t *ctx,
                                                            const dsu_u8 *bytes,
                                                            dsu_u32 len,
                                                            dsu_manifest_t **out_manifest) {
    char *text;
    char *p;
    char *line;
    char *product_id = NULL;
    char *version = NULL;
    char *install_root = NULL;
    char **components = NULL;
    dsu_u32 component_count = 0u;
    dsu_u32 component_cap = 0u;
    dsu_status_t st;
    dsu_manifest_t *m;

    if (!ctx || !bytes || !out_manifest) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_manifest = NULL;

    if (dsu__bytes_contains_nul(bytes, len)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    text = (char *)dsu__malloc(len + 1u);
    if (!text) {
        return DSU_STATUS_IO_ERROR;
    }
    if (len) {
        memcpy(text, bytes, (size_t)len);
    }
    text[len] = '\0';

    p = text;
    while (*p) {
        char *eq;
        char *key;
        char *val;

        line = p;
        while (*p && *p != '\n') {
            ++p;
        }
        if (*p == '\n') {
            *p++ = '\0';
        }
        if (dsu__legacy_is_comment_or_empty(line)) {
            continue;
        }
        eq = strchr(line, '=');
        if (!eq) {
            st = DSU_STATUS_PARSE_ERROR;
            goto fail;
        }
        *eq = '\0';
        key = dsu__legacy_trim(line);
        val = dsu__legacy_trim(eq + 1);

        if (dsu__streq(key, "product_id")) {
            if (product_id) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__legacy_parse_string_value(val, &product_id);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            st = dsu__normalize_id_inplace(product_id);
            if (st != DSU_STATUS_SUCCESS) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
        } else if (dsu__streq(key, "version")) {
            if (version) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__legacy_parse_string_value(val, &version);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            (void)dsu__ascii_to_lower_inplace(version);
            if (!dsu__is_semverish(version)) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
        } else if (dsu__streq(key, "install_root")) {
            if (install_root) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__legacy_parse_string_value(val, &install_root);
            if (st != DSU_STATUS_SUCCESS) goto fail;
            dsu__normalize_path_inplace(install_root);
        } else if (dsu__streq(key, "components")) {
            if (components) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__legacy_parse_components_value(val, &components, &component_count, &component_cap);
            if (st != DSU_STATUS_SUCCESS) goto fail;
        } else {
            st = DSU_STATUS_PARSE_ERROR;
            goto fail;
        }
    }

    if (!product_id || !version || !install_root || !components || component_count == 0u) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }

    dsu__sort_str_ptrs(components, component_count);
    {
        dsu_u32 w = 0u;
        dsu_u32 i;
        for (i = 0u; i < component_count; ++i) {
            if (w == 0u || dsu__strcmp_bytes(components[w - 1u], components[i]) != 0) {
                components[w++] = components[i];
            } else {
                dsu__free(components[i]);
            }
        }
        component_count = w;
    }

    m = (dsu_manifest_t *)dsu__malloc((dsu_u32)sizeof(*m));
    if (!m) {
        st = DSU_STATUS_IO_ERROR;
        goto fail;
    }
    memset(m, 0, sizeof(*m));
    m->root_version = DSU_MANIFEST_ROOT_SCHEMA_VERSION;
    m->product_id = product_id;
    product_id = NULL;
    m->product_version = version;
    version = NULL;
    m->build_channel = dsu__strdup("stable");
    if (!m->build_channel) {
        st = DSU_STATUS_IO_ERROR;
        goto fail_m;
    }
    {
        char *plat = dsu__strdup("any-any");
        if (!plat) {
            st = DSU_STATUS_IO_ERROR;
            goto fail_m;
        }
        st = dsu__str_list_push(&m->platform_targets, &m->platform_target_count, &m->platform_target_cap, plat);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(plat);
            goto fail_m;
        }
    }
    {
        dsu_manifest_install_root_t r;
        memset(&r, 0, sizeof(r));
        r.scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        r.platform = dsu__strdup("any-any");
        r.path = install_root;
        if (!r.platform) {
            st = DSU_STATUS_IO_ERROR;
            goto fail_m;
        }
        st = dsu__install_root_push(m, &r);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(r.platform);
            goto fail_m;
        }
        install_root = NULL;
    }

    {
        dsu_u32 i;
        for (i = 0u; i < component_count; ++i) {
            dsu_manifest_component_t c;
            memset(&c, 0, sizeof(c));
            c.id = components[i];
            c.kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
            c.flags = 0u;
            st = dsu__component_push(m, &c);
            if (st != DSU_STATUS_SUCCESS) {
                dsu_u32 j;
                for (j = i; j < component_count; ++j) {
                    dsu__free(components[j]);
                }
                goto fail_m;
            }
        }
    }
    dsu__free(components);
    components = NULL;
    component_count = 0u;

    st = dsu_manifest_canonicalize(m);
    if (st != DSU_STATUS_SUCCESS) goto fail_m;
    st = dsu_manifest_validate(m);
    if (st != DSU_STATUS_SUCCESS) goto fail_m;

    {
        dsu_blob_t canonical_payload;
        st = dsu__manifest_serialize_payload(m, &canonical_payload);
        if (st != DSU_STATUS_SUCCESS) goto fail_m;
        m->content_digest32 = dsu_digest32_bytes(canonical_payload.data, canonical_payload.size);
        m->content_digest64 = dsu_digest64_bytes(canonical_payload.data, canonical_payload.size);
        dsu__blob_free(&canonical_payload);
    }

    dsu__free(text);
    *out_manifest = m;
    return DSU_STATUS_SUCCESS;

fail_m:
    dsu__manifest_free(m);
    dsu__free(m);
fail:
    dsu__free(text);
    dsu__free(product_id);
    dsu__free(version);
    dsu__free(install_root);
    if (components) {
        dsu_u32 i;
        for (i = 0u; i < component_count; ++i) {
            dsu__free(components[i]);
        }
        dsu__free(components);
    }
    return st;
}
#endif /* DSU_MANIFEST_ENABLE_LEGACY_INI */

dsu_status_t dsu_manifest_load_file(dsu_ctx_t *ctx, const char *path, dsu_manifest_t **out_manifest) {
    dsu_u8 *file_bytes = NULL;
    dsu_u32 file_len = 0u;
    const dsu_u8 *payload = NULL;
    dsu_u32 payload_len = 0u;
    dsu_u8 magic[4];
    dsu_status_t st;
    dsu_manifest_t *m = NULL;
    dsu_u32 off = 0u;
    int have_root = 0;
    dsu_blob_t canonical_payload;

    if (!ctx || !path || !out_manifest) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_manifest = NULL;

    st = dsu__fs_read_all(&ctx->config, path, &file_bytes, &file_len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    magic[0] = (dsu_u8)DSU_MANIFEST_MAGIC_0;
    magic[1] = (dsu_u8)DSU_MANIFEST_MAGIC_1;
    magic[2] = (dsu_u8)DSU_MANIFEST_MAGIC_2;
    magic[3] = (dsu_u8)DSU_MANIFEST_MAGIC_3;

    st = dsu__file_unwrap_payload(file_bytes,
                                  file_len,
                                  magic,
                                  (dsu_u16)DSU_MANIFEST_FORMAT_VERSION,
                                  &payload,
                                  &payload_len);
    if (st != DSU_STATUS_SUCCESS) {
#if defined(DSU_MANIFEST_ENABLE_LEGACY_INI)
        if (st != DSU_STATUS_UNSUPPORTED_VERSION) {
            dsu_manifest_t *legacy = NULL;
            dsu_status_t st2 = dsu__manifest_load_legacy_ini_from_bytes(ctx, file_bytes, file_len, &legacy);
            if (st2 == DSU_STATUS_SUCCESS) {
                dsu__free(file_bytes);
                (void)dsu_log_emit(ctx,
                                  dsu_ctx_get_audit_log(ctx),
                                  DSU_EVENT_MANIFEST_LOADED,
                                  (dsu_u8)DSU_LOG_SEVERITY_INFO,
                                  (dsu_u8)DSU_LOG_CATEGORY_MANIFEST,
                                  "manifest loaded (legacy)");
                *out_manifest = legacy;
                return DSU_STATUS_SUCCESS;
            }
        }
#endif
        dsu__free(file_bytes);
        return st;
    }

    m = (dsu_manifest_t *)dsu__malloc((dsu_u32)sizeof(*m));
    if (!m) {
        dsu__free(file_bytes);
        return DSU_STATUS_IO_ERROR;
    }
    memset(m, 0, sizeof(*m));

    while (off < payload_len) {
        dsu_u16 t;
        dsu_u32 n;
        dsu_u32 start;
        st = dsu__tlv_read_header(payload, payload_len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) {
            goto fail;
        }
        start = off;

        if (t == (dsu_u16)DSU_TLV_MANIFEST_ROOT) {
            if (have_root) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            st = dsu__manifest_parse_root(m, payload + start, n);
            if (st != DSU_STATUS_SUCCESS) {
                goto fail;
            }
            have_root = 1;
        }

        off = start + n;
    }

    if (!have_root) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }

    st = dsu_manifest_canonicalize(m);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    st = dsu_manifest_validate(m);
    if (st != DSU_STATUS_SUCCESS) goto fail;

    st = dsu__manifest_serialize_payload(m, &canonical_payload);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    m->content_digest32 = dsu_digest32_bytes(canonical_payload.data, canonical_payload.size);
    m->content_digest64 = dsu_digest64_bytes(canonical_payload.data, canonical_payload.size);
    dsu__blob_free(&canonical_payload);

    dsu__free(file_bytes);
    file_bytes = NULL;

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_MANIFEST_LOADED,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_MANIFEST,
                      "manifest loaded");

    *out_manifest = m;
    return DSU_STATUS_SUCCESS;

fail:
    dsu__free(file_bytes);
    if (m) {
        dsu__manifest_free(m);
        dsu__free(m);
    }
    return st;
}

void dsu_manifest_destroy(dsu_ctx_t *ctx, dsu_manifest_t *manifest) {
    (void)ctx;
    if (!manifest) {
        return;
    }
    dsu__manifest_free(manifest);
    dsu__free(manifest);
}

const char *dsu_manifest_product_id(const dsu_manifest_t *manifest) {
    if (!manifest || !manifest->product_id) {
        return "";
    }
    return manifest->product_id;
}

const char *dsu_manifest_product_version(const dsu_manifest_t *manifest) {
    if (!manifest || !manifest->product_version) {
        return "";
    }
    return manifest->product_version;
}

const char *dsu_manifest_build_channel(const dsu_manifest_t *manifest) {
    if (!manifest || !manifest->build_channel) {
        return "";
    }
    return manifest->build_channel;
}

const char *dsu_manifest_version(const dsu_manifest_t *manifest) {
    return dsu_manifest_product_version(manifest);
}

static const char *dsu__manifest_select_install_root(const dsu_manifest_t *m) {
    dsu_u32 i;
    dsu_u32 j;
    const char *target;
    if (!m || m->install_root_count == 0u) {
        return "";
    }
    target = (m->platform_target_count != 0u) ? m->platform_targets[0] : NULL;
    if (target && target[0] != '\0') {
        for (j = 0u; j < 3u; ++j) {
            dsu_u8 scope = (dsu_u8)j;
            for (i = 0u; i < m->install_root_count; ++i) {
                const dsu_manifest_install_root_t *r = &m->install_roots[i];
                if (r->scope == scope && dsu__streq(r->platform, target)) {
                    return r->path ? r->path : "";
                }
            }
        }
    }
    return m->install_roots[0].path ? m->install_roots[0].path : "";
}

const char *dsu_manifest_install_root(const dsu_manifest_t *manifest) {
    return dsu__manifest_select_install_root(manifest);
}

dsu_u32 dsu_manifest_content_digest32(const dsu_manifest_t *manifest) {
    if (!manifest) {
        return 0u;
    }
    return manifest->content_digest32;
}

dsu_u64 dsu_manifest_content_digest64(const dsu_manifest_t *manifest) {
    if (!manifest) {
        return (dsu_u64)0u;
    }
    return manifest->content_digest64;
}

dsu_u32 dsu_manifest_component_count(const dsu_manifest_t *manifest) {
    if (!manifest) {
        return 0u;
    }
    return manifest->component_count;
}

const char *dsu_manifest_component_id(const dsu_manifest_t *manifest, dsu_u32 index) {
    if (!manifest || index >= manifest->component_count) {
        return NULL;
    }
    return manifest->components[index].id;
}

const char *dsu_manifest_component_version(const dsu_manifest_t *manifest, dsu_u32 index) {
    const dsu_manifest_component_t *c;
    if (!manifest || index >= manifest->component_count) {
        return "";
    }
    c = &manifest->components[index];
    if (c->version && c->version[0] != '\0') {
        return c->version;
    }
    return dsu_manifest_product_version(manifest);
}

dsu_manifest_component_kind_t dsu_manifest_component_kind(const dsu_manifest_t *manifest, dsu_u32 index) {
    if (!manifest || index >= manifest->component_count) {
        return DSU_MANIFEST_COMPONENT_KIND_OTHER;
    }
    return (dsu_manifest_component_kind_t)manifest->components[index].kind;
}

dsu_u32 dsu_manifest_component_flags(const dsu_manifest_t *manifest, dsu_u32 index) {
    if (!manifest || index >= manifest->component_count) {
        return 0u;
    }
    return manifest->components[index].flags;
}

dsu_u32 dsu_manifest_component_payload_count(const dsu_manifest_t *manifest, dsu_u32 component_index) {
    if (!manifest || component_index >= manifest->component_count) {
        return 0u;
    }
    return manifest->components[component_index].payload_count;
}

dsu_manifest_payload_kind_t dsu_manifest_component_payload_kind(const dsu_manifest_t *manifest,
                                                               dsu_u32 component_index,
                                                               dsu_u32 payload_index) {
    const dsu_manifest_component_t *c;
    if (!manifest || component_index >= manifest->component_count) {
        return DSU_MANIFEST_PAYLOAD_KIND_FILESET;
    }
    c = &manifest->components[component_index];
    if (payload_index >= c->payload_count) {
        return DSU_MANIFEST_PAYLOAD_KIND_FILESET;
    }
    return (dsu_manifest_payload_kind_t)c->payloads[payload_index].kind;
}

const char *dsu_manifest_component_payload_path(const dsu_manifest_t *manifest,
                                               dsu_u32 component_index,
                                               dsu_u32 payload_index) {
    const dsu_manifest_component_t *c;
    if (!manifest || component_index >= manifest->component_count) {
        return NULL;
    }
    c = &manifest->components[component_index];
    if (payload_index >= c->payload_count) {
        return NULL;
    }
    return c->payloads[payload_index].path;
}

const dsu_u8 *dsu_manifest_component_payload_sha256(const dsu_manifest_t *manifest,
                                                  dsu_u32 component_index,
                                                  dsu_u32 payload_index) {
    const dsu_manifest_component_t *c;
    if (!manifest || component_index >= manifest->component_count) {
        return NULL;
    }
    c = &manifest->components[component_index];
    if (payload_index >= c->payload_count) {
        return NULL;
    }
    return c->payloads[payload_index].sha256;
}

dsu_u64 dsu_manifest_component_payload_size(const dsu_manifest_t *manifest,
                                          dsu_u32 component_index,
                                          dsu_u32 payload_index,
                                          dsu_bool *out_present) {
    const dsu_manifest_component_t *c;
    if (out_present) {
        *out_present = DSU_FALSE;
    }
    if (!manifest || component_index >= manifest->component_count) {
        return (dsu_u64)0u;
    }
    c = &manifest->components[component_index];
    if (payload_index >= c->payload_count) {
        return (dsu_u64)0u;
    }
    if (out_present) {
        *out_present = c->payloads[payload_index].has_size ? DSU_TRUE : DSU_FALSE;
    }
    return c->payloads[payload_index].size;
}

dsu_u32 dsu_manifest_component_dependency_count(const dsu_manifest_t *manifest, dsu_u32 component_index) {
    if (!manifest || component_index >= manifest->component_count) {
        return 0u;
    }
    return manifest->components[component_index].dep_count;
}

const char *dsu_manifest_component_dependency_id(const dsu_manifest_t *manifest,
                                                dsu_u32 component_index,
                                                dsu_u32 dependency_index) {
    const dsu_manifest_component_t *c;
    if (!manifest || component_index >= manifest->component_count) {
        return NULL;
    }
    c = &manifest->components[component_index];
    if (dependency_index >= c->dep_count) {
        return NULL;
    }
    return c->deps[dependency_index].id;
}

dsu_manifest_version_constraint_kind_t dsu_manifest_component_dependency_constraint_kind(const dsu_manifest_t *manifest,
                                                                                       dsu_u32 component_index,
                                                                                       dsu_u32 dependency_index) {
    const dsu_manifest_component_t *c;
    if (!manifest || component_index >= manifest->component_count) {
        return DSU_MANIFEST_VERSION_CONSTRAINT_ANY;
    }
    c = &manifest->components[component_index];
    if (dependency_index >= c->dep_count) {
        return DSU_MANIFEST_VERSION_CONSTRAINT_ANY;
    }
    return (dsu_manifest_version_constraint_kind_t)c->deps[dependency_index].constraint_kind;
}

const char *dsu_manifest_component_dependency_constraint_version(const dsu_manifest_t *manifest,
                                                               dsu_u32 component_index,
                                                               dsu_u32 dependency_index) {
    const dsu_manifest_component_t *c;
    const char *v;
    if (!manifest || component_index >= manifest->component_count) {
        return "";
    }
    c = &manifest->components[component_index];
    if (dependency_index >= c->dep_count) {
        return "";
    }
    v = c->deps[dependency_index].constraint_version;
    return (v ? v : "");
}

dsu_u32 dsu_manifest_component_conflict_count(const dsu_manifest_t *manifest, dsu_u32 component_index) {
    if (!manifest || component_index >= manifest->component_count) {
        return 0u;
    }
    return manifest->components[component_index].conflict_count;
}

const char *dsu_manifest_component_conflict_id(const dsu_manifest_t *manifest,
                                              dsu_u32 component_index,
                                              dsu_u32 conflict_index) {
    const dsu_manifest_component_t *c;
    if (!manifest || component_index >= manifest->component_count) {
        return NULL;
    }
    c = &manifest->components[component_index];
    if (conflict_index >= c->conflict_count) {
        return NULL;
    }
    return c->conflicts[conflict_index];
}

dsu_u32 dsu_manifest_platform_target_count(const dsu_manifest_t *manifest) {
    if (!manifest) {
        return 0u;
    }
    return manifest->platform_target_count;
}

const char *dsu_manifest_platform_target(const dsu_manifest_t *manifest, dsu_u32 index) {
    if (!manifest || index >= manifest->platform_target_count) {
        return NULL;
    }
    return manifest->platform_targets[index];
}

dsu_u32 dsu_manifest_install_root_count(const dsu_manifest_t *manifest) {
    if (!manifest) {
        return 0u;
    }
    return manifest->install_root_count;
}

dsu_manifest_install_scope_t dsu_manifest_install_root_scope(const dsu_manifest_t *manifest, dsu_u32 index) {
    if (!manifest || index >= manifest->install_root_count) {
        return DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    }
    return (dsu_manifest_install_scope_t)manifest->install_roots[index].scope;
}

const char *dsu_manifest_install_root_platform(const dsu_manifest_t *manifest, dsu_u32 index) {
    if (!manifest || index >= manifest->install_root_count) {
        return NULL;
    }
    return manifest->install_roots[index].platform;
}

const char *dsu_manifest_install_root_path(const dsu_manifest_t *manifest, dsu_u32 index) {
    if (!manifest || index >= manifest->install_root_count) {
        return NULL;
    }
    return manifest->install_roots[index].path;
}
