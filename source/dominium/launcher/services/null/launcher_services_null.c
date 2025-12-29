/*
FILE: source/dominium/launcher/services/null/launcher_services_null.c
MODULE: Dominium Launcher
PURPOSE: Null services backend for kernel-only smoke tests (filesystem + time + hashing).
*/
#include "launcher_core_api.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static bool launcher_null_fs_get_path(launcher_fs_path_kind kind, char *buf, size_t buf_size) {
    const char *path = ".";
    size_t len;
    if (!buf || buf_size == 0u) {
        return false;
    }
    if (kind == LAUNCHER_FS_PATH_STATE) {
        path = "state";
    } else if (kind == LAUNCHER_FS_PATH_AUDIT) {
        path = "audit";
    }
    len = strlen(path);
    if (len + 1u > buf_size) {
        return false;
    }
    memcpy(buf, path, len + 1u);
    return true;
}

static void *launcher_null_file_open(const char *path, const char *mode) {
    return (void *)fopen(path, mode);
}

static size_t launcher_null_file_read(void *fh, void *buf, size_t size) {
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    return fread(buf, 1u, size, (FILE *)fh);
}

static size_t launcher_null_file_write(void *fh, const void *buf, size_t size) {
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    return fwrite(buf, 1u, size, (FILE *)fh);
}

static int launcher_null_file_seek(void *fh, long offset, int origin) {
    if (!fh) {
        return -1;
    }
    return fseek((FILE *)fh, offset, origin);
}

static long launcher_null_file_tell(void *fh) {
    if (!fh) {
        return -1L;
    }
    return ftell((FILE *)fh);
}

static int launcher_null_file_close(void *fh) {
    if (!fh) {
        return -1;
    }
    return fclose((FILE *)fh);
}

static u64 launcher_null_time_now_us(void) {
    static u64 now_us = 1000000ull;
    return now_us++;
}

static u64 launcher_null_hash_fnv1a64(const void *data, u32 len) {
    const unsigned char *p = (const unsigned char *)data;
    u64 h = (u64)0xcbf29ce484222325ULL;
    u32 i;
    if (!p || len == 0u) {
        return h;
    }
    for (i = 0u; i < len; ++i) {
        h ^= (u64)p[i];
        h *= (u64)0x100000001b3ULL;
    }
    return h;
}

#if defined(_WIN32) || defined(_WIN64)
extern int _mkdir(const char* path);
#else
extern int mkdir(const char* path, unsigned int mode);
#endif

#define LAUNCHER_LOG_MAX_RUN_BYTES     (256u * 1024u)
#define LAUNCHER_LOG_MAX_ROLLING_BYTES (128u * 1024u)

static void launcher_log_hex16(u64 v, char out_hex[17]) {
    static const char* hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & 0xFu);
        out_hex[i] = hex[nib & 0xFu];
    }
    out_hex[16] = '\0';
}

static void launcher_log_mkdir_one(const char* path) {
    if (!path || !path[0]) {
        return;
    }
#if defined(_WIN32) || defined(_WIN64)
    (void)_mkdir(path);
#else
    (void)mkdir(path, 0777u);
#endif
}

static void launcher_log_mkdir_p(const char* path) {
    char buf[512];
    size_t i;
    size_t len;
    if (!path || !path[0]) {
        return;
    }
    len = strlen(path);
    if (len >= sizeof(buf)) {
        return;
    }
    memcpy(buf, path, len + 1u);
    for (i = 0u; i < len; ++i) {
        if (buf[i] == '/' || buf[i] == '\\') {
            char saved = buf[i];
            buf[i] = '\0';
            launcher_log_mkdir_one(buf);
            buf[i] = saved;
        }
    }
    launcher_log_mkdir_one(buf);
}

static void launcher_log_dirname(const char* path, char* out, size_t cap) {
    size_t len;
    size_t i;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!path) {
        return;
    }
    len = strlen(path);
    if (len + 1u > cap) {
        return;
    }
    memcpy(out, path, len + 1u);
    for (i = len; i > 0u; --i) {
        if (out[i - 1u] == '/' || out[i - 1u] == '\\') {
            out[i - 1u] = '\0';
            return;
        }
    }
    out[0] = '\0';
}

static int launcher_log_get_state_root(char* out_root, size_t cap, const core_log_scope* scope) {
    if (!out_root || cap == 0u) {
        return 0;
    }
    out_root[0] = '\0';
    if (scope && scope->state_root && scope->state_root[0]) {
        size_t len = strlen(scope->state_root);
        if (len + 1u > cap) {
            return 0;
        }
        memcpy(out_root, scope->state_root, len + 1u);
        return 1;
    }
    return launcher_null_fs_get_path(LAUNCHER_FS_PATH_STATE, out_root, cap) ? 1 : 0;
}

static int launcher_log_build_path(const core_log_scope* scope, char* out_path, size_t cap, u32* out_max_bytes) {
    char state_root[256];
    char run_hex[17];
    int ok;
    int n;

    if (!out_path || cap == 0u || !scope) {
        return 0;
    }

    ok = launcher_log_get_state_root(state_root, sizeof(state_root), scope);
    if (!ok) {
        return 0;
    }

    if (scope->kind == CORE_LOG_SCOPE_RUN) {
        if (!scope->instance_id || scope->run_id == 0u) {
            return 0;
        }
        launcher_log_hex16(scope->run_id, run_hex);
        n = snprintf(out_path, cap,
                     "%s/instances/%s/logs/runs/%s/events.tlv",
                     state_root, scope->instance_id, run_hex);
        if (out_max_bytes) {
            *out_max_bytes = LAUNCHER_LOG_MAX_RUN_BYTES;
        }
    } else if (scope->kind == CORE_LOG_SCOPE_INSTANCE) {
        if (!scope->instance_id) {
            return 0;
        }
        n = snprintf(out_path, cap,
                     "%s/instances/%s/logs/rolling/events_rolling.tlv",
                     state_root, scope->instance_id);
        if (out_max_bytes) {
            *out_max_bytes = LAUNCHER_LOG_MAX_ROLLING_BYTES;
        }
    } else {
        n = snprintf(out_path, cap,
                     "%s/logs/rolling/events_rolling.tlv",
                     state_root);
        if (out_max_bytes) {
            *out_max_bytes = LAUNCHER_LOG_MAX_ROLLING_BYTES;
        }
    }

    return (n > 0 && (size_t)n < cap) ? 1 : 0;
}

static dom_abi_result launcher_log_file_write(void* user, const void* data, u32 len) {
    FILE* f = (FILE*)user;
    size_t wrote;
    if (!f || !data || len == 0u) {
        return 0;
    }
    wrote = fwrite(data, 1u, (size_t)len, f);
    return (wrote == (size_t)len) ? 0 : (dom_abi_result)-1;
}

struct launcher_log_mem_sink {
    unsigned char* buf;
    u32 cap;
    u32 off;
};

static dom_abi_result launcher_log_mem_write(void* user, const void* data, u32 len) {
    struct launcher_log_mem_sink* s = (struct launcher_log_mem_sink*)user;
    if (!s || !data || len == 0u) {
        return 0;
    }
    if ((u64)s->off + (u64)len > (u64)s->cap) {
        return (dom_abi_result)-1;
    }
    memcpy(s->buf + s->off, data, len);
    s->off += len;
    return 0;
}

static int launcher_log_read_file(const char* path, unsigned char** out_data, u32* out_len) {
    FILE* f;
    long sz;
    size_t got;
    if (!out_data || !out_len) {
        return 0;
    }
    *out_data = NULL;
    *out_len = 0u;
    f = fopen(path, "rb");
    if (!f) {
        return 0;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    sz = ftell(f);
    if (sz <= 0) {
        fclose(f);
        return 0;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return 0;
    }
    *out_data = (unsigned char*)malloc((size_t)sz);
    if (!*out_data) {
        fclose(f);
        return 0;
    }
    got = fread(*out_data, 1u, (size_t)sz, f);
    fclose(f);
    if (got != (size_t)sz) {
        free(*out_data);
        *out_data = NULL;
        return 0;
    }
    *out_len = (u32)sz;
    return 1;
}

static int launcher_log_write_file(const char* path, const unsigned char* data, u32 len) {
    FILE* f;
    size_t wrote;
    f = fopen(path, "wb");
    if (!f) {
        return 0;
    }
    wrote = 0u;
    if (len > 0u && data) {
        wrote = fwrite(data, 1u, (size_t)len, f);
    }
    fclose(f);
    return wrote == (size_t)len;
}

static int launcher_log_append_event(const char* path, const core_log_event* ev, u32 max_bytes, int rolling) {
    FILE* f;
    u32 ev_size;
    char dir[512];

    ev_size = core_log_event_encoded_size(ev);
    if (ev_size == 0u) {
        return 0;
    }

    launcher_log_dirname(path, dir, sizeof(dir));
    if (dir[0]) {
        launcher_log_mkdir_p(dir);
    }

    if (!rolling) {
        long sz = 0;
        f = fopen(path, "ab");
        if (!f) {
            return 0;
        }
        if (max_bytes > 0u) {
            if (fseek(f, 0, SEEK_END) == 0) {
                sz = ftell(f);
            }
            if (sz >= 0 && ((u64)sz + (u64)ev_size) > (u64)max_bytes) {
                fclose(f);
                return 1;
            }
        }
        {
            core_log_write_sink sink;
            sink.user = f;
            sink.write = launcher_log_file_write;
            (void)core_log_event_write_tlv(ev, &sink);
        }
        fclose(f);
        return 1;
    }

    /* Rolling: keep newest events within bound. */
    {
        unsigned char* data = NULL;
        u32 data_len = 0u;
        u32 offsets[256];
        u32 lengths[256];
        u32 count = 0u;
        u32 off = 0u;
        u32 keep_from = 0u;
        u32 keep_bytes = 0u;
        u32 i;

        if (launcher_log_read_file(path, &data, &data_len)) {
            while (off + 8u <= data_len && count < 256u) {
                u32 used = 0u;
                core_log_event tmp;
                if (core_log_event_read_tlv(data + off, data_len - off, &tmp, &used) != 0) {
                    break;
                }
                if (used == 0u || off + used > data_len) {
                    break;
                }
                offsets[count] = off;
                lengths[count] = used;
                count += 1u;
                off += used;
            }
        }

        if (max_bytes > 0u) {
            if (ev_size > max_bytes) {
                if (data) {
                    free(data);
                }
                return 1;
            }
            keep_bytes = 0u;
            keep_from = count;
            for (i = count; i > 0u; --i) {
                u32 idx = i - 1u;
                if ((u64)keep_bytes + (u64)lengths[idx] + (u64)ev_size > (u64)max_bytes) {
                    break;
                }
                keep_bytes += lengths[idx];
                keep_from = idx;
            }
        }

        {
            u32 out_len = keep_bytes + ev_size;
            unsigned char* out_buf = (unsigned char*)malloc(out_len);
            u32 w = 0u;
            struct launcher_log_mem_sink mem;
            if (!out_buf) {
                if (data) free(data);
                return 0;
            }
            if (keep_bytes > 0u && data) {
                for (i = keep_from; i < count; ++i) {
                    memcpy(out_buf + w, data + offsets[i], lengths[i]);
                    w += lengths[i];
                }
            }
            mem.buf = out_buf + w;
            mem.cap = out_len - w;
            mem.off = 0u;
            {
                core_log_write_sink sink;
                sink.user = &mem;
                sink.write = launcher_log_mem_write;
                if (core_log_event_write_tlv(ev, &sink) != 0) {
                    free(out_buf);
                    if (data) free(data);
                    return 0;
                }
            }
            if (!launcher_log_write_file(path, out_buf, w + mem.off)) {
                /* ignore */
            }
            free(out_buf);
        }

        if (data) {
            free(data);
        }
    }

    return 1;
}

static dom_abi_result launcher_null_log_emit(void* user, const core_log_scope* scope, const core_log_event* ev) {
    char path[512];
    u32 max_bytes = 0u;
    int rolling = 0;
    (void)user;

    if (!scope || !ev) {
        return (dom_abi_result)-1;
    }

    if (!launcher_log_build_path(scope, path, sizeof(path), &max_bytes)) {
        return (dom_abi_result)-1;
    }

    rolling = (scope->kind != CORE_LOG_SCOPE_RUN) ? 1 : 0;
    if (!launcher_log_append_event(path, ev, max_bytes, rolling)) {
        return (dom_abi_result)-1;
    }
    return 0;
}

static launcher_fs_api_v1 launcher_null_fs_api = {
    DOM_ABI_HEADER_INIT(1u, launcher_fs_api_v1),
    launcher_null_fs_get_path,
    launcher_null_file_open,
    launcher_null_file_read,
    launcher_null_file_write,
    launcher_null_file_seek,
    launcher_null_file_tell,
    launcher_null_file_close
};

static launcher_time_api_v1 launcher_null_time_api = {
    DOM_ABI_HEADER_INIT(1u, launcher_time_api_v1),
    launcher_null_time_now_us
};

static launcher_hash_api_v1 launcher_null_hash_api = {
    DOM_ABI_HEADER_INIT(1u, launcher_hash_api_v1),
    launcher_null_hash_fnv1a64
};

static launcher_log_api_v1 launcher_null_log_api = {
    DOM_ABI_HEADER_INIT(CORE_LOG_SINK_ABI_VERSION, launcher_log_api_v1),
    0,
    launcher_null_log_emit
};

static launcher_services_caps launcher_null_get_caps(void) {
    return LAUNCHER_SERVICES_CAP_FILESYSTEM |
           LAUNCHER_SERVICES_CAP_TIME |
           LAUNCHER_SERVICES_CAP_HASHING |
           LAUNCHER_SERVICES_CAP_LOGGING;
}

static dom_abi_result launcher_null_query_interface(dom_iid iid, void **out_iface) {
    if (!out_iface) {
        return -1;
    }
    *out_iface = NULL;
    if (iid == LAUNCHER_IID_FS_V1) {
        *out_iface = (void *)&launcher_null_fs_api;
        return 0;
    }
    if (iid == LAUNCHER_IID_TIME_V1) {
        *out_iface = (void *)&launcher_null_time_api;
        return 0;
    }
    if (iid == LAUNCHER_IID_HASH_V1) {
        *out_iface = (void *)&launcher_null_hash_api;
        return 0;
    }
    if (iid == LAUNCHER_IID_LOG_V1) {
        *out_iface = (void *)&launcher_null_log_api;
        return 0;
    }
    return -1;
}

const launcher_services_api_v1 *launcher_services_null_v1(void) {
    static launcher_services_api_v1 s_services = {
        DOM_ABI_HEADER_INIT(1u, launcher_services_api_v1),
        launcher_null_get_caps,
        launcher_null_query_interface
    };
    return &s_services;
}
