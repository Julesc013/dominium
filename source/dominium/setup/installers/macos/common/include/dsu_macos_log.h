#ifndef DSU_MACOS_LOG_H_INCLUDED
#define DSU_MACOS_LOG_H_INCLUDED

#include <stdarg.h>

#ifdef __cplusplus
extern "C" {
#endif

void dsu_macos_log_set_file(const char *path);
void dsu_macos_log_info(const char *fmt, ...);
void dsu_macos_log_error(const char *fmt, ...);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_MACOS_LOG_H_INCLUDED */
