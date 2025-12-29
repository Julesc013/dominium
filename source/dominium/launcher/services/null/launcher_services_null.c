/*
FILE: source/dominium/launcher/services/null/launcher_services_null.c
MODULE: Dominium Launcher
PURPOSE: Null services backend for kernel-only smoke tests (filesystem + time + hashing).
*/
#include "launcher_core_api.h"

#include <stdio.h>
#include <string.h>

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

static launcher_services_caps launcher_null_get_caps(void) {
    return LAUNCHER_SERVICES_CAP_FILESYSTEM |
           LAUNCHER_SERVICES_CAP_TIME |
           LAUNCHER_SERVICES_CAP_HASHING;
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
