#ifndef DSS_FS_H
#define DSS_FS_H

#include "dss_error.h"

#ifdef __cplusplus
#include <string>
#include <vector>

struct dss_fs_api_t {
    void *ctx;
    dss_error_t (*read_file_bytes)(void *ctx,
                                   const char *path,
                                   std::vector<dss_u8> *out_bytes);
    dss_error_t (*write_file_bytes_atomic)(void *ctx,
                                           const char *path,
                                           const dss_u8 *data,
                                           dss_u32 len);
    dss_error_t (*make_dir)(void *ctx, const char *path);
    dss_error_t (*remove_file)(void *ctx, const char *path);
    dss_error_t (*remove_dir_if_empty)(void *ctx, const char *path);
    dss_error_t (*list_dir)(void *ctx,
                            const char *path,
                            std::vector<std::string> *out_entries);
    dss_error_t (*canonicalize_path)(void *ctx,
                                     const char *path,
                                     std::string *out_path);
    dss_error_t (*join_path)(void *ctx,
                             const char *a,
                             const char *b,
                             std::string *out_path);
    dss_error_t (*temp_dir)(void *ctx, std::string *out_path);
    dss_error_t (*atomic_rename)(void *ctx, const char *src, const char *dst);
    dss_error_t (*dir_swap)(void *ctx, const char *src_dir, const char *dst_dir);
    dss_error_t (*exists)(void *ctx, const char *path, dss_bool *out_exists);
    dss_error_t (*file_size)(void *ctx, const char *path, dss_u64 *out_size);
};

#endif /* __cplusplus */

#endif /* DSS_FS_H */
