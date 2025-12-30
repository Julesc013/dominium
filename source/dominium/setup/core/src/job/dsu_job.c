/*
FILE: source/dominium/setup/core/src/job/dsu_job.c
MODULE: Dominium Setup
PURPOSE: Resumable job journaling + execution wrapper for long setup operations.
*/
#include "../../include/dsu/dsu_job.h"

#include "../../include/dsu/dsu_fs.h"
#include "../../include/dsu/dsu_plan.h"
#include "../../include/dsu/dsu_state.h"
#include "dominium/core_log.h"

#include "../fs/dsu_platform_iface.h"
#include "../util/dsu_util_internal.h"

#include <stdio.h>
#include <string.h>
#include <time.h>

enum {
    DSU_JOB_INPUT_TAG_SCHEMA = 1u,
    DSU_JOB_INPUT_TAG_JOB_TYPE = 2u,
    DSU_JOB_INPUT_TAG_PLAN_PATH = 3u,
    DSU_JOB_INPUT_TAG_STATE_PATH = 4u,
    DSU_JOB_INPUT_TAG_LOG_PATH = 5u,
    DSU_JOB_INPUT_TAG_DRY_RUN = 6u,
    DSU_JOB_INPUT_TAG_FLAGS = 7u
};

typedef struct dsu_job_paths_t {
    char job_root[DSU_JOB_PATH_MAX];
    char job_dir[DSU_JOB_PATH_MAX];
    char def_path[DSU_JOB_PATH_MAX];
    char state_path[DSU_JOB_PATH_MAX];
    char input_path[DSU_JOB_PATH_MAX];
    char events_path[DSU_JOB_PATH_MAX];
} dsu_job_paths_t;

typedef struct dsu_job_ctx_t {
    dsu_ctx_t *ctx;
    dsu_job_input_t input;
    dsu_job_options_t opts;
    core_job_def def;
    core_job_state state;
    dsu_job_paths_t paths;
    dsu_txn_result_t txn_result;
} dsu_job_ctx_t;

static void dsu_job_normalize_path(const char *in, char *out, dsu_u32 out_cap) {
    dsu_u32 i = 0u;
    dsu_u32 w = 0u;
    if (!out || out_cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!in) {
        return;
    }
    while (in[i] != '\0' && (w + 1u) < out_cap) {
        char c = in[i++];
        if (c == '\\') c = '/';
        out[w++] = c;
    }
    out[w] = '\0';
}

static int dsu_job_is_alpha(char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

static int dsu_job_is_abs_path_like(const char *p) {
    if (!p) return 0;
    if (p[0] == '/' || p[0] == '\\') return 1;
    if ((p[0] == '/' && p[1] == '/') || (p[0] == '\\' && p[1] == '\\')) return 1;
    if (dsu_job_is_alpha(p[0]) && p[1] == ':' && (p[2] == '/' || p[2] == '\\')) return 1;
    return 0;
}

static dsu_status_t dsu_job_mkdirs_abs(const char *abs_dir) {
    dsu_u8 exists = 0u;
    dsu_u8 is_dir = 0u;
    dsu_u8 is_symlink = 0u;
    dsu_status_t st;

    if (!abs_dir || abs_dir[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu_platform_path_info(abs_dir, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (exists) {
        if (is_dir && !is_symlink) {
            return DSU_STATUS_SUCCESS;
        }
        return DSU_STATUS_IO_ERROR;
    }

    {
        char parent[DSU_JOB_PATH_MAX];
        char base[256];
        parent[0] = '\0';
        base[0] = '\0';
        st = dsu_fs_path_split(abs_dir, parent, (dsu_u32)sizeof(parent), base, (dsu_u32)sizeof(base));
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        if (parent[0] != '\0' && dsu_job_is_abs_path_like(parent)) {
            st = dsu_job_mkdirs_abs(parent);
            if (st != DSU_STATUS_SUCCESS) {
                return st;
            }
        }
    }

    return dsu_platform_mkdir(abs_dir);
}

static void dsu_job_u64_to_hex16(dsu_u64 v, char out_hex[17]) {
    static const char *hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        dsu_u32 shift = (dsu_u32)((15 - i) * 4);
        dsu_u32 nib = (dsu_u32)((v >> shift) & (dsu_u64)0xFu);
        out_hex[i] = hex[nib & 0xFu];
    }
    out_hex[16] = '\0';
}

static dsu_status_t dsu_job_path_join(const char *a, const char *b, char *out, dsu_u32 out_cap) {
    char norm_a[DSU_JOB_PATH_MAX];
    char norm_b[DSU_JOB_PATH_MAX];
    dsu_u32 len_a;
    dsu_u32 len_b;
    dsu_job_normalize_path(a, norm_a, (dsu_u32)sizeof(norm_a));
    dsu_job_normalize_path(b, norm_b, (dsu_u32)sizeof(norm_b));
    len_a = (dsu_u32)strlen(norm_a);
    len_b = (dsu_u32)strlen(norm_b);
    if (!out || out_cap == 0u) return DSU_STATUS_INVALID_ARGS;
    out[0] = '\0';
    if (len_a == 0u) {
        if (len_b + 1u > out_cap) return DSU_STATUS_INVALID_ARGS;
        memcpy(out, norm_b, len_b + 1u);
        return DSU_STATUS_SUCCESS;
    }
    if (len_b == 0u) {
        if (len_a + 1u > out_cap) return DSU_STATUS_INVALID_ARGS;
        memcpy(out, norm_a, len_a + 1u);
        return DSU_STATUS_SUCCESS;
    }
    if (len_a + len_b + 2u > out_cap) return DSU_STATUS_INVALID_ARGS;
    memcpy(out, norm_a, len_a);
    if (norm_a[len_a - 1u] != '/') {
        out[len_a] = '/';
        memcpy(out + len_a + 1u, norm_b, len_b + 1u);
    } else {
        memcpy(out + len_a, norm_b, len_b + 1u);
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu_job_write_all_atomic(const char *path, const dsu_u8 *bytes, dsu_u32 len) {
    char tmp[DSU_JOB_PATH_MAX];
    size_t n;
    dsu_status_t st;
    if (!path || !bytes) return DSU_STATUS_INVALID_ARGS;
    n = strlen(path);
    if (n + 5u >= sizeof(tmp)) return DSU_STATUS_INVALID_ARGS;
    memcpy(tmp, path, n);
    memcpy(tmp + n, ".tmp", 5u);
    st = dsu__fs_write_all(tmp, bytes, len);
    if (st != DSU_STATUS_SUCCESS) {
        (void)dsu_platform_remove_file(tmp);
        return st;
    }
    st = dsu_platform_rename(tmp, path, 1u);
    if (st != DSU_STATUS_SUCCESS) {
        (void)dsu_platform_remove_file(tmp);
        return st;
    }
    return DSU_STATUS_SUCCESS;
}

static void dsu_job_build_paths(const char *job_root, dsu_u64 job_id, dsu_job_paths_t *out_paths) {
    char hex[17];
    if (!out_paths) return;
    memset(out_paths, 0, sizeof(*out_paths));
    dsu_job_u64_to_hex16(job_id, hex);
    dsu_job_path_join(job_root, hex, out_paths->job_dir, (dsu_u32)sizeof(out_paths->job_dir));
    dsu_job_path_join(out_paths->job_dir, "job_def.tlv", out_paths->def_path, (dsu_u32)sizeof(out_paths->def_path));
    dsu_job_path_join(out_paths->job_dir, "job_state.tlv", out_paths->state_path, (dsu_u32)sizeof(out_paths->state_path));
    dsu_job_path_join(out_paths->job_dir, "job_input.tlv", out_paths->input_path, (dsu_u32)sizeof(out_paths->input_path));
    dsu_job_path_join(out_paths->job_dir, "job_events.tlv", out_paths->events_path, (dsu_u32)sizeof(out_paths->events_path));
    dsu_job_normalize_path(job_root, out_paths->job_root, (dsu_u32)sizeof(out_paths->job_root));
}

static int dsu_job_is_plan_job(dsu_u32 job_type) {
    return (job_type == (dsu_u32)CORE_JOB_TYPE_SETUP_INSTALL ||
            job_type == (dsu_u32)CORE_JOB_TYPE_SETUP_UPGRADE ||
            job_type == (dsu_u32)CORE_JOB_TYPE_SETUP_REPAIR);
}

static int dsu_job_is_state_job(dsu_u32 job_type) {
    return (job_type == (dsu_u32)CORE_JOB_TYPE_SETUP_UNINSTALL ||
            job_type == (dsu_u32)CORE_JOB_TYPE_SETUP_VERIFY);
}

static void dsu_job_build_def(dsu_u32 job_type, core_job_def *out_def) {
    core_job_def def;
    u32 step_count = 0u;
    core_job_def_clear(&def);
    def.schema_version = CORE_JOB_DEF_TLV_VERSION;
    def.job_type = job_type;

    if (dsu_job_is_plan_job(job_type) || dsu_job_is_state_job(job_type)) {
        step_count = 2u;
        def.steps[0].step_id = 1u;
        def.steps[0].flags = (u32)(CORE_JOB_STEP_IDEMPOTENT | CORE_JOB_STEP_RETRYABLE);
        def.steps[0].depends_on_count = 0u;

        def.steps[1].step_id = 2u;
        def.steps[1].flags = (u32)(CORE_JOB_STEP_IDEMPOTENT | CORE_JOB_STEP_RETRYABLE);
        def.steps[1].depends_on_count = 1u;
        def.steps[1].depends_on[0] = def.steps[0].step_id;
    }

    def.step_count = step_count;
    *out_def = def;
}

static dsu_u64 dsu_job_generate_id(void) {
    static dsu_u64 counter = 0u;
    dsu_u64 t = (dsu_u64)(unsigned long)time(NULL);
    if (t == 0u) t = 1u;
    counter += 1u;
    return (t << 16) ^ (counter & 0xFFFFu);
}

typedef struct dsu_job_mem_sink_t {
    dsu_blob_t *blob;
} dsu_job_mem_sink_t;

static dom_abi_result dsu_job_mem_sink_write(void *user, const void *data, u32 len) {
    dsu_job_mem_sink_t *sink = (dsu_job_mem_sink_t *)user;
    if (!sink || !sink->blob || !data || len == 0u) {
        return 0;
    }
    if (dsu__blob_append(sink->blob, data, (dsu_u32)len) != DSU_STATUS_SUCCESS) {
        return (dom_abi_result)-1;
    }
    return 0;
}

static dsu_status_t dsu_job_write_def(const dsu_job_paths_t *paths, const core_job_def *def) {
    dsu_blob_t blob;
    dsu_job_mem_sink_t sink;
    core_job_write_sink csink;
    dsu_status_t st;
    dsu__blob_init(&blob);
    sink.blob = &blob;
    csink.user = &sink;
    csink.write = dsu_job_mem_sink_write;
    if (core_job_def_write_tlv(def, &csink) != 0) {
        dsu__blob_free(&blob);
        return DSU_STATUS_INTERNAL_ERROR;
    }
    st = dsu_job_write_all_atomic(paths->def_path, blob.data, blob.size);
    dsu__blob_free(&blob);
    return st;
}

static dsu_status_t dsu_job_write_state(const dsu_job_paths_t *paths, const core_job_state *st_in) {
    dsu_blob_t blob;
    dsu_job_mem_sink_t sink;
    core_job_write_sink csink;
    dsu_status_t st;
    dsu__blob_init(&blob);
    sink.blob = &blob;
    csink.user = &sink;
    csink.write = dsu_job_mem_sink_write;
    if (core_job_state_write_tlv(st_in, &csink) != 0) {
        dsu__blob_free(&blob);
        return DSU_STATUS_INTERNAL_ERROR;
    }
    st = dsu_job_write_all_atomic(paths->state_path, blob.data, blob.size);
    dsu__blob_free(&blob);
    return st;
}

static dsu_status_t dsu_job_read_state(dsu_ctx_t *ctx, const dsu_job_paths_t *paths, core_job_state *out_state) {
    dsu_u8 *bytes = NULL;
    dsu_u32 len = 0u;
    dsu_status_t st;
    if (!ctx || !paths || !out_state) return DSU_STATUS_INVALID_ARGS;
    st = dsu__fs_read_all(&ctx->config, paths->state_path, &bytes, &len);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(bytes);
        return st;
    }
    if (!bytes || len == 0u) {
        dsu__free(bytes);
        return DSU_STATUS_PARSE_ERROR;
    }
    if (core_job_state_read_tlv(bytes, len, out_state) != 0) {
        dsu__free(bytes);
        return DSU_STATUS_PARSE_ERROR;
    }
    dsu__free(bytes);
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu_job_read_def(dsu_ctx_t *ctx, const dsu_job_paths_t *paths, core_job_def *out_def) {
    dsu_u8 *bytes = NULL;
    dsu_u32 len = 0u;
    dsu_status_t st;
    if (!ctx || !paths || !out_def) return DSU_STATUS_INVALID_ARGS;
    st = dsu__fs_read_all(&ctx->config, paths->def_path, &bytes, &len);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(bytes);
        return st;
    }
    if (!bytes || len == 0u) {
        dsu__free(bytes);
        return DSU_STATUS_PARSE_ERROR;
    }
    if (core_job_def_read_tlv(bytes, len, out_def) != 0) {
        dsu__free(bytes);
        return DSU_STATUS_PARSE_ERROR;
    }
    dsu__free(bytes);
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu_job_input_write_tlv(const dsu_job_paths_t *paths, const dsu_job_input_t *in) {
    dsu_blob_t blob;
    dsu_status_t st;
    dsu_u32 len;
    dsu__blob_init(&blob);

    len = 4u;
    st = dsu__blob_put_u32le(&blob, (dsu_u32)DSU_JOB_INPUT_TAG_SCHEMA);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    st = dsu__blob_put_u32le(&blob, len);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    st = dsu__blob_put_u32le(&blob, (dsu_u32)in->schema_version);
    if (st != DSU_STATUS_SUCCESS) goto fail;

    if (in->job_type != 0u) {
        st = dsu__blob_put_u32le(&blob, (dsu_u32)DSU_JOB_INPUT_TAG_JOB_TYPE);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_put_u32le(&blob, 4u);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_put_u32le(&blob, (dsu_u32)in->job_type);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }
    if (in->plan_path[0] != '\0') {
        dsu_u32 n = (dsu_u32)strlen(in->plan_path);
        st = dsu__blob_put_u32le(&blob, (dsu_u32)DSU_JOB_INPUT_TAG_PLAN_PATH);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_put_u32le(&blob, n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_append(&blob, in->plan_path, n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }
    if (in->state_path[0] != '\0') {
        dsu_u32 n = (dsu_u32)strlen(in->state_path);
        st = dsu__blob_put_u32le(&blob, (dsu_u32)DSU_JOB_INPUT_TAG_STATE_PATH);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_put_u32le(&blob, n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_append(&blob, in->state_path, n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }
    if (in->log_path[0] != '\0') {
        dsu_u32 n = (dsu_u32)strlen(in->log_path);
        st = dsu__blob_put_u32le(&blob, (dsu_u32)DSU_JOB_INPUT_TAG_LOG_PATH);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_put_u32le(&blob, n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_append(&blob, in->log_path, n);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }
    if (in->dry_run != 0u) {
        st = dsu__blob_put_u32le(&blob, (dsu_u32)DSU_JOB_INPUT_TAG_DRY_RUN);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_put_u32le(&blob, 4u);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_put_u32le(&blob, (dsu_u32)in->dry_run);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }
    if (in->flags != 0u) {
        st = dsu__blob_put_u32le(&blob, (dsu_u32)DSU_JOB_INPUT_TAG_FLAGS);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_put_u32le(&blob, 4u);
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu__blob_put_u32le(&blob, (dsu_u32)in->flags);
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }

    st = dsu_job_write_all_atomic(paths->input_path, blob.data, blob.size);
    dsu__blob_free(&blob);
    return st;

fail:
    dsu__blob_free(&blob);
    return DSU_STATUS_INTERNAL_ERROR;
}

static dsu_status_t dsu_job_input_read_tlv(dsu_ctx_t *ctx, const dsu_job_paths_t *paths, dsu_job_input_t *out_in) {
    dsu_u8 *bytes = NULL;
    dsu_u32 len = 0u;
    dsu_u32 off = 0u;
    dsu_status_t st;
    dsu_job_input_t in;

    if (!ctx || !paths || !out_in) return DSU_STATUS_INVALID_ARGS;
    dsu_job_input_init(&in);

    st = dsu__fs_read_all(&ctx->config, paths->input_path, &bytes, &len);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(bytes);
        return st;
    }
    if (!bytes || len == 0u) {
        dsu__free(bytes);
        return DSU_STATUS_PARSE_ERROR;
    }

    while (off + 8u <= len) {
        dsu_u32 tag = 0u;
        dsu_u32 plen = 0u;
        dsu_u32 payload_off = 0u;
        st = dsu__read_u32le(bytes, len, &off, &tag);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u32le(bytes, len, &off, &plen);
        if (st != DSU_STATUS_SUCCESS) break;
        if (plen > (len - off)) {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
        payload_off = off;
        switch (tag) {
        case DSU_JOB_INPUT_TAG_SCHEMA:
            if (plen == 4u) {
                dsu_u32 v = 0u;
                (void)dsu__read_u32le(bytes, len, &payload_off, &v);
                in.schema_version = v;
            }
            break;
        case DSU_JOB_INPUT_TAG_JOB_TYPE:
            if (plen == 4u) {
                dsu_u32 v = 0u;
                (void)dsu__read_u32le(bytes, len, &payload_off, &v);
                in.job_type = v;
            }
            break;
        case DSU_JOB_INPUT_TAG_PLAN_PATH:
            if (plen > 0u) {
                dsu_u32 copy = plen;
                if (copy + 1u > (dsu_u32)sizeof(in.plan_path)) {
                    copy = (dsu_u32)sizeof(in.plan_path) - 1u;
                }
                memcpy(in.plan_path, bytes + off, copy);
                in.plan_path[copy] = '\0';
            }
            break;
        case DSU_JOB_INPUT_TAG_STATE_PATH:
            if (plen > 0u) {
                dsu_u32 copy = plen;
                if (copy + 1u > (dsu_u32)sizeof(in.state_path)) {
                    copy = (dsu_u32)sizeof(in.state_path) - 1u;
                }
                memcpy(in.state_path, bytes + off, copy);
                in.state_path[copy] = '\0';
            }
            break;
        case DSU_JOB_INPUT_TAG_LOG_PATH:
            if (plen > 0u) {
                dsu_u32 copy = plen;
                if (copy + 1u > (dsu_u32)sizeof(in.log_path)) {
                    copy = (dsu_u32)sizeof(in.log_path) - 1u;
                }
                memcpy(in.log_path, bytes + off, copy);
                in.log_path[copy] = '\0';
            }
            break;
        case DSU_JOB_INPUT_TAG_DRY_RUN:
            if (plen == 4u) {
                dsu_u32 v = 0u;
                (void)dsu__read_u32le(bytes, len, &payload_off, &v);
                in.dry_run = v;
            }
            break;
        case DSU_JOB_INPUT_TAG_FLAGS:
            if (plen == 4u) {
                dsu_u32 v = 0u;
                (void)dsu__read_u32le(bytes, len, &payload_off, &v);
                in.flags = v;
            }
            break;
        default:
            break;
        }
        off += plen;
    }

    dsu__free(bytes);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (in.schema_version == 0u) {
        in.schema_version = DSU_JOB_INPUT_TLV_VERSION;
    }
    if (in.schema_version > DSU_JOB_INPUT_TLV_VERSION) {
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }
    *out_in = in;
    return DSU_STATUS_SUCCESS;
}

static void dsu_job_add_err_fields(core_log_event *ev, const err_t *err) {
    if (!ev || !err) return;
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_DOMAIN, (u32)err->domain);
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_CODE, (u32)err->code);
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_FLAGS, (u32)err->flags);
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_MSG_ID, (u32)err->msg_id);
}

static dom_abi_result dsu_job_file_sink_write(void *user, const void *data, u32 len) {
    FILE *f = (FILE *)user;
    if (!f || !data || len == 0u) {
        return 0;
    }
    if (fwrite(data, 1u, (size_t)len, f) != (size_t)len) {
        return (dom_abi_result)-1;
    }
    return 0;
}

static void dsu_job_emit_event(dsu_job_ctx_t *ctx,
                               dsu_u32 event_code,
                               dsu_u32 step_id,
                               const err_t *err,
                               dsu_u32 outcome) {
    core_log_event ev;
    FILE *f;
    core_log_write_sink sink;

    if (!ctx) return;
    core_log_event_clear(&ev);
    ev.domain = CORE_LOG_DOMAIN_SETUP;
    ev.code = (u16)event_code;
    if (event_code == CORE_LOG_EVT_OP_FAIL) {
        ev.severity = CORE_LOG_SEV_ERROR;
    } else if (event_code == CORE_LOG_EVT_OP_REFUSED) {
        ev.severity = CORE_LOG_SEV_WARN;
    } else {
        ev.severity = CORE_LOG_SEV_INFO;
    }
    ev.msg_id = err ? err->msg_id : 0u;
    ev.t_mono = 0u;
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_OPERATION_ID, CORE_LOG_OP_SETUP_JOB);
    (void)core_log_event_add_u64(&ev, CORE_LOG_KEY_JOB_ID, ctx->state.job_id);
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_JOB_TYPE, ctx->state.job_type);
    if (step_id != 0u) {
        (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_JOB_STEP_ID, step_id);
    }
    if (outcome != 0u) {
        (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_JOB_OUTCOME, outcome);
    }
    if (err && !err_is_ok(err)) {
        dsu_job_add_err_fields(&ev, err);
    }

    f = fopen(ctx->paths.events_path, "ab");
    if (!f) {
        return;
    }
    sink.user = f;
    sink.write = dsu_job_file_sink_write;
    (void)core_log_event_write_tlv(&ev, &sink);
    fclose(f);
}

static err_t dsu_job_err_from_status(dsu_status_t st, dsu_u32 job_type, dsu_u32 step_id) {
    err_t err = err_ok();
    if (st == DSU_STATUS_SUCCESS) {
        return err;
    }
    switch (st) {
    case DSU_STATUS_INVALID_ARGS:
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
        break;
    case DSU_STATUS_IO_ERROR:
        err = err_make((u16)ERRD_FS, (u16)ERRC_FS_READ_FAILED, (u32)ERRF_TRANSIENT, (u32)ERRMSG_FS_READ_FAILED);
        break;
    case DSU_STATUS_PARSE_ERROR:
        err = err_make((u16)ERRD_TLV, (u16)ERRC_TLV_PARSE_FAILED, (u32)ERRF_INTEGRITY, (u32)ERRMSG_TLV_PARSE_FAILED);
        break;
    case DSU_STATUS_UNSUPPORTED_VERSION:
        err = err_make((u16)ERRD_TLV, (u16)ERRC_TLV_SCHEMA_VERSION, (u32)ERRF_NOT_SUPPORTED, (u32)ERRMSG_TLV_SCHEMA_VERSION);
        break;
    case DSU_STATUS_INTEGRITY_ERROR:
        err = err_make((u16)ERRD_TLV, (u16)ERRC_TLV_INTEGRITY, (u32)ERRF_INTEGRITY, (u32)ERRMSG_TLV_INTEGRITY);
        break;
    case DSU_STATUS_MISSING_COMPONENT:
    case DSU_STATUS_UNSATISFIED_DEPENDENCY:
    case DSU_STATUS_VERSION_CONFLICT:
    case DSU_STATUS_EXPLICIT_CONFLICT:
        err = err_make((u16)ERRD_SETUP, (u16)ERRC_SETUP_DEPENDENCY_CONFLICT, (u32)ERRF_USER_ACTIONABLE,
                       (u32)ERRMSG_SETUP_DEPENDENCY_CONFLICT);
        break;
    case DSU_STATUS_PLATFORM_INCOMPATIBLE:
        err = err_refuse((u16)ERRD_SETUP, (u16)ERRC_SETUP_UNSUPPORTED_PLATFORM, (u32)ERRMSG_SETUP_UNSUPPORTED_PLATFORM);
        err.flags |= (u32)ERRF_NOT_SUPPORTED;
        break;
    case DSU_STATUS_ILLEGAL_DOWNGRADE:
        err = err_refuse((u16)ERRD_SETUP, (u16)ERRC_SETUP_PLAN_FAILED, (u32)ERRMSG_SETUP_PLAN_FAILED);
        break;
    default:
        if (job_type == (u32)CORE_JOB_TYPE_SETUP_UNINSTALL) {
            err = err_make((u16)ERRD_SETUP, (u16)ERRC_SETUP_UNINSTALL_FAILED, 0u, (u32)ERRMSG_SETUP_UNINSTALL_FAILED);
        } else if (job_type == (u32)CORE_JOB_TYPE_SETUP_REPAIR) {
            err = err_make((u16)ERRD_SETUP, (u16)ERRC_SETUP_REPAIR_FAILED, 0u, (u32)ERRMSG_SETUP_REPAIR_FAILED);
        } else if (job_type == (u32)CORE_JOB_TYPE_SETUP_VERIFY) {
            err = err_make((u16)ERRD_SETUP, (u16)ERRC_SETUP_VERIFY_FAILED, 0u, (u32)ERRMSG_SETUP_VERIFY_FAILED);
        } else {
            err = err_make((u16)ERRD_SETUP, (u16)ERRC_SETUP_APPLY_FAILED, 0u, (u32)ERRMSG_SETUP_APPLY_FAILED);
        }
        break;
    }
    (void)err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_STATUS_CODE, (u32)st);
    (void)err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_OPERATION, (u32)job_type);
    (void)err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_STAGE, (u32)step_id);
    err_sort_details_by_key(&err);
    return err;
}

static dsu_status_t dsu_job_execute_step(dsu_job_ctx_t *ctx, dsu_u32 step_id, err_t *out_err) {
    dsu_status_t st = DSU_STATUS_INTERNAL_ERROR;
    if (!ctx) return DSU_STATUS_INVALID_ARGS;
    if (out_err) *out_err = err_ok();

    if (dsu_job_is_plan_job(ctx->state.job_type)) {
        if (step_id == 1u) {
            dsu_plan_t *plan = NULL;
            st = dsu_plan_read_file(ctx->ctx, ctx->input.plan_path, &plan);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu_plan_validate(plan);
            }
            if (plan) dsu_plan_destroy(ctx->ctx, plan);
        } else if (step_id == 2u) {
            dsu_plan_t *plan = NULL;
            dsu_txn_options_t txn_opts;
            dsu_txn_options_init(&txn_opts);
            txn_opts.dry_run = (dsu_bool)(ctx->input.dry_run ? 1 : 0);
            if (ctx->opts.fail_after_entries != 0u) {
                txn_opts.fail_after_entries = ctx->opts.fail_after_entries;
            }
            dsu_txn_result_init(&ctx->txn_result);
            st = dsu_plan_read_file(ctx->ctx, ctx->input.plan_path, &plan);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu_txn_apply_plan(ctx->ctx, plan, &txn_opts, &ctx->txn_result);
            }
            if (plan) dsu_plan_destroy(ctx->ctx, plan);
        }
    } else if (ctx->state.job_type == (u32)CORE_JOB_TYPE_SETUP_UNINSTALL) {
        if (step_id == 1u) {
            dsu_state_t *state = NULL;
            st = dsu_state_load_file(ctx->ctx, ctx->input.state_path, &state);
            if (state) dsu_state_destroy(ctx->ctx, state);
        } else if (step_id == 2u) {
            dsu_state_t *state = NULL;
            dsu_txn_options_t txn_opts;
            dsu_txn_options_init(&txn_opts);
            txn_opts.dry_run = (dsu_bool)(ctx->input.dry_run ? 1 : 0);
            if (ctx->opts.fail_after_entries != 0u) {
                txn_opts.fail_after_entries = ctx->opts.fail_after_entries;
            }
            dsu_txn_result_init(&ctx->txn_result);
            st = dsu_state_load_file(ctx->ctx, ctx->input.state_path, &state);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu_txn_uninstall_state(ctx->ctx, state, ctx->input.state_path, &txn_opts, &ctx->txn_result);
            }
            if (state) dsu_state_destroy(ctx->ctx, state);
        }
    } else if (ctx->state.job_type == (u32)CORE_JOB_TYPE_SETUP_VERIFY) {
        if (step_id == 1u) {
            dsu_state_t *state = NULL;
            st = dsu_state_load_file(ctx->ctx, ctx->input.state_path, &state);
            if (state) dsu_state_destroy(ctx->ctx, state);
        } else if (step_id == 2u) {
            dsu_state_t *state = NULL;
            dsu_txn_options_t txn_opts;
            dsu_txn_options_init(&txn_opts);
            dsu_txn_result_init(&ctx->txn_result);
            st = dsu_state_load_file(ctx->ctx, ctx->input.state_path, &state);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu_txn_verify_state(ctx->ctx, state, &txn_opts, &ctx->txn_result);
            }
            if (state) dsu_state_destroy(ctx->ctx, state);
        }
    } else {
        st = DSU_STATUS_INVALID_ARGS;
    }

    if (out_err) {
        *out_err = dsu_job_err_from_status(st, ctx->state.job_type, step_id);
    }
    return st;
}

static dsu_status_t dsu_job_run_steps(dsu_job_ctx_t *ctx, err_t *out_err) {
    core_job_def *def;
    core_job_state *st;
    dsu_status_t exec_st = DSU_STATUS_SUCCESS;
    u32 step_index = 0u;

    if (!ctx) return DSU_STATUS_INVALID_ARGS;
    def = &ctx->def;
    st = &ctx->state;

    if (out_err) *out_err = err_ok();

    if (!core_job_def_validate(def)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        }
        return DSU_STATUS_INTERNAL_ERROR;
    }

    dsu_job_emit_event(ctx, CORE_LOG_EVT_OP_BEGIN, 0u, (const err_t *)0, 0u);

    if (st->outcome != (u32)CORE_JOB_OUTCOME_NONE) {
        if (out_err) *out_err = st->last_error;
        return err_is_ok(&st->last_error) ? DSU_STATUS_SUCCESS : DSU_STATUS_INTERNAL_ERROR;
    }

    while (!core_job_state_all_steps_complete(def, st)) {
        u32 step_id = 0u;
        err_t step_err = err_ok();

        if (st->current_step != 0u) {
            u32 idx = 0u;
            if (core_job_def_find_step_index(def, st->current_step, &idx) &&
                !core_job_state_step_complete(st, idx)) {
                step_index = idx;
                step_id = def->steps[idx].step_id;
            } else {
                st->current_step = 0u;
            }
        }
        if (step_id == 0u) {
            if (!core_job_next_step_index(def, st, &step_index)) {
                break;
            }
            step_id = def->steps[step_index].step_id;
        }

        st->current_step = step_id;
        (void)dsu_job_write_state(&ctx->paths, st);
        dsu_job_emit_event(ctx, CORE_LOG_EVT_STATE, step_id, (const err_t *)0, 0u);

        if (ctx->opts.stop_after_step != 0u && ctx->opts.stop_after_step == step_id) {
            if (out_err) {
                *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
            }
            return DSU_STATUS_INTERNAL_ERROR;
        }

        exec_st = dsu_job_execute_step(ctx, step_id, &step_err);
        if (exec_st != DSU_STATUS_SUCCESS) {
            st->last_error = step_err;
            st->retry_count[step_index] += 1u;
            st->outcome = (step_err.flags & (u32)ERRF_POLICY_REFUSAL) ? (u32)CORE_JOB_OUTCOME_REFUSED : (u32)CORE_JOB_OUTCOME_FAILED;
            (void)dsu_job_write_state(&ctx->paths, st);
            dsu_job_emit_event(ctx,
                               (st->outcome == (u32)CORE_JOB_OUTCOME_REFUSED) ? CORE_LOG_EVT_OP_REFUSED : CORE_LOG_EVT_OP_FAIL,
                               step_id,
                               &step_err,
                               st->outcome);
            if (out_err) *out_err = step_err;
            return exec_st;
        }

        core_job_state_mark_step_complete(st, step_index);
        st->current_step = 0u;
        (void)dsu_job_write_state(&ctx->paths, st);
        dsu_job_emit_event(ctx, CORE_LOG_EVT_OP_OK, step_id, (const err_t *)0, 0u);
    }

    if (core_job_state_all_steps_complete(def, st)) {
        st->outcome = (u32)CORE_JOB_OUTCOME_OK;
        st->last_error = err_ok();
        (void)dsu_job_write_state(&ctx->paths, st);
        dsu_job_emit_event(ctx, CORE_LOG_EVT_OP_OK, 0u, (const err_t *)0, st->outcome);
        if (out_err) *out_err = err_ok();
        return DSU_STATUS_SUCCESS;
    }

    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
    }
    return DSU_STATUS_INTERNAL_ERROR;
}

static dsu_status_t dsu_job_extract_install_root(dsu_ctx_t *ctx,
                                                const dsu_job_input_t *in,
                                                char *out_root,
                                                dsu_u32 out_root_cap) {
    if (!ctx || !in || !out_root || out_root_cap == 0u) return DSU_STATUS_INVALID_ARGS;
    out_root[0] = '\0';
    if (dsu_job_is_plan_job(in->job_type)) {
        dsu_plan_t *plan = NULL;
        dsu_status_t st = dsu_plan_read_file(ctx, in->plan_path, &plan);
        if (st != DSU_STATUS_SUCCESS || !plan) {
            if (plan) dsu_plan_destroy(ctx, plan);
            return st;
        }
        dsu_job_normalize_path(dsu_plan_install_root(plan), out_root, out_root_cap);
        dsu_plan_destroy(ctx, plan);
        return (out_root[0] != '\0') ? DSU_STATUS_SUCCESS : DSU_STATUS_INVALID_ARGS;
    }
    if (dsu_job_is_state_job(in->job_type)) {
        dsu_state_t *state = NULL;
        dsu_status_t st = dsu_state_load_file(ctx, in->state_path, &state);
        if (st != DSU_STATUS_SUCCESS || !state) {
            if (state) dsu_state_destroy(ctx, state);
            return st;
        }
        dsu_job_normalize_path(dsu_state_primary_install_root(state), out_root, out_root_cap);
        dsu_state_destroy(ctx, state);
        return (out_root[0] != '\0') ? DSU_STATUS_SUCCESS : DSU_STATUS_INVALID_ARGS;
    }
    return DSU_STATUS_INVALID_ARGS;
}

static dsu_status_t dsu_job_prepare_new(dsu_job_ctx_t *ctx,
                                       dsu_ctx_t *dsu_ctx,
                                       const dsu_job_input_t *input,
                                       const char *job_root_override,
                                       const dsu_job_options_t *opts,
                                       err_t *out_err) {
    dsu_status_t st;
    char install_root[DSU_JOB_PATH_MAX];
    char job_root[DSU_JOB_PATH_MAX];
    u64 job_id;

    if (!ctx || !dsu_ctx || !input) return DSU_STATUS_INVALID_ARGS;
    memset(ctx, 0, sizeof(*ctx));
    ctx->ctx = dsu_ctx;
    ctx->input = *input;
    if (opts) {
        ctx->opts = *opts;
    } else {
        dsu_job_options_init(&ctx->opts);
    }
    dsu_job_build_def(input->job_type, &ctx->def);

    install_root[0] = '\0';
    job_root[0] = '\0';
    if (job_root_override && job_root_override[0] != '\0') {
        dsu_job_normalize_path(job_root_override, job_root, (dsu_u32)sizeof(job_root));
    } else {
        st = dsu_job_extract_install_root(dsu_ctx, input, install_root, (dsu_u32)sizeof(install_root));
        if (st != DSU_STATUS_SUCCESS) {
            if (out_err) *out_err = dsu_job_err_from_status(st, input->job_type, 0u);
            return st;
        }
        st = dsu_job_build_root_for_install_root(install_root, job_root, (dsu_u32)sizeof(job_root));
        if (st != DSU_STATUS_SUCCESS) {
            if (out_err) *out_err = dsu_job_err_from_status(st, input->job_type, 0u);
            return st;
        }
    }

    job_id = dsu_job_generate_id();
    dsu_job_build_paths(job_root, job_id, &ctx->paths);

    st = dsu_job_mkdirs_abs(ctx->paths.job_root);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_job_mkdirs_abs(ctx->paths.job_dir);
    if (st != DSU_STATUS_SUCCESS) return st;

    core_job_state_init(&ctx->state, job_id, ctx->def.job_type, ctx->def.step_count);

    st = dsu_job_write_def(&ctx->paths, &ctx->def);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_job_write_state(&ctx->paths, &ctx->state);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_job_input_write_tlv(&ctx->paths, &ctx->input);
    if (st != DSU_STATUS_SUCCESS) return st;

    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu_job_prepare_resume(dsu_job_ctx_t *ctx,
                                          dsu_ctx_t *dsu_ctx,
                                          const char *job_root,
                                          dsu_u64 job_id,
                                          err_t *out_err) {
    dsu_status_t st;
    if (!ctx || !dsu_ctx || !job_root || job_root[0] == '\0') return DSU_STATUS_INVALID_ARGS;
    memset(ctx, 0, sizeof(*ctx));
    ctx->ctx = dsu_ctx;
    dsu_job_build_paths(job_root, job_id, &ctx->paths);

    st = dsu_job_read_def(dsu_ctx, &ctx->paths, &ctx->def);
    if (st != DSU_STATUS_SUCCESS) {
        if (out_err) *out_err = dsu_job_err_from_status(st, 0u, 0u);
        return st;
    }
    st = dsu_job_read_state(dsu_ctx, &ctx->paths, &ctx->state);
    if (st != DSU_STATUS_SUCCESS) {
        if (out_err) *out_err = dsu_job_err_from_status(st, ctx->def.job_type, 0u);
        return st;
    }
    st = dsu_job_input_read_tlv(dsu_ctx, &ctx->paths, &ctx->input);
    if (st != DSU_STATUS_SUCCESS) {
        if (out_err) *out_err = dsu_job_err_from_status(st, ctx->def.job_type, 0u);
        return st;
    }
    dsu_job_options_init(&ctx->opts);
    return DSU_STATUS_SUCCESS;
}

void dsu_job_input_init(dsu_job_input_t *in) {
    if (!in) return;
    memset(in, 0, sizeof(*in));
    in->schema_version = DSU_JOB_INPUT_TLV_VERSION;
}

void dsu_job_options_init(dsu_job_options_t *opts) {
    if (!opts) return;
    memset(opts, 0, sizeof(*opts));
    opts->struct_size = (dsu_u32)sizeof(*opts);
    opts->struct_version = DSU_JOB_OPTIONS_VERSION;
}

dsu_status_t dsu_job_build_root_for_install_root(const char *install_root,
                                                char *out_root,
                                                dsu_u32 out_root_cap) {
    char norm_root[DSU_JOB_PATH_MAX];
    if (!install_root || !out_root || out_root_cap == 0u) return DSU_STATUS_INVALID_ARGS;
    dsu_job_normalize_path(install_root, norm_root, (dsu_u32)sizeof(norm_root));
    return dsu_job_path_join(norm_root, ".dsu_txn/jobs", out_root, out_root_cap);
}

dsu_status_t dsu_job_run(dsu_ctx_t *ctx,
                        const dsu_job_input_t *input,
                        const char *job_root_override,
                        const dsu_job_options_t *opts,
                        dsu_job_run_result_t *out_result) {
    dsu_job_ctx_t job;
    err_t err;
    dsu_status_t st;

    if (!ctx || !input || !out_result) return DSU_STATUS_INVALID_ARGS;
    err = err_ok();

    st = dsu_job_prepare_new(&job, ctx, input, job_root_override, opts, &err);
    if (st != DSU_STATUS_SUCCESS) {
        out_result->state = job.state;
        out_result->err = err;
        dsu_txn_result_init(&out_result->txn_result);
        return st;
    }

    st = dsu_job_run_steps(&job, &err);
    out_result->state = job.state;
    out_result->err = err;
    out_result->txn_result = job.txn_result;
    return st;
}

dsu_status_t dsu_job_resume(dsu_ctx_t *ctx,
                           const char *job_root_override,
                           dsu_u64 job_id,
                           dsu_job_run_result_t *out_result) {
    dsu_job_ctx_t job;
    err_t err;
    dsu_status_t st;

    if (!ctx || !job_root_override || !out_result) return DSU_STATUS_INVALID_ARGS;
    err = err_ok();

    st = dsu_job_prepare_resume(&job, ctx, job_root_override, job_id, &err);
    if (st != DSU_STATUS_SUCCESS) {
        out_result->state = job.state;
        out_result->err = err;
        dsu_txn_result_init(&out_result->txn_result);
        return st;
    }

    st = dsu_job_run_steps(&job, &err);
    out_result->state = job.state;
    out_result->err = err;
    out_result->txn_result = job.txn_result;
    return st;
}

dsu_status_t dsu_job_state_load(dsu_ctx_t *ctx,
                               const char *job_root_override,
                               dsu_u64 job_id,
                               core_job_state *out_state) {
    dsu_job_paths_t paths;
    dsu_status_t st;
    if (!ctx || !job_root_override || !out_state) return DSU_STATUS_INVALID_ARGS;
    dsu_job_build_paths(job_root_override, job_id, &paths);
    st = dsu_job_read_state(ctx, &paths, out_state);
    return st;
}
