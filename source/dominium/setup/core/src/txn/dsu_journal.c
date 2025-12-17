/*
FILE: source/dominium/setup/core/src/txn/dsu_journal.c
MODULE: Dominium Setup
PURPOSE: Binary transaction journal format + IO (Plan S-4).
*/
#include "dsu_journal.h"

#include <stdio.h>
#include <string.h>

/* Inner entry payload fields (TLV inside the outer entry record). */
#define DSU_JTLV_ENTRY_VERSION 0x0001u /* u32 */

#define DSU_JTLV_TARGET_ROOT 0x0010u   /* u8 */
#define DSU_JTLV_TARGET_PATH 0x0011u   /* string */
#define DSU_JTLV_SOURCE_ROOT 0x0012u   /* u8 */
#define DSU_JTLV_SOURCE_PATH 0x0013u   /* string */
#define DSU_JTLV_ROLLBACK_ROOT 0x0014u /* u8 */
#define DSU_JTLV_ROLLBACK_PATH 0x0015u /* string */

#define DSU_JTLV_FLAGS 0x0020u         /* u32 */

/* NOOP metadata/checkpoint fields. */
#define DSU_JTLV_META_INSTALL_ROOT 0x0100u /* string */
#define DSU_JTLV_META_TXN_ROOT 0x0101u     /* string */
#define DSU_JTLV_META_STATE_PATH 0x0102u   /* string */
#define DSU_JTLV_META_PROGRESS 0x0103u     /* u32 */

#define DSU_JTLV_CHECKSUM64 0x00FFu    /* u64 */

static dsu_status_t dsu__blob_put_tlv_u8(dsu_blob_t *b, dsu_u16 type, dsu_u8 v) {
    return dsu__blob_put_tlv(b, type, &v, 1u);
}

static dsu_status_t dsu__blob_put_tlv_u32(dsu_blob_t *b, dsu_u16 type, dsu_u32 v) {
    dsu_u8 tmp[4];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    return dsu__blob_put_tlv(b, type, tmp, 4u);
}

static dsu_status_t dsu__blob_put_tlv_u64(dsu_blob_t *b, dsu_u16 type, dsu_u64 v) {
    dsu_u8 tmp[8];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    tmp[4] = (dsu_u8)((v >> 32) & 0xFFu);
    tmp[5] = (dsu_u8)((v >> 40) & 0xFFu);
    tmp[6] = (dsu_u8)((v >> 48) & 0xFFu);
    tmp[7] = (dsu_u8)((v >> 56) & 0xFFu);
    return dsu__blob_put_tlv(b, type, tmp, 8u);
}

static dsu_status_t dsu__blob_put_tlv_str(dsu_blob_t *b, dsu_u16 type, const char *s) {
    dsu_u32 n;
    if (!s) s = "";
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    return dsu__blob_put_tlv(b, type, s, n);
}

static dsu_status_t dsu__write_all(FILE *f, const void *bytes, dsu_u32 len) {
    size_t nw;
    if (!f || (!bytes && len != 0u)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (len == 0u) {
        return DSU_STATUS_SUCCESS;
    }
    nw = fwrite(bytes, 1u, (size_t)len, f);
    if (nw != (size_t)len) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_u64 dsu__entry_checksum64(dsu_u16 entry_type, const dsu_u8 *payload, dsu_u32 payload_len) {
    dsu_u64 h;
    dsu_u8 tmp[2];
    tmp[0] = (dsu_u8)(entry_type & 0xFFu);
    tmp[1] = (dsu_u8)((entry_type >> 8) & 0xFFu);
    h = dsu_digest64_init();
    h = dsu_digest64_update(h, tmp, 2u);
    h = dsu_digest64_update(h, payload, payload_len);
    return h;
}

static dsu_status_t dsu__journal_write_header(FILE *f, dsu_u64 journal_id, dsu_u64 plan_digest) {
    dsu_u8 hdr[24];
    dsu_u16 v = (dsu_u16)DSU_JOURNAL_FORMAT_VERSION;
    dsu_u16 endian = (dsu_u16)DSU_ENDIAN_MARKER_LE;

    hdr[0] = (dsu_u8)DSU_JOURNAL_MAGIC_0;
    hdr[1] = (dsu_u8)DSU_JOURNAL_MAGIC_1;
    hdr[2] = (dsu_u8)DSU_JOURNAL_MAGIC_2;
    hdr[3] = (dsu_u8)DSU_JOURNAL_MAGIC_3;
    hdr[4] = (dsu_u8)(v & 0xFFu);
    hdr[5] = (dsu_u8)((v >> 8) & 0xFFu);
    hdr[6] = (dsu_u8)(endian & 0xFFu);
    hdr[7] = (dsu_u8)((endian >> 8) & 0xFFu);
    hdr[8] = (dsu_u8)(journal_id & 0xFFu);
    hdr[9] = (dsu_u8)((journal_id >> 8) & 0xFFu);
    hdr[10] = (dsu_u8)((journal_id >> 16) & 0xFFu);
    hdr[11] = (dsu_u8)((journal_id >> 24) & 0xFFu);
    hdr[12] = (dsu_u8)((journal_id >> 32) & 0xFFu);
    hdr[13] = (dsu_u8)((journal_id >> 40) & 0xFFu);
    hdr[14] = (dsu_u8)((journal_id >> 48) & 0xFFu);
    hdr[15] = (dsu_u8)((journal_id >> 56) & 0xFFu);
    hdr[16] = (dsu_u8)(plan_digest & 0xFFu);
    hdr[17] = (dsu_u8)((plan_digest >> 8) & 0xFFu);
    hdr[18] = (dsu_u8)((plan_digest >> 16) & 0xFFu);
    hdr[19] = (dsu_u8)((plan_digest >> 24) & 0xFFu);
    hdr[20] = (dsu_u8)((plan_digest >> 32) & 0xFFu);
    hdr[21] = (dsu_u8)((plan_digest >> 40) & 0xFFu);
    hdr[22] = (dsu_u8)((plan_digest >> 48) & 0xFFu);
    hdr[23] = (dsu_u8)((plan_digest >> 56) & 0xFFu);
    return dsu__write_all(f, hdr, (dsu_u32)sizeof(hdr));
}

static dsu_status_t dsu__journal_write_record(FILE *f, dsu_u16 type, const dsu_u8 *payload, dsu_u32 payload_len) {
    dsu_u8 hdr[6];
    hdr[0] = (dsu_u8)(type & 0xFFu);
    hdr[1] = (dsu_u8)((type >> 8) & 0xFFu);
    hdr[2] = (dsu_u8)(payload_len & 0xFFu);
    hdr[3] = (dsu_u8)((payload_len >> 8) & 0xFFu);
    hdr[4] = (dsu_u8)((payload_len >> 16) & 0xFFu);
    hdr[5] = (dsu_u8)((payload_len >> 24) & 0xFFu);
    if (dsu__write_all(f, hdr, 6u) != DSU_STATUS_SUCCESS) {
        return DSU_STATUS_IO_ERROR;
    }
    return dsu__write_all(f, payload, payload_len);
}

dsu_status_t dsu_journal_writer_open(dsu_journal_writer_t *w,
                                    const char *path,
                                    dsu_u64 journal_id,
                                    dsu_u64 plan_digest) {
    FILE *f;
    dsu_status_t st;
    if (!w || !path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(w, 0, sizeof(*w));
    f = fopen(path, "wb");
    if (!f) {
        return DSU_STATUS_IO_ERROR;
    }
    st = dsu__journal_write_header(f, journal_id, plan_digest);
    if (st != DSU_STATUS_SUCCESS) {
        fclose(f);
        return st;
    }
    w->f = f;
    w->journal_id = journal_id;
    w->plan_digest = plan_digest;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_journal_writer_open_append(dsu_journal_writer_t *w, const char *path) {
    FILE *f;
    if (!w || !path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(w, 0, sizeof(*w));
    f = fopen(path, "ab");
    if (!f) {
        return DSU_STATUS_IO_ERROR;
    }
    w->f = f;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__journal_append_noop_payload(dsu_journal_writer_t *w, const dsu_blob_t *payload) {
    if (!w || !w->f || !payload) {
        return DSU_STATUS_INVALID_ARGS;
    }
    return dsu__journal_write_record(w->f, (dsu_u16)DSU_JOURNAL_ENTRY_NOOP, payload->data, payload->size);
}

dsu_status_t dsu_journal_writer_write_meta(dsu_journal_writer_t *w,
                                          const char *install_root_abs,
                                          const char *txn_root_abs,
                                          const char *state_rel) {
    dsu_blob_t b;
    dsu_u64 sum;
    dsu_status_t st;

    if (!w || !w->f || !install_root_abs || !txn_root_abs) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!state_rel) {
        state_rel = "";
    }

    dsu__blob_init(&b);
    st = dsu__blob_put_tlv_u32(&b, (dsu_u16)DSU_JTLV_ENTRY_VERSION, 1u);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&b, (dsu_u16)DSU_JTLV_META_INSTALL_ROOT, install_root_abs);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&b, (dsu_u16)DSU_JTLV_META_TXN_ROOT, txn_root_abs);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&b, (dsu_u16)DSU_JTLV_META_STATE_PATH, state_rel);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&b);
        return st;
    }

    sum = dsu__entry_checksum64((dsu_u16)DSU_JOURNAL_ENTRY_NOOP, b.data, b.size);
    st = dsu__blob_put_tlv_u64(&b, (dsu_u16)DSU_JTLV_CHECKSUM64, sum);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&b);
        return st;
    }

    st = dsu__journal_append_noop_payload(w, &b);
    dsu__blob_free(&b);
    return st;
}

dsu_status_t dsu_journal_writer_append_progress(dsu_journal_writer_t *w, dsu_u32 commit_progress) {
    dsu_blob_t b;
    dsu_u64 sum;
    dsu_status_t st;
    if (!w || !w->f) {
        return DSU_STATUS_INVALID_ARGS;
    }
    dsu__blob_init(&b);
    st = dsu__blob_put_tlv_u32(&b, (dsu_u16)DSU_JTLV_ENTRY_VERSION, 1u);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u32(&b, (dsu_u16)DSU_JTLV_META_PROGRESS, commit_progress);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&b);
        return st;
    }
    sum = dsu__entry_checksum64((dsu_u16)DSU_JOURNAL_ENTRY_NOOP, b.data, b.size);
    st = dsu__blob_put_tlv_u64(&b, (dsu_u16)DSU_JTLV_CHECKSUM64, sum);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&b);
        return st;
    }
    st = dsu__journal_append_noop_payload(w, &b);
    dsu__blob_free(&b);
    return st;
}

dsu_status_t dsu_journal_writer_append_entry(dsu_journal_writer_t *w,
                                            dsu_u16 entry_type,
                                            dsu_u8 target_root,
                                            const char *target_path,
                                            dsu_u8 source_root,
                                            const char *source_path,
                                            dsu_u8 rollback_root,
                                            const char *rollback_path,
                                            dsu_u32 flags) {
    dsu_blob_t b;
    dsu_u64 sum;
    dsu_status_t st;
    dsu_u32 checksum_offset;

    if (!w || !w->f) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!target_path) target_path = "";
    if (!source_path) source_path = "";
    if (!rollback_path) rollback_path = "";

    dsu__blob_init(&b);
    st = dsu__blob_put_tlv_u32(&b, (dsu_u16)DSU_JTLV_ENTRY_VERSION, 1u);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&b, (dsu_u16)DSU_JTLV_TARGET_ROOT, target_root);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&b, (dsu_u16)DSU_JTLV_TARGET_PATH, target_path);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&b, (dsu_u16)DSU_JTLV_SOURCE_ROOT, source_root);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&b, (dsu_u16)DSU_JTLV_SOURCE_PATH, source_path);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&b, (dsu_u16)DSU_JTLV_ROLLBACK_ROOT, rollback_root);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&b, (dsu_u16)DSU_JTLV_ROLLBACK_PATH, rollback_path);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u32(&b, (dsu_u16)DSU_JTLV_FLAGS, flags);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&b);
        return st;
    }

    checksum_offset = b.size;
    sum = dsu__entry_checksum64(entry_type, b.data, checksum_offset);
    st = dsu__blob_put_tlv_u64(&b, (dsu_u16)DSU_JTLV_CHECKSUM64, sum);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&b);
        return st;
    }

    st = dsu__journal_write_record(w->f, entry_type, b.data, b.size);
    dsu__blob_free(&b);
    return st;
}

dsu_status_t dsu_journal_writer_close(dsu_journal_writer_t *w) {
    if (!w) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (w->f) {
        if (fclose(w->f) != 0) {
            w->f = NULL;
            return DSU_STATUS_IO_ERROR;
        }
        w->f = NULL;
    }
    return DSU_STATUS_SUCCESS;
}

static void dsu__journal_entry_free(dsu_journal_entry_t *e) {
    if (!e) {
        return;
    }
    dsu__free(e->target_path);
    dsu__free(e->source_path);
    dsu__free(e->rollback_path);
    memset(e, 0, sizeof(*e));
}

void dsu_journal_destroy(dsu_ctx_t *ctx, dsu_journal_t *journal) {
    dsu_u32 i;
    (void)ctx;
    if (!journal) {
        return;
    }
    dsu__free(journal->install_root);
    dsu__free(journal->txn_root);
    dsu__free(journal->state_path);
    for (i = 0u; i < journal->entry_count; ++i) {
        dsu__journal_entry_free(&journal->entries[i]);
    }
    dsu__free(journal->entries);
    dsu__free(journal);
}

static dsu_status_t dsu__dup_bytes_str(const dsu_u8 *bytes, dsu_u32 len, char **out) {
    char *p;
    if (!out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out = NULL;
    if (!bytes && len != 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    p = (char *)dsu__malloc(len + 1u);
    if (!p) {
        return DSU_STATUS_IO_ERROR;
    }
    if (len) {
        memcpy(p, bytes, (size_t)len);
    }
    p[len] = '\0';
    *out = p;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__read_exact(FILE *f, void *dst, dsu_u32 n) {
    size_t nr;
    if (!f || !dst) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (n == 0u) {
        return DSU_STATUS_SUCCESS;
    }
    nr = fread(dst, 1u, (size_t)n, f);
    if (nr != (size_t)n) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__journal_read_header(FILE *f, dsu_journal_t *j) {
    dsu_u8 hdr[24];
    dsu_u16 version;
    dsu_u16 endian;
    dsu_u32 off = 8u;
    dsu_status_t st;
    if (!f || !j) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu__read_exact(f, hdr, (dsu_u32)sizeof(hdr));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (hdr[0] != (dsu_u8)DSU_JOURNAL_MAGIC_0 ||
        hdr[1] != (dsu_u8)DSU_JOURNAL_MAGIC_1 ||
        hdr[2] != (dsu_u8)DSU_JOURNAL_MAGIC_2 ||
        hdr[3] != (dsu_u8)DSU_JOURNAL_MAGIC_3) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    version = (dsu_u16)((dsu_u16)hdr[4] | ((dsu_u16)hdr[5] << 8));
    if ((dsu_u32)version != DSU_JOURNAL_FORMAT_VERSION) {
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }
    endian = (dsu_u16)((dsu_u16)hdr[6] | ((dsu_u16)hdr[7] << 8));
    if (endian != (dsu_u16)DSU_ENDIAN_MARKER_LE) {
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }
    st = dsu__read_u64le(hdr, (dsu_u32)sizeof(hdr), &off, &j->journal_id);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu__read_u64le(hdr, (dsu_u32)sizeof(hdr), &off, &j->plan_digest);
    if (st != DSU_STATUS_SUCCESS) return st;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__parse_entry_payload(dsu_u16 entry_type,
                                            const dsu_u8 *payload,
                                            dsu_u32 payload_len,
                                            dsu_journal_entry_t *out_entry,
                                            dsu_journal_t *journal) {
    dsu_u32 off = 0u;
    dsu_u32 checksum_off = 0xFFFFFFFFu;
    dsu_u64 checksum_stored = 0u;
    dsu_u32 entry_version = 0u;

    dsu_u8 target_root = 0u;
    dsu_u8 source_root = 0u;
    dsu_u8 rollback_root = 0u;
    char *target_path = NULL;
    char *source_path = NULL;
    char *rollback_path = NULL;
    dsu_u32 flags = 0u;

    if (!payload && payload_len != 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }

    while (off < payload_len) {
        dsu_u16 t;
        dsu_u32 n;
        dsu_u32 start = off;
        dsu_status_t st = dsu__tlv_read_header(payload, payload_len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(target_path);
            dsu__free(source_path);
            dsu__free(rollback_path);
            return st;
        }
        if (t == (dsu_u16)DSU_JTLV_CHECKSUM64) {
            dsu_u32 sub = 0u;
            checksum_off = start;
            if (off + n != payload_len) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return DSU_STATUS_INTEGRITY_ERROR;
            }
            if (n != 8u) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return DSU_STATUS_INTEGRITY_ERROR;
            }
            st = dsu__read_u64le(payload + off, n, &sub, &checksum_stored);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_ENTRY_VERSION) {
            dsu_u32 sub = 0u;
            st = dsu__read_u32le(payload + off, n, &sub, &entry_version);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_TARGET_ROOT) {
            dsu_u32 sub = 0u;
            st = dsu__read_u8(payload + off, n, &sub, &target_root);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_SOURCE_ROOT) {
            dsu_u32 sub = 0u;
            st = dsu__read_u8(payload + off, n, &sub, &source_root);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_ROLLBACK_ROOT) {
            dsu_u32 sub = 0u;
            st = dsu__read_u8(payload + off, n, &sub, &rollback_root);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_TARGET_PATH) {
            dsu__free(target_path);
            target_path = NULL;
            st = dsu__dup_bytes_str(payload + off, n, &target_path);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_SOURCE_PATH) {
            dsu__free(source_path);
            source_path = NULL;
            st = dsu__dup_bytes_str(payload + off, n, &source_path);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_ROLLBACK_PATH) {
            dsu__free(rollback_path);
            rollback_path = NULL;
            st = dsu__dup_bytes_str(payload + off, n, &rollback_path);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_FLAGS) {
            dsu_u32 sub = 0u;
            st = dsu__read_u32le(payload + off, n, &sub, &flags);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_META_INSTALL_ROOT) {
            dsu__free(journal->install_root);
            journal->install_root = NULL;
            st = dsu__dup_bytes_str(payload + off, n, &journal->install_root);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_META_TXN_ROOT) {
            dsu__free(journal->txn_root);
            journal->txn_root = NULL;
            st = dsu__dup_bytes_str(payload + off, n, &journal->txn_root);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_META_STATE_PATH) {
            dsu__free(journal->state_path);
            journal->state_path = NULL;
            st = dsu__dup_bytes_str(payload + off, n, &journal->state_path);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
        } else if (t == (dsu_u16)DSU_JTLV_META_PROGRESS) {
            dsu_u32 sub = 0u;
            dsu_u32 v = 0u;
            st = dsu__read_u32le(payload + off, n, &sub, &v);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_path);
                dsu__free(source_path);
                dsu__free(rollback_path);
                return st;
            }
            journal->commit_progress = v;
        }

        st = dsu__tlv_skip_value(payload_len, &off, n);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(target_path);
            dsu__free(source_path);
            dsu__free(rollback_path);
            return st;
        }
    }

    if (checksum_off == 0xFFFFFFFFu) {
        dsu__free(target_path);
        dsu__free(source_path);
        dsu__free(rollback_path);
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    if (entry_version != 1u) {
        dsu__free(target_path);
        dsu__free(source_path);
        dsu__free(rollback_path);
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }

    {
        dsu_u64 checksum_calc = dsu__entry_checksum64(entry_type, payload, checksum_off);
        if (checksum_calc != checksum_stored) {
            dsu__free(target_path);
            dsu__free(source_path);
            dsu__free(rollback_path);
            return DSU_STATUS_INTEGRITY_ERROR;
        }
    }

    if (out_entry) {
        memset(out_entry, 0, sizeof(*out_entry));
        out_entry->type = entry_type;
        out_entry->target_root = target_root;
        out_entry->source_root = source_root;
        out_entry->rollback_root = rollback_root;
        out_entry->target_path = target_path;
        out_entry->source_path = source_path;
        out_entry->rollback_path = rollback_path;
        out_entry->flags = flags;
    } else {
        dsu__free(target_path);
        dsu__free(source_path);
        dsu__free(rollback_path);
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_journal_read_file(dsu_ctx_t *ctx, const char *path, dsu_journal_t **out_journal) {
    FILE *f;
    dsu_journal_t *j;
    dsu_status_t st;
    dsu_u32 cap = 0u;
    dsu_u32 count = 0u;
    dsu_journal_entry_t *entries = NULL;
    (void)ctx;

    if (!path || !out_journal) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_journal = NULL;

    f = fopen(path, "rb");
    if (!f) {
        return DSU_STATUS_IO_ERROR;
    }

    j = (dsu_journal_t *)dsu__malloc((dsu_u32)sizeof(*j));
    if (!j) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }
    memset(j, 0, sizeof(*j));

    st = dsu__journal_read_header(f, j);
    if (st != DSU_STATUS_SUCCESS) {
        fclose(f);
        dsu_journal_destroy(ctx, j);
        return st;
    }

    for (;;) {
        dsu_u8 rec_hdr[6];
        dsu_u16 type;
        dsu_u32 n;
        dsu_u32 off = 0u;
        dsu_u8 *payload;
        size_t nr;

        nr = fread(rec_hdr, 1u, 6u, f);
        if (nr == 0u) {
            break; /* EOF */
        }
        if (nr != 6u) {
            fclose(f);
            dsu_journal_destroy(ctx, j);
            return DSU_STATUS_INTEGRITY_ERROR;
        }

        st = dsu__read_u16le(rec_hdr, 6u, &off, &type);
        if (st != DSU_STATUS_SUCCESS) {
            fclose(f);
            dsu_journal_destroy(ctx, j);
            return st;
        }
        st = dsu__read_u32le(rec_hdr, 6u, &off, &n);
        if (st != DSU_STATUS_SUCCESS) {
            fclose(f);
            dsu_journal_destroy(ctx, j);
            return st;
        }

        payload = (dsu_u8 *)dsu__malloc(n);
        if (!payload && n != 0u) {
            fclose(f);
            dsu_journal_destroy(ctx, j);
            return DSU_STATUS_IO_ERROR;
        }
        if (n != 0u) {
            st = dsu__read_exact(f, payload, n);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(payload);
                fclose(f);
                dsu_journal_destroy(ctx, j);
                return st;
            }
        }

        if (type == (dsu_u16)DSU_JOURNAL_ENTRY_NOOP) {
            st = dsu__parse_entry_payload(type, payload, n, NULL, j);
            dsu__free(payload);
            if (st != DSU_STATUS_SUCCESS) {
                fclose(f);
                dsu_journal_destroy(ctx, j);
                return st;
            }
            continue;
        }

        if (count == cap) {
            dsu_u32 new_cap = (cap == 0u) ? 16u : (cap * 2u);
            dsu_journal_entry_t *p = (dsu_journal_entry_t *)dsu__realloc(entries, new_cap * (dsu_u32)sizeof(*entries));
            if (!p) {
                dsu__free(payload);
                fclose(f);
                dsu_journal_destroy(ctx, j);
                return DSU_STATUS_IO_ERROR;
            }
            entries = p;
            cap = new_cap;
        }
        memset(&entries[count], 0, sizeof(entries[count]));
        st = dsu__parse_entry_payload(type, payload, n, &entries[count], j);
        dsu__free(payload);
        if (st != DSU_STATUS_SUCCESS) {
            fclose(f);
            j->entries = entries;
            j->entry_count = count;
            dsu_journal_destroy(ctx, j);
            return st;
        }
        ++count;
    }

    fclose(f);

    j->entries = entries;
    j->entry_count = count;
    *out_journal = j;
    return DSU_STATUS_SUCCESS;
}
