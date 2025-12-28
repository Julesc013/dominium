/*
FILE: source/dominium/setup/installers/macos_classic/core_legacy/src/legacy_manifest.c
MODULE: Dominium Setup (Legacy Core)
PURPOSE: Manifest TLV subset loader for Classic legacy installers.
*/
#include "legacy_internal.h"

#define DSU_MANIFEST_MAGIC_0 'D'
#define DSU_MANIFEST_MAGIC_1 'S'
#define DSU_MANIFEST_MAGIC_2 'U'
#define DSU_MANIFEST_MAGIC_3 'M'
#define DSU_MANIFEST_FORMAT_VERSION 2u

#define DSU_TLV_MANIFEST_ROOT 0x0001u
#define DSU_TLV_ROOT_VERSION 0x0002u
#define DSU_TLV_PRODUCT_ID 0x0010u
#define DSU_TLV_PRODUCT_VERSION 0x0011u
#define DSU_TLV_BUILD_CHANNEL 0x0012u
#define DSU_TLV_PLATFORM_TARGET 0x0020u

#define DSU_TLV_DEFAULT_INSTALL_ROOT 0x0030u
#define DSU_TLV_INSTALL_ROOT_VERSION 0x0031u
#define DSU_TLV_INSTALL_SCOPE 0x0032u
#define DSU_TLV_INSTALL_PLATFORM 0x0033u
#define DSU_TLV_INSTALL_PATH 0x0034u

#define DSU_TLV_COMPONENT 0x0040u
#define DSU_TLV_COMPONENT_VERSION 0x0041u
#define DSU_TLV_COMPONENT_ID 0x0042u
#define DSU_TLV_COMPONENT_VERSTR 0x0043u
#define DSU_TLV_COMPONENT_KIND 0x0044u
#define DSU_TLV_COMPONENT_FLAGS 0x0045u

#define DSU_TLV_PAYLOAD 0x004Cu
#define DSU_TLV_PAYLOAD_VERSION 0x004Du
#define DSU_TLV_PAYLOAD_KIND 0x004Eu
#define DSU_TLV_PAYLOAD_PATH 0x004Fu
#define DSU_TLV_PAYLOAD_SIZE 0x0051u

static void dsu_legacy_manifest_payload_free(dsu_legacy_manifest_payload_t *p) {
    if (!p) return;
    free(p->path);
    p->path = NULL;
    p->kind = 0u;
    p->size = 0u;
}

static void dsu_legacy_manifest_component_free(dsu_legacy_manifest_component_t *c) {
    dsu_legacy_u32 i;
    if (!c) return;
    free(c->id);
    free(c->version);
    for (i = 0u; i < c->payload_count; ++i) {
        dsu_legacy_manifest_payload_free(&c->payloads[i]);
    }
    free(c->payloads);
    memset(c, 0, sizeof(*c));
}

void dsu_legacy_manifest_free(dsu_legacy_manifest_t *manifest) {
    dsu_legacy_u32 i;
    if (!manifest) return;
    free(manifest->product_id);
    free(manifest->product_version);
    for (i = 0u; i < manifest->platform_target_count; ++i) {
        free(manifest->platform_targets[i]);
    }
    free(manifest->platform_targets);
    for (i = 0u; i < manifest->install_root_count; ++i) {
        free(manifest->install_roots[i].platform);
        free(manifest->install_roots[i].path);
    }
    free(manifest->install_roots);
    for (i = 0u; i < manifest->component_count; ++i) {
        dsu_legacy_manifest_component_free(&manifest->components[i]);
    }
    free(manifest->components);
    free(manifest);
}

static dsu_legacy_status_t dsu_legacy_install_root_push(dsu_legacy_manifest_t *m,
                                                        const dsu_legacy_manifest_install_root_t *src) {
    dsu_legacy_manifest_install_root_t *p;
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    if (!m || !src) return DSU_LEGACY_STATUS_INVALID_ARGS;
    count = m->install_root_count;
    cap = m->install_root_cap;
    if (count == cap) {
        dsu_legacy_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_legacy_manifest_install_root_t *)realloc(m->install_roots,
                                                          (size_t)new_cap * sizeof(*m->install_roots));
        if (!p) return DSU_LEGACY_STATUS_IO_ERROR;
        m->install_roots = p;
        m->install_root_cap = new_cap;
    }
    m->install_roots[count] = *src;
    m->install_root_count = count + 1u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_component_push(dsu_legacy_manifest_t *m,
                                                     const dsu_legacy_manifest_component_t *src) {
    dsu_legacy_manifest_component_t *p;
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    if (!m || !src) return DSU_LEGACY_STATUS_INVALID_ARGS;
    count = m->component_count;
    cap = m->component_cap;
    if (count == cap) {
        dsu_legacy_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_legacy_manifest_component_t *)realloc(m->components,
                                                       (size_t)new_cap * sizeof(*m->components));
        if (!p) return DSU_LEGACY_STATUS_IO_ERROR;
        m->components = p;
        m->component_cap = new_cap;
    }
    m->components[count] = *src;
    m->component_count = count + 1u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_component_payload_push(dsu_legacy_manifest_component_t *c,
                                                             const dsu_legacy_manifest_payload_t *src) {
    dsu_legacy_manifest_payload_t *p;
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    if (!c || !src) return DSU_LEGACY_STATUS_INVALID_ARGS;
    count = c->payload_count;
    cap = c->payload_cap;
    if (count == cap) {
        dsu_legacy_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_legacy_manifest_payload_t *)realloc(c->payloads,
                                                     (size_t)new_cap * sizeof(*c->payloads));
        if (!p) return DSU_LEGACY_STATUS_IO_ERROR;
        c->payloads = p;
        c->payload_cap = new_cap;
    }
    c->payloads[count] = *src;
    c->payload_count = count + 1u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_parse_install_root(const unsigned char *buf,
                                                         dsu_legacy_u32 len,
                                                         dsu_legacy_manifest_install_root_t *out_root) {
    dsu_legacy_u32 off = 0u;
    dsu_legacy_u32 version = 0u;
    dsu_legacy_u8 scope = 0u;
    char *platform = NULL;
    char *path = NULL;
    dsu_legacy_u8 have_version = 0u;
    dsu_legacy_u8 have_scope = 0u;
    dsu_legacy_u8 have_platform = 0u;
    dsu_legacy_u8 have_path = 0u;
    dsu_legacy_status_t st = DSU_LEGACY_STATUS_SUCCESS;

    if (!buf || !out_root) return DSU_LEGACY_STATUS_INVALID_ARGS;
    memset(out_root, 0, sizeof(*out_root));

    while (off < len && st == DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_u16 t;
        dsu_legacy_u32 n;
        const unsigned char *v;
        st = dsu_legacy_tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_LEGACY_STATUS_SUCCESS) break;
        v = buf + off;
        if (t == (dsu_legacy_u16)DSU_TLV_INSTALL_ROOT_VERSION) {
            if (n != 4u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            version = (dsu_legacy_u32)v[0]
                    | ((dsu_legacy_u32)v[1] << 8)
                    | ((dsu_legacy_u32)v[2] << 16)
                    | ((dsu_legacy_u32)v[3] << 24);
            have_version = 1u;
        } else if (t == (dsu_legacy_u16)DSU_TLV_INSTALL_SCOPE) {
            if (n != 1u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            scope = v[0];
            have_scope = 1u;
        } else if (t == (dsu_legacy_u16)DSU_TLV_INSTALL_PLATFORM) {
            dsu_legacy_status_t st2;
            if (have_platform) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            st2 = dsu_legacy_dup_bytes_cstr(v, n, &platform);
            if (st2 != DSU_LEGACY_STATUS_SUCCESS) return st2;
            have_platform = 1u;
        } else if (t == (dsu_legacy_u16)DSU_TLV_INSTALL_PATH) {
            dsu_legacy_status_t st2;
            if (have_path) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            st2 = dsu_legacy_dup_bytes_cstr(v, n, &path);
            if (st2 != DSU_LEGACY_STATUS_SUCCESS) return st2;
            have_path = 1u;
        }
        off += n;
    }
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    if (!have_version || version != 1u || !have_scope || !have_platform || !have_path) {
        free(platform);
        free(path);
        return DSU_LEGACY_STATUS_PARSE_ERROR;
    }
    out_root->scope = scope;
    out_root->platform = platform;
    out_root->path = path;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_parse_payload(const unsigned char *buf,
                                                    dsu_legacy_u32 len,
                                                    dsu_legacy_manifest_payload_t *out_payload) {
    dsu_legacy_u32 off = 0u;
    dsu_legacy_u32 version = 0u;
    dsu_legacy_u8 kind = 0u;
    char *path = NULL;
    dsu_legacy_u64 size = 0u;
    dsu_legacy_u8 have_version = 0u;
    dsu_legacy_u8 have_kind = 0u;
    dsu_legacy_u8 have_path = 0u;
    dsu_legacy_status_t st = DSU_LEGACY_STATUS_SUCCESS;

    if (!buf || !out_payload) return DSU_LEGACY_STATUS_INVALID_ARGS;
    memset(out_payload, 0, sizeof(*out_payload));

    while (off < len && st == DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_u16 t;
        dsu_legacy_u32 n;
        const unsigned char *v;
        st = dsu_legacy_tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_LEGACY_STATUS_SUCCESS) break;
        v = buf + off;
        if (t == (dsu_legacy_u16)DSU_TLV_PAYLOAD_VERSION) {
            if (n != 4u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            version = (dsu_legacy_u32)v[0]
                    | ((dsu_legacy_u32)v[1] << 8)
                    | ((dsu_legacy_u32)v[2] << 16)
                    | ((dsu_legacy_u32)v[3] << 24);
            have_version = 1u;
        } else if (t == (dsu_legacy_u16)DSU_TLV_PAYLOAD_KIND) {
            if (n != 1u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            kind = v[0];
            have_kind = 1u;
        } else if (t == (dsu_legacy_u16)DSU_TLV_PAYLOAD_PATH) {
            dsu_legacy_status_t st2;
            if (have_path) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            st2 = dsu_legacy_dup_bytes_cstr(v, n, &path);
            if (st2 != DSU_LEGACY_STATUS_SUCCESS) return st2;
            have_path = 1u;
        } else if (t == (dsu_legacy_u16)DSU_TLV_PAYLOAD_SIZE) {
            dsu_legacy_status_t st2;
            dsu_legacy_u32 off2 = 0u;
            st2 = dsu_legacy_read_u64le(v, n, &off2, &size);
            if (st2 != DSU_LEGACY_STATUS_SUCCESS) return st2;
        }
        off += n;
    }
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    if (!have_version || version != 1u || !have_kind) {
        free(path);
        return DSU_LEGACY_STATUS_PARSE_ERROR;
    }
    if (!have_path) {
        free(path);
        return DSU_LEGACY_STATUS_PARSE_ERROR;
    }
    out_payload->kind = kind;
    out_payload->path = path;
    out_payload->size = size;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_parse_component(const unsigned char *buf,
                                                      dsu_legacy_u32 len,
                                                      dsu_legacy_manifest_component_t *out_comp) {
    dsu_legacy_u32 off = 0u;
    dsu_legacy_u32 version = 0u;
    char *id = NULL;
    char *ver = NULL;
    dsu_legacy_u8 kind = 0u;
    dsu_legacy_u32 flags = 0u;
    dsu_legacy_u8 have_version = 0u;
    dsu_legacy_u8 have_id = 0u;
    dsu_legacy_u8 have_kind = 0u;
    dsu_legacy_status_t st = DSU_LEGACY_STATUS_SUCCESS;
    dsu_legacy_manifest_component_t comp;

    if (!buf || !out_comp) return DSU_LEGACY_STATUS_INVALID_ARGS;
    memset(&comp, 0, sizeof(comp));

    while (off < len && st == DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_u16 t;
        dsu_legacy_u32 n;
        const unsigned char *v;
        st = dsu_legacy_tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_LEGACY_STATUS_SUCCESS) break;
        v = buf + off;
        if (t == (dsu_legacy_u16)DSU_TLV_COMPONENT_VERSION) {
            if (n != 4u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            version = (dsu_legacy_u32)v[0]
                    | ((dsu_legacy_u32)v[1] << 8)
                    | ((dsu_legacy_u32)v[2] << 16)
                    | ((dsu_legacy_u32)v[3] << 24);
            have_version = 1u;
        } else if (t == (dsu_legacy_u16)DSU_TLV_COMPONENT_ID) {
            dsu_legacy_status_t st2;
            st2 = dsu_legacy_dup_bytes_cstr(v, n, &id);
            if (st2 != DSU_LEGACY_STATUS_SUCCESS) return st2;
            dsu_legacy_ascii_lower_inplace(id);
            have_id = 1u;
        } else if (t == (dsu_legacy_u16)DSU_TLV_COMPONENT_VERSTR) {
            dsu_legacy_status_t st2 = dsu_legacy_dup_bytes_cstr(v, n, &ver);
            if (st2 != DSU_LEGACY_STATUS_SUCCESS) return st2;
        } else if (t == (dsu_legacy_u16)DSU_TLV_COMPONENT_KIND) {
            if (n != 1u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            kind = v[0];
            have_kind = 1u;
        } else if (t == (dsu_legacy_u16)DSU_TLV_COMPONENT_FLAGS) {
            if (n != 4u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            flags = (dsu_legacy_u32)v[0]
                  | ((dsu_legacy_u32)v[1] << 8)
                  | ((dsu_legacy_u32)v[2] << 16)
                  | ((dsu_legacy_u32)v[3] << 24);
        } else if (t == (dsu_legacy_u16)DSU_TLV_PAYLOAD) {
            dsu_legacy_manifest_payload_t payload;
            dsu_legacy_status_t st2;
            memset(&payload, 0, sizeof(payload));
            st2 = dsu_legacy_parse_payload(v, n, &payload);
            if (st2 != DSU_LEGACY_STATUS_SUCCESS) {
                dsu_legacy_manifest_payload_free(&payload);
                return st2;
            }
            st2 = dsu_legacy_component_payload_push(&comp, &payload);
            if (st2 != DSU_LEGACY_STATUS_SUCCESS) {
                dsu_legacy_manifest_payload_free(&payload);
                return st2;
            }
        }
        off += n;
    }
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    if (!have_version || version != 1u || !have_id || !have_kind) {
        free(id);
        free(ver);
        dsu_legacy_manifest_component_free(&comp);
        return DSU_LEGACY_STATUS_PARSE_ERROR;
    }
    comp.id = id;
    comp.version = ver ? ver : dsu_legacy_strdup("");
    comp.kind = kind;
    comp.flags = flags;
    *out_comp = comp;
    return DSU_LEGACY_STATUS_SUCCESS;
}

dsu_legacy_status_t dsu_legacy_manifest_load(const char *path,
                                             dsu_legacy_manifest_t **out_manifest) {
    unsigned char *file_bytes = NULL;
    dsu_legacy_u32 file_len = 0u;
    const unsigned char *payload = NULL;
    dsu_legacy_u32 payload_len = 0u;
    dsu_legacy_u32 off = 0u;
    dsu_legacy_status_t st;
    dsu_legacy_manifest_t *m;
    unsigned char magic[4];

    if (!path || !out_manifest) return DSU_LEGACY_STATUS_INVALID_ARGS;
    *out_manifest = NULL;

    st = dsu_legacy_read_file_all(path, &file_bytes, &file_len);
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;

    magic[0] = (unsigned char)DSU_MANIFEST_MAGIC_0;
    magic[1] = (unsigned char)DSU_MANIFEST_MAGIC_1;
    magic[2] = (unsigned char)DSU_MANIFEST_MAGIC_2;
    magic[3] = (unsigned char)DSU_MANIFEST_MAGIC_3;

    st = dsu_legacy_file_unwrap_payload(file_bytes,
                                        file_len,
                                        magic,
                                        (dsu_legacy_u16)DSU_MANIFEST_FORMAT_VERSION,
                                        &payload,
                                        &payload_len);
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        free(file_bytes);
        return st;
    }

    m = (dsu_legacy_manifest_t *)malloc(sizeof(*m));
    if (!m) {
        free(file_bytes);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    memset(m, 0, sizeof(*m));

    while (off < payload_len && st == DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_u16 t;
        dsu_legacy_u32 n;
        const unsigned char *v;
        st = dsu_legacy_tlv_read_header(payload, payload_len, &off, &t, &n);
        if (st != DSU_LEGACY_STATUS_SUCCESS) break;
        v = payload + off;
        if (t == (dsu_legacy_u16)DSU_TLV_MANIFEST_ROOT) {
            dsu_legacy_u32 off2 = 0u;
            dsu_legacy_u32 root_version = 0u;
            dsu_legacy_u8 have_root_version = 0u;
            while (off2 < n && st == DSU_LEGACY_STATUS_SUCCESS) {
                dsu_legacy_u16 t2;
                dsu_legacy_u32 n2;
                const unsigned char *v2;
                st = dsu_legacy_tlv_read_header(v, n, &off2, &t2, &n2);
                if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                v2 = v + off2;
                if (t2 == (dsu_legacy_u16)DSU_TLV_ROOT_VERSION) {
                    if (n2 != 4u) {
                        st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    root_version = (dsu_legacy_u32)v2[0]
                                 | ((dsu_legacy_u32)v2[1] << 8)
                                 | ((dsu_legacy_u32)v2[2] << 16)
                                 | ((dsu_legacy_u32)v2[3] << 24);
                    have_root_version = 1u;
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_PRODUCT_ID) {
                    free(m->product_id);
                    m->product_id = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &m->product_id);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    dsu_legacy_ascii_lower_inplace(m->product_id);
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_PRODUCT_VERSION) {
                    free(m->product_version);
                    m->product_version = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &m->product_version);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_PLATFORM_TARGET) {
                    char *tmp = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &tmp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    dsu_legacy_ascii_lower_inplace(tmp);
                    st = dsu_legacy_list_push(&m->platform_targets,
                                              &m->platform_target_count,
                                              &m->platform_target_cap,
                                              tmp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) {
                        free(tmp);
                        break;
                    }
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_DEFAULT_INSTALL_ROOT) {
                    dsu_legacy_manifest_install_root_t root;
                    st = dsu_legacy_parse_install_root(v2, n2, &root);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    st = dsu_legacy_install_root_push(m, &root);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) {
                        free(root.platform);
                        free(root.path);
                        break;
                    }
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_COMPONENT) {
                    dsu_legacy_manifest_component_t comp;
                    st = dsu_legacy_parse_component(v2, n2, &comp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    st = dsu_legacy_component_push(m, &comp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) {
                        dsu_legacy_manifest_component_free(&comp);
                        break;
                    }
                } else {
                    /* skip */
                }
                off2 += n2;
            }
            if (st != DSU_LEGACY_STATUS_SUCCESS) break;
            if (!have_root_version || root_version != 1u) {
                st = DSU_LEGACY_STATUS_UNSUPPORTED;
                break;
            }
        }
        off += n;
    }

    free(file_bytes);
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_manifest_free(m);
        return st;
    }
    if (!m->product_id || !m->product_version) {
        dsu_legacy_manifest_free(m);
        return DSU_LEGACY_STATUS_PARSE_ERROR;
    }
    *out_manifest = m;
    return DSU_LEGACY_STATUS_SUCCESS;
}
