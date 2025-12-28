/*
FILE: source/dominium/setup/installers/macos_classic/core_legacy/src/legacy_invocation.c
MODULE: Dominium Setup (Legacy Core)
PURPOSE: Invocation TLV subset loader for Classic legacy installers.
*/
#include "legacy_internal.h"

#define DSU_INVOCATION_MAGIC_0 'D'
#define DSU_INVOCATION_MAGIC_1 'S'
#define DSU_INVOCATION_MAGIC_2 'U'
#define DSU_INVOCATION_MAGIC_3 'I'
#define DSU_INVOCATION_FORMAT_VERSION 1u

#define DSU_INVOCATION_TLV_ROOT 0x0100u
#define DSU_INVOCATION_TLV_ROOT_VERSION 0x0101u
#define DSU_INVOCATION_TLV_OPERATION 0x0110u
#define DSU_INVOCATION_TLV_SCOPE 0x0111u
#define DSU_INVOCATION_TLV_PLATFORM_TRIPLE 0x0120u
#define DSU_INVOCATION_TLV_INSTALL_ROOT 0x0130u
#define DSU_INVOCATION_TLV_POLICY_FLAGS 0x0140u
#define DSU_INVOCATION_TLV_UI_MODE 0x0150u
#define DSU_INVOCATION_TLV_FRONTEND_ID 0x0151u
#define DSU_INVOCATION_TLV_SELECTED_COMPONENT 0x0160u
#define DSU_INVOCATION_TLV_EXCLUDED_COMPONENT 0x0161u

static void dsu_legacy_invocation_reset(dsu_legacy_invocation_t *inv) {
    if (!inv) return;
    memset(inv, 0, sizeof(*inv));
}

void dsu_legacy_invocation_free(dsu_legacy_invocation_t *invocation) {
    dsu_legacy_u32 i;
    if (!invocation) return;
    free(invocation->platform_triple);
    free(invocation->ui_mode);
    free(invocation->frontend_id);
    for (i = 0u; i < invocation->install_root_count; ++i) {
        free(invocation->install_roots[i]);
    }
    free(invocation->install_roots);
    for (i = 0u; i < invocation->selected_component_count; ++i) {
        free(invocation->selected_components[i]);
    }
    free(invocation->selected_components);
    for (i = 0u; i < invocation->excluded_component_count; ++i) {
        free(invocation->excluded_components[i]);
    }
    free(invocation->excluded_components);
    free(invocation);
}

dsu_legacy_status_t dsu_legacy_invocation_load(const char *path,
                                               dsu_legacy_invocation_t **out_invocation) {
    unsigned char *file_bytes = NULL;
    dsu_legacy_u32 file_len = 0u;
    const unsigned char *payload = NULL;
    dsu_legacy_u32 payload_len = 0u;
    dsu_legacy_u32 off = 0u;
    dsu_legacy_u8 have_root = 0u;
    dsu_legacy_status_t st;
    dsu_legacy_invocation_t *inv;
    unsigned char magic[4];

    if (!path || !out_invocation) return DSU_LEGACY_STATUS_INVALID_ARGS;
    *out_invocation = NULL;

    st = dsu_legacy_read_file_all(path, &file_bytes, &file_len);
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;

    magic[0] = (unsigned char)DSU_INVOCATION_MAGIC_0;
    magic[1] = (unsigned char)DSU_INVOCATION_MAGIC_1;
    magic[2] = (unsigned char)DSU_INVOCATION_MAGIC_2;
    magic[3] = (unsigned char)DSU_INVOCATION_MAGIC_3;

    st = dsu_legacy_file_unwrap_payload(file_bytes,
                                        file_len,
                                        magic,
                                        (dsu_legacy_u16)DSU_INVOCATION_FORMAT_VERSION,
                                        &payload,
                                        &payload_len);
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        free(file_bytes);
        return st;
    }

    inv = (dsu_legacy_invocation_t *)malloc(sizeof(*inv));
    if (!inv) {
        free(file_bytes);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    dsu_legacy_invocation_reset(inv);

    while (off < payload_len && st == DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_u16 t;
        dsu_legacy_u32 n;
        const unsigned char *v;
        st = dsu_legacy_tlv_read_header(payload, payload_len, &off, &t, &n);
        if (st != DSU_LEGACY_STATUS_SUCCESS) break;
        if (payload_len - off < n) {
            st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
            break;
        }
        v = payload + off;
        if (t == (dsu_legacy_u16)DSU_INVOCATION_TLV_ROOT) {
            dsu_legacy_u32 off2 = 0u;
            dsu_legacy_u32 root_version = 0u;
            dsu_legacy_u8 have_root_version = 0u;
            dsu_legacy_u8 have_op = 0u;
            dsu_legacy_u8 have_scope = 0u;
            dsu_legacy_u8 have_platform = 0u;
            dsu_legacy_u8 have_policy = 0u;
            dsu_legacy_u8 have_ui = 0u;
            dsu_legacy_u8 have_frontend = 0u;
            if (have_root) {
                st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                break;
            }
            have_root = 1u;
            while (off2 < n && st == DSU_LEGACY_STATUS_SUCCESS) {
                dsu_legacy_u16 t2;
                dsu_legacy_u32 n2;
                const unsigned char *v2;
                st = dsu_legacy_tlv_read_header(v, n, &off2, &t2, &n2);
                if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                if (n - off2 < n2) {
                    st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                    break;
                }
                v2 = v + off2;
                if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_ROOT_VERSION) {
                    if (n2 != 4u) {
                        st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    root_version = (dsu_legacy_u32)v2[0]
                                 | ((dsu_legacy_u32)v2[1] << 8)
                                 | ((dsu_legacy_u32)v2[2] << 16)
                                 | ((dsu_legacy_u32)v2[3] << 24);
                    have_root_version = 1u;
                } else if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_OPERATION) {
                    if (n2 != 1u) {
                        st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    inv->operation = v2[0];
                    have_op = 1u;
                } else if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_SCOPE) {
                    if (n2 != 1u) {
                        st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    inv->scope = v2[0];
                    have_scope = 1u;
                } else if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_PLATFORM_TRIPLE) {
                    if (have_platform) {
                        st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &inv->platform_triple);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    have_platform = 1u;
                } else if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_INSTALL_ROOT) {
                    char *tmp = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &tmp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    st = dsu_legacy_list_push(&inv->install_roots,
                                              &inv->install_root_count,
                                              &inv->install_root_cap,
                                              tmp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) {
                        free(tmp);
                        break;
                    }
                } else if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_POLICY_FLAGS) {
                    if (n2 != 4u) {
                        st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    inv->policy_flags = (dsu_legacy_u32)v2[0]
                                      | ((dsu_legacy_u32)v2[1] << 8)
                                      | ((dsu_legacy_u32)v2[2] << 16)
                                      | ((dsu_legacy_u32)v2[3] << 24);
                    have_policy = 1u;
                } else if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_UI_MODE) {
                    if (have_ui) {
                        st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &inv->ui_mode);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    have_ui = 1u;
                } else if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_FRONTEND_ID) {
                    if (have_frontend) {
                        st = DSU_LEGACY_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &inv->frontend_id);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    have_frontend = 1u;
                } else if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_SELECTED_COMPONENT) {
                    char *tmp = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &tmp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    dsu_legacy_ascii_lower_inplace(tmp);
                    st = dsu_legacy_list_push(&inv->selected_components,
                                              &inv->selected_component_count,
                                              &inv->selected_component_cap,
                                              tmp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) {
                        free(tmp);
                        break;
                    }
                } else if (t2 == (dsu_legacy_u16)DSU_INVOCATION_TLV_EXCLUDED_COMPONENT) {
                    char *tmp = NULL;
                    st = dsu_legacy_dup_bytes_cstr(v2, n2, &tmp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) break;
                    dsu_legacy_ascii_lower_inplace(tmp);
                    st = dsu_legacy_list_push(&inv->excluded_components,
                                              &inv->excluded_component_count,
                                              &inv->excluded_component_cap,
                                              tmp);
                    if (st != DSU_LEGACY_STATUS_SUCCESS) {
                        free(tmp);
                        break;
                    }
                }
                off2 += n2;
            }
            if (st != DSU_LEGACY_STATUS_SUCCESS) break;
            if (!have_root_version || root_version != 1u) {
                st = DSU_LEGACY_STATUS_UNSUPPORTED;
                break;
            }
            if (!have_op || !have_scope || !have_platform || !have_policy || !have_ui || !have_frontend) {
                st = DSU_LEGACY_STATUS_PARSE_ERROR;
                break;
            }
        }
        off += n;
    }

    free(file_bytes);
    if (st != DSU_LEGACY_STATUS_SUCCESS || !have_root) {
        dsu_legacy_invocation_free(inv);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? DSU_LEGACY_STATUS_PARSE_ERROR : st;
    }

    if (!inv->platform_triple || !dsu_legacy_is_ascii_printable(inv->platform_triple)) {
        dsu_legacy_invocation_free(inv);
        return DSU_LEGACY_STATUS_PARSE_ERROR;
    }
    if (!inv->ui_mode || !dsu_legacy_is_ascii_printable(inv->ui_mode)) {
        dsu_legacy_invocation_free(inv);
        return DSU_LEGACY_STATUS_PARSE_ERROR;
    }
    if (!inv->frontend_id || !dsu_legacy_is_ascii_printable(inv->frontend_id)) {
        dsu_legacy_invocation_free(inv);
        return DSU_LEGACY_STATUS_PARSE_ERROR;
    }

    *out_invocation = inv;
    return DSU_LEGACY_STATUS_SUCCESS;
}
