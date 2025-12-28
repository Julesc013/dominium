/*
FILE: source/dominium/setup/installers/macos_classic/core_legacy/src/legacy_state.c
MODULE: Dominium Setup (Legacy Core)
PURPOSE: Installed-state writer/reader (DSUS TLV subset).
*/
#include "legacy_internal.h"

#define DSU_STATE_MAGIC_0 'D'
#define DSU_STATE_MAGIC_1 'S'
#define DSU_STATE_MAGIC_2 'U'
#define DSU_STATE_MAGIC_3 'S'
#define DSU_STATE_FORMAT_VERSION 1u

#define DSU_TLV_STATE_ROOT 0x0001u
#define DSU_TLV_STATE_ROOT_VERSION 0x0002u
#define DSU_TLV_STATE_PRODUCT_ID 0x0010u
#define DSU_TLV_STATE_PRODUCT_VERSION 0x0011u
#define DSU_TLV_STATE_PLATFORM 0x0020u
#define DSU_TLV_STATE_SCOPE 0x0021u
#define DSU_TLV_STATE_INSTALL_ROOT 0x0022u

#define DSU_TLV_STATE_COMPONENT 0x0040u
#define DSU_TLV_STATE_COMPONENT_VERSION 0x0041u
#define DSU_TLV_STATE_COMPONENT_ID 0x0042u
#define DSU_TLV_STATE_COMPONENT_VERSTR 0x0043u

#define DSU_TLV_STATE_FILE 0x0050u
#define DSU_TLV_STATE_FILE_VERSION 0x0051u
#define DSU_TLV_STATE_FILE_PATH 0x0052u
#define DSU_TLV_STATE_FILE_SHA256 0x0053u
#define DSU_TLV_STATE_FILE_SIZE 0x0054u

static void dsu_legacy_state_component_free(dsu_legacy_state_component_t *c) {
    if (!c) return;
    free(c->id);
    free(c->version);
    c->id = NULL;
    c->version = NULL;
}

static void dsu_legacy_state_file_free(dsu_legacy_state_file_t *f) {
    if (!f) return;
    free(f->path);
    memset(f, 0, sizeof(*f));
}

void dsu_legacy_state_free(dsu_legacy_state_t *state) {
    dsu_legacy_u32 i;
    if (!state) return;
    free(state->product_id);
    free(state->product_version);
    free(state->platform_triple);
    free(state->install_root);
    for (i = 0u; i < state->component_count; ++i) {
        dsu_legacy_state_component_free(&state->components[i]);
    }
    free(state->components);
    for (i = 0u; i < state->file_count; ++i) {
        dsu_legacy_state_file_free(&state->files[i]);
    }
    free(state->files);
    free(state);
}

static dsu_legacy_status_t dsu_legacy_state_component_push(dsu_legacy_state_t *s,
                                                           const dsu_legacy_state_component_t *src) {
    dsu_legacy_state_component_t *p;
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    if (!s || !src) return DSU_LEGACY_STATUS_INVALID_ARGS;
    count = s->component_count;
    cap = s->component_cap;
    if (count == cap) {
        dsu_legacy_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_legacy_state_component_t *)realloc(s->components,
                                                    (size_t)new_cap * sizeof(*s->components));
        if (!p) return DSU_LEGACY_STATUS_IO_ERROR;
        s->components = p;
        s->component_cap = new_cap;
    }
    s->components[count] = *src;
    s->component_count = count + 1u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_state_file_push(dsu_legacy_state_t *s,
                                                      const dsu_legacy_state_file_t *src) {
    dsu_legacy_state_file_t *p;
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    if (!s || !src) return DSU_LEGACY_STATUS_INVALID_ARGS;
    count = s->file_count;
    cap = s->file_cap;
    if (count == cap) {
        dsu_legacy_u32 new_cap = (cap == 0u) ? 16u : (cap * 2u);
        p = (dsu_legacy_state_file_t *)realloc(s->files,
                                               (size_t)new_cap * sizeof(*s->files));
        if (!p) return DSU_LEGACY_STATUS_IO_ERROR;
        s->files = p;
        s->file_cap = new_cap;
    }
    s->files[count] = *src;
    s->file_count = count + 1u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

dsu_legacy_status_t dsu_legacy_state_add_component(dsu_legacy_state_t *state,
                                                   const char *id,
                                                   const char *version) {
    dsu_legacy_state_component_t c;
    if (!state || !id || !version) return DSU_LEGACY_STATUS_INVALID_ARGS;
    memset(&c, 0, sizeof(c));
    c.id = dsu_legacy_strdup(id);
    c.version = dsu_legacy_strdup(version);
    if (!c.id || !c.version) {
        dsu_legacy_state_component_free(&c);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    dsu_legacy_ascii_lower_inplace(c.id);
    return dsu_legacy_state_component_push(state, &c);
}

dsu_legacy_status_t dsu_legacy_state_add_file(dsu_legacy_state_t *state,
                                              const char *path,
                                              dsu_legacy_u64 size) {
    dsu_legacy_state_file_t f;
    if (!state || !path || path[0] == '\0') return DSU_LEGACY_STATUS_INVALID_ARGS;
    memset(&f, 0, sizeof(f));
    f.path = dsu_legacy_strdup(path);
    f.size = size;
    f.has_size = 1u;
    memset(f.sha256, 0, sizeof(f.sha256));
    f.has_sha256 = 1u;
    if (!f.path) {
        dsu_legacy_state_file_free(&f);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    return dsu_legacy_state_file_push(state, &f);
}

dsu_legacy_status_t dsu_legacy_state_write(const dsu_legacy_state_t *state,
                                           const char *path) {
    dsu_legacy_blob_t root;
    dsu_legacy_blob_t payload;
    dsu_legacy_blob_t file_bytes;
    dsu_legacy_status_t st;
    dsu_legacy_u32 i;
    unsigned char magic[4];
    if (!state || !path || path[0] == '\0') return DSU_LEGACY_STATUS_INVALID_ARGS;

    dsu_legacy_blob_init(&root);
    dsu_legacy_blob_init(&payload);
    dsu_legacy_blob_init(&file_bytes);

    st = dsu_legacy_blob_put_tlv(&root, (dsu_legacy_u16)DSU_TLV_STATE_ROOT_VERSION, "\x01\x00\x00\x00", 4u);
    if (st == DSU_LEGACY_STATUS_SUCCESS) {
        st = dsu_legacy_blob_put_tlv(&root, (dsu_legacy_u16)DSU_TLV_STATE_PRODUCT_ID,
                                     state->product_id ? state->product_id : "",
                                     dsu_legacy_strlen(state->product_id));
    }
    if (st == DSU_LEGACY_STATUS_SUCCESS) {
        st = dsu_legacy_blob_put_tlv(&root, (dsu_legacy_u16)DSU_TLV_STATE_PRODUCT_VERSION,
                                     state->product_version ? state->product_version : "",
                                     dsu_legacy_strlen(state->product_version));
    }
    if (st == DSU_LEGACY_STATUS_SUCCESS) {
        st = dsu_legacy_blob_put_tlv(&root, (dsu_legacy_u16)DSU_TLV_STATE_PLATFORM,
                                     state->platform_triple ? state->platform_triple : "",
                                     dsu_legacy_strlen(state->platform_triple));
    }
    if (st == DSU_LEGACY_STATUS_SUCCESS) {
        unsigned char scope = state->scope;
        st = dsu_legacy_blob_put_tlv(&root, (dsu_legacy_u16)DSU_TLV_STATE_SCOPE, &scope, 1u);
    }
    if (st == DSU_LEGACY_STATUS_SUCCESS) {
        st = dsu_legacy_blob_put_tlv(&root, (dsu_legacy_u16)DSU_TLV_STATE_INSTALL_ROOT,
                                     state->install_root ? state->install_root : "",
                                     dsu_legacy_strlen(state->install_root));
    }
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_blob_free(&root);
        dsu_legacy_blob_free(&payload);
        dsu_legacy_blob_free(&file_bytes);
        return st;
    }

    for (i = 0u; i < state->component_count && st == DSU_LEGACY_STATUS_SUCCESS; ++i) {
        dsu_legacy_blob_t comp;
        dsu_legacy_state_component_t *c = &state->components[i];
        dsu_legacy_blob_init(&comp);
        st = dsu_legacy_blob_put_tlv(&comp, (dsu_legacy_u16)DSU_TLV_STATE_COMPONENT_VERSION, "\x01\x00\x00\x00", 4u);
        if (st == DSU_LEGACY_STATUS_SUCCESS) {
            st = dsu_legacy_blob_put_tlv(&comp, (dsu_legacy_u16)DSU_TLV_STATE_COMPONENT_ID,
                                         c->id ? c->id : "", dsu_legacy_strlen(c->id));
        }
        if (st == DSU_LEGACY_STATUS_SUCCESS) {
            st = dsu_legacy_blob_put_tlv(&comp, (dsu_legacy_u16)DSU_TLV_STATE_COMPONENT_VERSTR,
                                         c->version ? c->version : "", dsu_legacy_strlen(c->version));
        }
        if (st == DSU_LEGACY_STATUS_SUCCESS) {
            st = dsu_legacy_blob_put_tlv(&root, (dsu_legacy_u16)DSU_TLV_STATE_COMPONENT, comp.data, comp.size);
        }
        dsu_legacy_blob_free(&comp);
    }
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_blob_free(&root);
        dsu_legacy_blob_free(&payload);
        dsu_legacy_blob_free(&file_bytes);
        return st;
    }

    for (i = 0u; i < state->file_count && st == DSU_LEGACY_STATUS_SUCCESS; ++i) {
        dsu_legacy_blob_t fb;
        dsu_legacy_state_file_t *f = &state->files[i];
        dsu_legacy_blob_init(&fb);
        st = dsu_legacy_blob_put_tlv(&fb, (dsu_legacy_u16)DSU_TLV_STATE_FILE_VERSION, "\x01\x00\x00\x00", 4u);
        if (st == DSU_LEGACY_STATUS_SUCCESS) {
            st = dsu_legacy_blob_put_tlv(&fb, (dsu_legacy_u16)DSU_TLV_STATE_FILE_PATH,
                                         f->path ? f->path : "", dsu_legacy_strlen(f->path));
        }
        if (st == DSU_LEGACY_STATUS_SUCCESS) {
            st = dsu_legacy_blob_put_tlv(&fb, (dsu_legacy_u16)DSU_TLV_STATE_FILE_SHA256,
                                         f->sha256, 32u);
        }
        if (st == DSU_LEGACY_STATUS_SUCCESS) {
            unsigned char size_le[8];
            size_le[0] = (unsigned char)(f->size & 0xFFu);
            size_le[1] = (unsigned char)((f->size >> 8) & 0xFFu);
            size_le[2] = (unsigned char)((f->size >> 16) & 0xFFu);
            size_le[3] = (unsigned char)((f->size >> 24) & 0xFFu);
            size_le[4] = 0u;
            size_le[5] = 0u;
            size_le[6] = 0u;
            size_le[7] = 0u;
            st = dsu_legacy_blob_put_tlv(&fb, (dsu_legacy_u16)DSU_TLV_STATE_FILE_SIZE, size_le, 8u);
        }
        if (st == DSU_LEGACY_STATUS_SUCCESS) {
            st = dsu_legacy_blob_put_tlv(&root, (dsu_legacy_u16)DSU_TLV_STATE_FILE, fb.data, fb.size);
        }
        dsu_legacy_blob_free(&fb);
    }
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_blob_free(&root);
        dsu_legacy_blob_free(&payload);
        dsu_legacy_blob_free(&file_bytes);
        return st;
    }

    st = dsu_legacy_blob_put_tlv(&payload, (dsu_legacy_u16)DSU_TLV_STATE_ROOT, root.data, root.size);
    dsu_legacy_blob_free(&root);
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_blob_free(&payload);
        dsu_legacy_blob_free(&file_bytes);
        return st;
    }

    magic[0] = (unsigned char)DSU_STATE_MAGIC_0;
    magic[1] = (unsigned char)DSU_STATE_MAGIC_1;
    magic[2] = (unsigned char)DSU_STATE_MAGIC_2;
    magic[3] = (unsigned char)DSU_STATE_MAGIC_3;
    st = dsu_legacy_file_wrap_payload(magic,
                                      (dsu_legacy_u16)DSU_STATE_FORMAT_VERSION,
                                      payload.data,
                                      payload.size,
                                      &file_bytes);
    dsu_legacy_blob_free(&payload);
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_blob_free(&file_bytes);
        return st;
    }
    st = dsu_legacy_write_file_all(path, file_bytes.data, file_bytes.size);
    dsu_legacy_blob_free(&file_bytes);
    return st;
}

dsu_legacy_status_t dsu_legacy_state_load(const char *path,
                                          dsu_legacy_state_t **out_state) {
    unsigned char *file_bytes = NULL;
    dsu_legacy_u32 file_len = 0u;
    const unsigned char *payload = NULL;
    dsu_legacy_u32 payload_len = 0u;
    dsu_legacy_u32 off = 0u;
    dsu_legacy_state_t *s;
    dsu_legacy_status_t st;
    unsigned char magic[4];

    if (!path || !out_state) return DSU_LEGACY_STATUS_INVALID_ARGS;
    *out_state = NULL;

    st = dsu_legacy_read_file_all(path, &file_bytes, &file_len);
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;

    magic[0] = (unsigned char)DSU_STATE_MAGIC_0;
    magic[1] = (unsigned char)DSU_STATE_MAGIC_1;
    magic[2] = (unsigned char)DSU_STATE_MAGIC_2;
    magic[3] = (unsigned char)DSU_STATE_MAGIC_3;

    st = dsu_legacy_file_unwrap_payload(file_bytes,
                                        file_len,
                                        magic,
                                        (dsu_legacy_u16)DSU_STATE_FORMAT_VERSION,
                                        &payload,
                                        &payload_len);
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        free(file_bytes);
        return st;
    }

    s = (dsu_legacy_state_t *)malloc(sizeof(*s));
    if (!s) {
        free(file_bytes);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    memset(s, 0, sizeof(*s));

    while (off < payload_len && st == DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_u16 t;
        dsu_legacy_u32 n;
        const unsigned char *v;
        st = dsu_legacy_tlv_read_header(payload, payload_len, &off, &t, &n);
        if (st != DSU_LEGACY_STATUS_SUCCESS) break;
        v = payload + off;
        if (t == (dsu_legacy_u16)DSU_TLV_STATE_ROOT) {
            dsu_legacy_u32 off2 = 0u;
            while (off2 < n && st == DSU_LEGACY_STATUS_SUCCESS) {
                dsu_legacy_u16 t2;
                dsu_legacy_u32 n2;
                const unsigned char *v2;
                st = dsu_legacy_tlv_read_header(v, n, &off2, &t2, &n2);
                if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                v2 = v + off2;
                if (t2 == (dsu_legacy_u16)DSU_TLV_STATE_PRODUCT_ID) {
                    free(s->product_id);
                    s->product_id = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &s->product_id);
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_STATE_PRODUCT_VERSION) {
                    free(s->product_version);
                    s->product_version = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &s->product_version);
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_STATE_PLATFORM) {
                    free(s->platform_triple);
                    s->platform_triple = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &s->platform_triple);
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_STATE_SCOPE) {
                    if (n2 != 1u) st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                    else s->scope = v2[0];
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_STATE_INSTALL_ROOT) {
                    free(s->install_root);
                    s->install_root = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &s->install_root);
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_STATE_COMPONENT) {
                    dsu_legacy_state_component_t c;
                    dsu_legacy_u32 off3 = 0u;
                    memset(&c, 0, sizeof(c));
                    while (off3 < n2 && st == DSU_LEGACY_STATUS_SUCCESS) {
                        dsu_legacy_u16 t3;
                        dsu_legacy_u32 n3;
                        const unsigned char *v3;
                        st = dsu_legacy_tlv_read_header(v2, n2, &off3, &t3, &n3);
                        if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                        v3 = v2 + off3;
                        if (t3 == (dsu_legacy_u16)DSU_TLV_STATE_COMPONENT_ID) {
                            free(c.id);
                            c.id = NULL;
                            st = dsu_legacy_dup_bytes_cstr(v3, n3, &c.id);
                            if (st == DSU_LEGACY_STATUS_SUCCESS) dsu_legacy_ascii_lower_inplace(c.id);
                        } else if (t3 == (dsu_legacy_u16)DSU_TLV_STATE_COMPONENT_VERSTR) {
                            free(c.version);
                            c.version = NULL;
                            st = dsu_legacy_dup_bytes_cstr(v3, n3, &c.version);
                        }
                        off3 += n3;
                    }
                    if (st == DSU_LEGACY_STATUS_SUCCESS && c.id) {
                        if (!c.version) c.version = dsu_legacy_strdup("");
                        st = dsu_legacy_state_component_push(s, &c);
                    } else {
                        dsu_legacy_state_component_free(&c);
                    }
                } else if (t2 == (dsu_legacy_u16)DSU_TLV_STATE_FILE) {
                    dsu_legacy_state_file_t f;
                    dsu_legacy_u32 off3 = 0u;
                    memset(&f, 0, sizeof(f));
                    while (off3 < n2 && st == DSU_LEGACY_STATUS_SUCCESS) {
                        dsu_legacy_u16 t3;
                        dsu_legacy_u32 n3;
                        const unsigned char *v3;
                        st = dsu_legacy_tlv_read_header(v2, n2, &off3, &t3, &n3);
                        if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                        v3 = v2 + off3;
                        if (t3 == (dsu_legacy_u16)DSU_TLV_STATE_FILE_PATH) {
                            free(f.path);
                            f.path = NULL;
                            st = dsu_legacy_dup_bytes_cstr(v3, n3, &f.path);
                        } else if (t3 == (dsu_legacy_u16)DSU_TLV_STATE_FILE_SIZE) {
                            dsu_legacy_u32 off4 = 0u;
                            st = dsu_legacy_read_u64le(v3, n3, &off4, &f.size);
                            if (st == DSU_LEGACY_STATUS_SUCCESS) f.has_size = 1u;
                        } else if (t3 == (dsu_legacy_u16)DSU_TLV_STATE_FILE_SHA256) {
                            if (n3 == 32u) {
                                memcpy(f.sha256, v3, 32u);
                                f.has_sha256 = 1u;
                            }
                        }
                        off3 += n3;
                    }
                    if (st == DSU_LEGACY_STATUS_SUCCESS && f.path) {
                        if (!f.has_sha256) memset(f.sha256, 0, sizeof(f.sha256));
                        st = dsu_legacy_state_file_push(s, &f);
                    } else {
                        dsu_legacy_state_file_free(&f);
                    }
                }
                off2 += n2;
            }
        }
        off += n;
    }

    free(file_bytes);
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_state_free(s);
        return st;
    }
    if (!s->product_id || !s->install_root) {
        dsu_legacy_state_free(s);
        return DSU_LEGACY_STATUS_PARSE_ERROR;
    }
    *out_state = s;
    return DSU_LEGACY_STATUS_SUCCESS;
}
