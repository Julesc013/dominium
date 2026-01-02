#ifndef DSS_ARCHIVE_H
#define DSS_ARCHIVE_H

#include "dss_error.h"

#ifdef __cplusplus

struct dss_archive_api_t {
    void *ctx;
    dss_error_t (*extract_deterministic)(void *ctx,
                                         const char *archive_path,
                                         const char *dest_dir);
    dss_error_t (*validate_archive_table)(void *ctx,
                                          const char *archive_path);
};

#endif /* __cplusplus */

#endif /* DSS_ARCHIVE_H */
