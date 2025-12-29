#ifndef DSS_FS_INTERNAL_H
#define DSS_FS_INTERNAL_H

#include "dss/dss_fs.h"

#ifdef __cplusplus
#include <string>

struct dss_fs_context_t {
    dss_u32 kind;
    std::string root;
    std::string temp_root;
};

dss_error_t dss_fs_canonicalize_path(const char *path,
                                     dss_bool reject_parent,
                                     std::string *out_path);
dss_error_t dss_fs_join_path(const char *a,
                             const char *b,
                             std::string *out_path);
dss_bool dss_fs_is_abs_path(const std::string &path);
dss_bool dss_fs_path_has_prefix(const std::string &path,
                                const std::string &root);

/* Native file ops used by real and fake backends. */
dss_error_t dss_fs_real_read_file_bytes(void *ctx,
                                        const char *path,
                                        std::vector<dss_u8> *out_bytes);
dss_error_t dss_fs_real_write_file_bytes_atomic(void *ctx,
                                                const char *path,
                                                const dss_u8 *data,
                                                dss_u32 len);
dss_error_t dss_fs_real_exists(void *ctx, const char *path, dss_bool *out_exists);
dss_error_t dss_fs_real_file_size(void *ctx, const char *path, dss_u64 *out_size);

#endif /* __cplusplus */

#endif /* DSS_FS_INTERNAL_H */
