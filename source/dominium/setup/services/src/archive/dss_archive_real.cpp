#include "dss/dss_archive.h"

extern "C" {
#include "dsu_util_internal.h"
}

#include <cstring>
#include <string>

#if defined(_WIN32)
#include <direct.h>
#include <errno.h>
#else
#include <errno.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

static dss_error_t dss_archive_from_dsu_status(dsu_status_t st) {
    switch (st) {
    case DSU_STATUS_SUCCESS:
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
    case DSU_STATUS_INVALID_ARGS:
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    case DSU_STATUS_IO_ERROR:
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    case DSU_STATUS_PARSE_ERROR:
    case DSU_STATUS_UNSUPPORTED_VERSION:
    case DSU_STATUS_INTEGRITY_ERROR:
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_ARCHIVE, DSS_SUBCODE_NONE, 0u);
    case DSU_STATUS_INTERNAL_ERROR:
    default:
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INTERNAL, DSS_SUBCODE_NONE, 0u);
    }
}

static int dss_archive_mkdir(const std::string &path) {
    if (path.empty()) {
        return 0;
    }
#if defined(_WIN32)
    if (_mkdir(path.c_str()) == 0) {
        return 0;
    }
#else
    if (mkdir(path.c_str(), 0755) == 0) {
        return 0;
    }
#endif
    return (errno == EEXIST) ? 0 : -1;
}

static dss_error_t dss_archive_ensure_parent_dirs(const std::string &path) {
    std::string norm = path;
    size_t i;
    size_t last_slash = std::string::npos;
    for (i = 0u; i < norm.size(); ++i) {
        if (norm[i] == '\\') {
            norm[i] = '/';
        }
        if (norm[i] == '/') {
            last_slash = i;
        }
    }
    if (last_slash == std::string::npos) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
    }
    {
        std::string dir = norm.substr(0u, last_slash);
        std::string prefix;
        size_t start = 0u;
        if (dir.size() >= 2u && ((dir[0] >= 'A' && dir[0] <= 'Z') || (dir[0] >= 'a' && dir[0] <= 'z'))
            && dir[1] == ':') {
            prefix = dir.substr(0u, 2u);
            start = 2u;
            if (start < dir.size() && dir[start] == '/') {
                ++start;
                prefix += "/";
            }
        } else if (dir.size() >= 2u && dir[0] == '/' && dir[1] == '/') {
            prefix = "//";
            start = 2u;
        } else if (!dir.empty() && dir[0] == '/') {
            prefix = "/";
            start = 1u;
        }
        {
            std::string accum = prefix;
            size_t seg_start = start;
            for (i = start; i <= dir.size(); ++i) {
                char c = (i < dir.size()) ? dir[i] : '/';
                if (c == '/') {
                    size_t len = i - seg_start;
                    if (len != 0u) {
                        if (!accum.empty() && accum[accum.size() - 1u] != '/') {
                            accum += "/";
                        }
                        accum.append(dir.substr(seg_start, len));
                        if (dss_archive_mkdir(accum) != 0) {
                            return dss_error_make(DSS_DOMAIN_SERVICES,
                                                  DSS_CODE_IO,
                                                  DSS_SUBCODE_NONE,
                                                  0u);
                        }
                    }
                    seg_start = i + 1u;
                }
            }
        }
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_archive_real_extract(void *ctx,
                                            const char *archive_path,
                                            const char *dest_dir) {
    dsu__archive_entry_t *entries = NULL;
    dsu_u32 count = 0u;
    dsu_u32 i;
    dsu_status_t st;
    (void)ctx;
    if (!archive_path || !dest_dir) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }

    st = dsu__archive_list(archive_path, &entries, &count);
    if (st != DSU_STATUS_SUCCESS) {
        return dss_archive_from_dsu_status(st);
    }

    for (i = 0u; i < count; ++i) {
        std::string out_path = std::string(dest_dir) + "/" + entries[i].path;
        dss_error_t mk = dss_archive_ensure_parent_dirs(out_path);
        if (!dss_error_is_ok(mk)) {
            dsu__archive_free_entries(entries, count);
            return mk;
        }
        st = dsu__archive_extract_file(archive_path, entries[i].path, out_path.c_str());
        if (st != DSU_STATUS_SUCCESS) {
            dsu__archive_free_entries(entries, count);
            return dss_archive_from_dsu_status(st);
        }
    }

    dsu__archive_free_entries(entries, count);
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_archive_real_validate(void *ctx, const char *archive_path) {
    dsu__archive_entry_t *entries = NULL;
    dsu_u32 count = 0u;
    dsu_status_t st;
    (void)ctx;
    if (!archive_path) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    st = dsu__archive_list(archive_path, &entries, &count);
    if (st != DSU_STATUS_SUCCESS) {
        return dss_archive_from_dsu_status(st);
    }
    dsu__archive_free_entries(entries, count);
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

void dss_archive_init_real(dss_archive_api_t *api) {
    dss_u32 *kind;
    if (!api) {
        return;
    }
    kind = new dss_u32(1u);
    api->ctx = kind;
    api->extract_deterministic = dss_archive_real_extract;
    api->validate_archive_table = dss_archive_real_validate;
}
